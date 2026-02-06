from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.models.user_features import CategoryAffinity
from app.database.mongodb import MongoDB, Collections
import pandas as pd
import numpy as np
from collections import defaultdict, Counter


class CategoryAffinityExtractor:
    """Extract category affinity features for users"""
    
    def __init__(self):
        self.db = MongoDB.get_database()
    
    async def calculate_category_affinity_for_user(self, user_id: str) -> List[CategoryAffinity]:
        """Calculate category affinity scores for a specific user"""
        try:
            # Get user's transaction history
            transactions_collection = self.db[Collections.TRANSACTIONS]
            cursor = transactions_collection.find({"user_id": user_id})
            transactions = await cursor.to_list(length=None)
            
            # Get user's browsing events
            sessions_collection = self.db[Collections.SESSIONS]
            cursor = sessions_collection.find({"user_id": user_id})
            sessions = await cursor.to_list(length=None)
            
            # Extract product interactions
            product_interactions = defaultdict(int)
            category_interactions = defaultdict(int)
            
            # Process transactions (higher weight)
            for transaction in transactions:
                items = transaction.get('items', [])
                for item in items:
                    product_id = item.get('product_id')
                    product_interactions[product_id] += 5  # Purchase weight
                    
                    # Get product category
                    category = await self._get_product_category(product_id)
                    if category:
                        category_interactions[category] += 5
            
            # Process browsing events (lower weight)
            for session in sessions:
                events = session.get('events', [])
                for event in events:
                    if event.get('type') == 'view':
                        product_id = event.get('product_id')
                        if product_id:
                            product_interactions[product_id] += 1  # View weight
                            
                            category = await self._get_product_category(product_id)
                            if category:
                                category_interactions[category] += 1
                    
                    elif event.get('type') == 'add_to_cart':
                        product_id = event.get('product_id')
                        if product_id:
                            product_interactions[product_id] += 3  # Cart weight
                            
                            category = await self._get_product_category(product_id)
                            if category:
                                category_interactions[category] += 3
            
            # Calculate affinity scores
            total_interactions = sum(category_interactions.values())
            
            if total_interactions == 0:
                return []
            
            category_affinities = []
            for category, interactions in category_interactions.items():
                affinity_score = interactions / total_interactions
                category_affinities.append(
                    CategoryAffinity(category=category, affinity_score=affinity_score)
                )
            
            # Sort by affinity score
            category_affinities.sort(key=lambda x: x.affinity_score, reverse=True)
            
            return category_affinities
            
        except Exception as e:
            print(f"Error calculating category affinity for user {user_id}: {e}")
            return []
    
    async def _get_product_category(self, product_id: str) -> Optional[str]:
        """Get category for a product"""
        try:
            products_collection = self.db[Collections.PRODUCTS]
            product = await products_collection.find_one({"product_id": product_id})
            return product.get('category') if product else None
        except Exception:
            return None
    
    async def get_category_affinity_vector(self, user_id: str, all_categories: List[str]) -> Dict[str, float]:
        """Get normalized category affinity vector for a user"""
        try:
            category_affinities = await self.calculate_category_affinity_for_user(user_id)
            
            # Create vector with all categories
            affinity_vector = {}
            for category in all_categories:
                affinity_vector[category] = 0.0
            
            # Fill in actual affinities
            for ca in category_affinities:
                if ca.category in affinity_vector:
                    affinity_vector[ca.category] = ca.affinity_score
            
            return affinity_vector
            
        except Exception as e:
            print(f"Error creating affinity vector for user {user_id}: {e}")
            return {}
    
    async def get_all_categories(self) -> List[str]:
        """Get all available categories"""
        try:
            products_collection = self.db[Collections.PRODUCTS]
            categories = await products_collection.distinct('category')
            return categories
        except Exception as e:
            print(f"Error getting all categories: {e}")
            return []
    
    async def calculate_cross_category_affinity(self, user_id: str) -> Dict[str, Dict[str, float]]:
        """Calculate cross-category affinity (which categories tend to be purchased together)"""
        try:
            transactions_collection = self.db[Collections.TRANSACTIONS]
            cursor = transactions_collection.find({"user_id": user_id})
            transactions = await cursor.to_list(length=None)
            
            category_cooccurrence = defaultdict(lambda: defaultdict(int))
            
            for transaction in transactions:
                items = transaction.get('items', [])
                categories_in_transaction = set()
                
                # Get categories for all items in transaction
                for item in items:
                    product_id = item.get('product_id')
                    category = await self._get_product_category(product_id)
                    if category:
                        categories_in_transaction.add(category)
                
                # Update co-occurrence counts
                categories_list = list(categories_in_transaction)
                for i, cat1 in enumerate(categories_list):
                    for cat2 in categories_list[i+1:]:
                        category_cooccurrence[cat1][cat2] += 1
                        category_cooccurrence[cat2][cat1] += 1
            
            # Normalize to get affinity scores
            cross_category_affinity = {}
            for cat1, cooccurrences in category_cooccurrence.items():
                total_cooccurrences = sum(cooccurrences.values())
                if total_cooccurrences > 0:
                    cross_category_affinity[cat1] = {
                        cat2: count / total_cooccurrences 
                        for cat2, count in cooccurrences.items()
                    }
            
            return cross_category_affinity
            
        except Exception as e:
            print(f"Error calculating cross-category affinity for user {user_id}: {e}")
            return {}
    
    async def get_category_evolution(self, user_id: str, days: int = 90) -> Dict[str, List[float]]:
        """Track how category preferences evolve over time"""
        try:
            transactions_collection = self.db[Collections.TRANSACTIONS]
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            cursor = transactions_collection.find({
                "user_id": user_id,
                "timestamp": {"$gte": start_date, "$lte": end_date}
            })
            transactions = await cursor.to_list(length=None)
            
            # Group transactions by week
            weekly_categories = defaultdict(lambda: defaultdict(int))
            
            for transaction in transactions:
                timestamp = transaction.get('timestamp')
                week_number = (timestamp - start_date).days // 7
                
                items = transaction.get('items', [])
                for item in items:
                    product_id = item.get('product_id')
                    category = await self._get_product_category(product_id)
                    if category:
                        weekly_categories[week_number][category] += 1
            
            # Calculate weekly affinity scores
            category_evolution = defaultdict(list)
            
            for week in range(days // 7):
                week_categories = weekly_categories[week]
                total_interactions = sum(week_categories.values())
                
                if total_interactions > 0:
                    for category, count in week_categories.items():
                        affinity = count / total_interactions
                        category_evolution[category].append(affinity)
                else:
                    # If no interactions this week, keep previous values or 0
                    for category in category_evolution:
                        category_evolution[category].append(0.0)
            
            return dict(category_evolution)
            
        except Exception as e:
            print(f"Error calculating category evolution for user {user_id}: {e}")
            return {}
    
    async def get_category_lift_analysis(self, user_id: str) -> Dict[str, float]:
        """Calculate category lift (how much more likely user is to purchase from category vs baseline)"""
        try:
            # Get user's category preferences
            user_affinities = await self.calculate_category_affinity_for_user(user_id)
            user_category_dict = {ca.category: ca.affinity_score for ca in user_affinities}
            
            # Get baseline category preferences (all users)
            baseline_affinities = await self._get_baseline_category_affinities()
            
            # Calculate lift
            category_lift = {}
            for category, user_affinity in user_category_dict.items():
                baseline_affinity = baseline_affinities.get(category, 0.01)  # Small default to avoid division by zero
                lift = user_affinity / baseline_affinity if baseline_affinity > 0 else 1.0
                category_lift[category] = lift
            
            return category_lift
            
        except Exception as e:
            print(f"Error calculating category lift for user {user_id}: {e}")
            return {}
    
    async def _get_baseline_category_affinities(self) -> Dict[str, float]:
        """Get baseline category affinities across all users"""
        try:
            transactions_collection = self.db[Collections.TRANSACTIONS]
            cursor = transactions_collection.find({})
            transactions = await cursor.to_list(length=None)
            
            category_counts = defaultdict(int)
            total_transactions = len(transactions)
            
            for transaction in transactions:
                items = transaction.get('items', [])
                for item in items:
                    product_id = item.get('product_id')
                    category = await self._get_product_category(product_id)
                    if category:
                        category_counts[category] += 1
            
            # Calculate baseline affinities
            baseline_affinities = {}
            total_category_interactions = sum(category_counts.values())
            
            for category, count in category_counts.items():
                baseline_affinities[category] = count / total_category_interactions
            
            return baseline_affinities
            
        except Exception as e:
            print(f"Error calculating baseline affinities: {e}")
            return {}
