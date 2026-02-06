from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.models.user_features import RFMFeatures
from app.database.mongodb import MongoDB, Collections
import pandas as pd
import numpy as np


class RFMFeatureExtractor:
    """Extract RFM (Recency, Frequency, Monetary) features for users"""
    
    def __init__(self):
        self.db = MongoDB.get_database()
    
    async def calculate_rfm_for_user(self, user_id: str) -> RFMFeatures:
        """Calculate RFM features for a specific user"""
        try:
            # Get user transactions
            transactions_collection = self.db[Collections.TRANSACTIONS]
            cursor = transactions_collection.find({"user_id": user_id})
            transactions = await cursor.to_list(length=None)
            
            if not transactions:
                return RFMFeatures(
                    recency=float('inf'),
                    frequency=0.0,
                    monetary=0.0
                )
            
            # Convert to DataFrame for easier analysis
            df = pd.DataFrame(transactions)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate Recency (days since last purchase)
            last_purchase_date = df['timestamp'].max()
            current_date = datetime.utcnow()
            recency = (current_date - last_purchase_date).days
            
            # Calculate Frequency (number of transactions in last 90 days)
            ninety_days_ago = current_date - timedelta(days=90)
            recent_transactions = df[df['timestamp'] >= ninety_days_ago]
            frequency = len(recent_transactions)
            
            # Calculate Monetary (total spent in last 90 days)
            monetary = recent_transactions['total_amount'].sum()
            
            return RFMFeatures(
                recency=float(recency),
                frequency=float(frequency),
                monetary=float(monetary)
            )
            
        except Exception as e:
            print(f"Error calculating RFM for user {user_id}: {e}")
            return RFMFeatures(
                recency=float('inf'),
                frequency=0.0,
                monetary=0.0
            )
    
    async def calculate_rfm_for_all_users(self) -> Dict[str, RFMFeatures]:
        """Calculate RFM features for all users"""
        try:
            users_collection = self.db[Collections.USERS]
            cursor = users_collection.find({})
            users = await cursor.to_list(length=None)
            
            rfm_features = {}
            for user in users:
                user_id = user['user_id']
                rfm_features[user_id] = await self.calculate_rfm_for_user(user_id)
            
            return rfm_features
            
        except Exception as e:
            print(f"Error calculating RFM for all users: {e}")
            return {}
    
    async def get_rfm_scores(self, user_id: str) -> Dict[str, int]:
        """Get RFM scores (1-5 scale) for a user"""
        try:
            rfm_features = await self.calculate_rfm_for_user(user_id)
            
            # Get all users' RFM for percentile calculation
            all_rfm = await self.calculate_rfm_for_all_users()
            
            # Calculate percentiles
            recency_values = [rfm.recency for rfm in all_rfm.values() if rfm.recency != float('inf')]
            frequency_values = [rfm.frequency for rfm in all_rfm.values()]
            monetary_values = [rfm.monetary for rfm in all_rfm.values()]
            
            # Calculate scores (1-5 scale, where 5 is best)
            recency_score = self._calculate_percentile_score(
                rfm_features.recency, recency_values, reverse=True
            )
            frequency_score = self._calculate_percentile_score(
                rfm_features.frequency, frequency_values
            )
            monetary_score = self._calculate_percentile_score(
                rfm_features.monetary, monetary_values
            )
            
            return {
                "recency_score": recency_score,
                "frequency_score": frequency_score,
                "monetary_score": monetary_score,
                "rfm_score": recency_score + frequency_score + monetary_score
            }
            
        except Exception as e:
            print(f"Error calculating RFM scores for user {user_id}: {e}")
            return {"recency_score": 1, "frequency_score": 1, "monetary_score": 1, "rfm_score": 3}
    
    def _calculate_percentile_score(self, value: float, values: List[float], reverse: bool = False) -> int:
        """Calculate percentile score (1-5 scale)"""
        if not values:
            return 1
        
        values_sorted = sorted(values)
        n = len(values_sorted)
        
        if reverse:  # For recency, lower is better
            rank = len([v for v in values_sorted if v <= value])
        else:  # For frequency and monetary, higher is better
            rank = len([v for v in values_sorted if v <= value])
        
        percentile = rank / n
        
        # Convert percentile to 1-5 score
        if percentile <= 0.2:
            return 1
        elif percentile <= 0.4:
            return 2
        elif percentile <= 0.6:
            return 3
        elif percentile <= 0.8:
            return 4
        else:
            return 5
    
    async def get_rfm_segments(self) -> Dict[str, List[str]]:
        """Get RFM-based segments"""
        try:
            users_collection = self.db[Collections.USERS]
            cursor = users_collection.find({})
            users = await cursor.to_list(length=None)
            
            segments = {
                "champions": [],      # High RFM scores
                "loyal_customers": [], # High frequency and monetary
                "potential_loyalists": [], # Recent customers with good frequency
                "new_customers": [],   # Recent customers with low frequency
                "at_risk": [],         # High frequency but haven't purchased recently
                "cannot_lose": [],     # High monetary but haven't purchased recently
                "hibernating": [],     # Low frequency and monetary, haven't purchased recently
                "lost": []            # Low RFM scores
            }
            
            for user in users:
                user_id = user['user_id']
                scores = await self.get_rfm_scores(user_id)
                
                r, f, m = scores['recency_score'], scores['frequency_score'], scores['monetary_score']
                
                if r >= 4 and f >= 4 and m >= 4:
                    segments["champions"].append(user_id)
                elif f >= 4 and m >= 4:
                    segments["loyal_customers"].append(user_id)
                elif r >= 4 and f >= 3:
                    segments["potential_loyalists"].append(user_id)
                elif r >= 4 and f <= 2:
                    segments["new_customers"].append(user_id)
                elif r <= 2 and f >= 4:
                    segments["at_risk"].append(user_id)
                elif r <= 2 and m >= 4:
                    segments["cannot_lose"].append(user_id)
                elif r <= 2 and f <= 2 and m <= 2:
                    segments["hibernating"].append(user_id)
                else:
                    segments["lost"].append(user_id)
            
            return segments
            
        except Exception as e:
            print(f"Error creating RFM segments: {e}")
            return {}
