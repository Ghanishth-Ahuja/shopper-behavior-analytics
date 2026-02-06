from typing import Dict, List, Optional
from datetime import datetime
from app.models.user_features import UserFeatures, UserFeaturesCreate
from app.database.mongodb import MongoDB, Collections
from app.feature_pipeline.rfm_features import RFMFeatureExtractor
from app.feature_pipeline.browsing_features import BrowsingFeatureExtractor
from app.feature_pipeline.category_affinity import CategoryAffinityExtractor
import asyncio
import numpy as np


class FeaturePipeline:
    """Main feature engineering pipeline"""
    
    def __init__(self):
        self.db = MongoDB.get_database()
        self.rfm_extractor = RFMFeatureExtractor()
        self.browsing_extractor = BrowsingFeatureExtractor()
        self.category_extractor = CategoryAffinityExtractor()
    
    async def process_user_features(self, user_id: str) -> UserFeatures:
        """Process all features for a single user"""
        try:
            # Extract all feature types
            rfm_features = await self.rfm_extractor.calculate_rfm_for_user(user_id)
            browsing_features = await self.browsing_extractor.calculate_browsing_features_for_user(user_id)
            category_affinity_vector = await self.category_extractor.calculate_category_affinity_for_user(user_id)
            
            # Generate embedding vector (simplified version)
            embedding_vector = await self._generate_embedding_vector(
                rfm_features, browsing_features, category_affinity_vector
            )
            
            # Create user features object
            user_features = UserFeatures(
                user_id=user_id,
                rfm_features=rfm_features,
                browsing_features=browsing_features,
                category_affinity_vector=category_affinity_vector,
                embedding_vector=embedding_vector,
                last_updated=datetime.utcnow()
            )
            
            # Save to database
            await self._save_user_features(user_features)
            
            return user_features
            
        except Exception as e:
            print(f"Error processing features for user {user_id}: {e}")
            raise
    
    async def process_all_users(self) -> Dict[str, UserFeatures]:
        """Process features for all users"""
        try:
            users_collection = self.db[Collections.USERS]
            cursor = users_collection.find({})
            users = await cursor.to_list(length=None)
            
            all_features = {}
            
            # Process users in batches to avoid memory issues
            batch_size = 100
            for i in range(0, len(users), batch_size):
                batch = users[i:i + batch_size]
                
                # Process batch concurrently
                tasks = [
                    self.process_user_features(user['user_id'])
                    for user in batch
                ]
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        print(f"Error processing user {batch[j]['user_id']}: {result}")
                    else:
                        all_features[result.user_id] = result
                
                print(f"Processed batch {i//batch_size + 1}/{(len(users) + batch_size - 1)//batch_size}")
            
            return all_features
            
        except Exception as e:
            print(f"Error processing all users: {e}")
            return {}
    
    async def update_user_features_realtime(self, user_id: str, event_data: Dict) -> None:
        """Update user features in real-time based on new events"""
        try:
            # Get current features
            current_features = await self.get_user_features(user_id)
            
            if not current_features:
                # If no features exist, create them
                await self.process_user_features(user_id)
                return
            
            # Update features based on event type
            event_type = event_data.get('type')
            
            if event_type == 'purchase':
                # Update RFM features
                await self._update_rfm_after_purchase(user_id, event_data)
            
            elif event_type in ['view', 'add_to_cart']:
                # Update browsing features
                await self._update_browsing_after_interaction(user_id, event_data)
            
            # Regenerate embedding vector
            embedding_vector = await self._generate_embedding_vector(
                current_features.rfm_features,
                current_features.browsing_features,
                current_features.category_affinity_vector
            )
            
            # Update timestamp
            current_features.last_updated = datetime.utcnow()
            current_features.embedding_vector = embedding_vector
            
            # Save updated features
            await self._save_user_features(current_features)
            
        except Exception as e:
            print(f"Error updating features in real-time for user {user_id}: {e}")
    
    async def get_user_features(self, user_id: str) -> Optional[UserFeatures]:
        """Get features for a specific user"""
        try:
            features_collection = self.db[Collections.USER_FEATURES]
            doc = await features_collection.find_one({"user_id": user_id})
            
            if doc:
                return UserFeatures(**doc)
            return None
            
        except Exception as e:
            print(f"Error getting features for user {user_id}: {e}")
            return None
    
    async def get_feature_matrix(self, user_ids: List[str]) -> np.ndarray:
        """Get feature matrix for multiple users for ML models"""
        try:
            features_list = []
            
            for user_id in user_ids:
                user_features = await self.get_user_features(user_id)
                if user_features:
                    # Convert to feature vector
                    feature_vector = self._features_to_vector(user_features)
                    features_list.append(feature_vector)
            
            return np.array(features_list) if features_list else np.array([])
            
        except Exception as e:
            print(f"Error creating feature matrix: {e}")
            return np.array([])
    
    async def _generate_embedding_vector(self, rfm_features, browsing_features, category_affinity_vector) -> List[float]:
        """Generate embedding vector from all features"""
        try:
            # Get all categories for consistent vector size
            all_categories = await self.category_extractor.get_all_categories()
            
            # Create category affinity dictionary
            category_dict = {ca.category: ca.affinity_score for ca in category_affinity_vector}
            
            # Build embedding vector
            embedding = []
            
            # RFM features (3)
            embedding.extend([
                rfm_features.recency / 365,  # Normalize by days in year
                rfm_features.frequency / 50,  # Normalize by expected max frequency
                rfm_features.monetary / 10000  # Normalize by expected max monetary value
            ])
            
            # Browsing features (7)
            embedding.extend([
                browsing_features.avg_session_duration / 60,  # Normalize by hour
                browsing_features.pages_per_session / 20,  # Normalize by expected max pages
                browsing_features.bounce_rate,
                browsing_features.cart_abandonment_rate,
                browsing_features.search_frequency / 10,  # Normalize by expected max searches
                browsing_features.preferred_hour / 24,  # Normalize by hours in day
                np.log1p(browsing_features.weekend_vs_weekday_ratio) / 5  # Log normalize
            ])
            
            # Category affinities (variable size)
            for category in all_categories:
                affinity = category_dict.get(category, 0.0)
                embedding.append(affinity)
            
            return embedding
            
        except Exception as e:
            print(f"Error generating embedding vector: {e}")
            return []
    
    def _features_to_vector(self, user_features: UserFeatures) -> List[float]:
        """Convert user features to vector for ML models"""
        try:
            # Combine all features into a single vector
            vector = []
            
            # RFM features
            vector.extend([
                user_features.rfm_features.recency,
                user_features.rfm_features.frequency,
                user_features.rfm_features.monetary
            ])
            
            # Browsing features
            vector.extend([
                user_features.browsing_features.avg_session_duration,
                user_features.browsing_features.pages_per_session,
                user_features.browsing_features.bounce_rate,
                user_features.browsing_features.cart_abandonment_rate,
                user_features.browsing_features.search_frequency,
                user_features.browsing_features.preferred_hour,
                user_features.browsing_features.weekend_vs_weekday_ratio
            ])
            
            # Category affinities (top 10)
            top_categories = user_features.category_affinity_vector[:10]
            for ca in top_categories:
                vector.append(ca.affinity_score)
            
            # Pad if fewer than 10 categories
            while len(vector) < 20:  # 3 RFM + 7 browsing + 10 categories
                vector.append(0.0)
            
            return vector[:20]  # Ensure consistent size
            
        except Exception as e:
            print(f"Error converting features to vector: {e}")
            return [0.0] * 20
    
    async def _save_user_features(self, user_features: UserFeatures) -> None:
        """Save user features to database"""
        try:
            features_collection = self.db[Collections.USER_FEATURES]
            await features_collection.replace_one(
                {"user_id": user_features.user_id},
                user_features.dict(),
                upsert=True
            )
        except Exception as e:
            print(f"Error saving user features: {e}")
    
    async def _update_rfm_after_purchase(self, user_id: str, event_data: Dict) -> None:
        """Update RFM features after a purchase"""
        try:
            # This would trigger a recalculation of RFM features
            # For now, we'll just mark for full recalculation
            pass
        except Exception as e:
            print(f"Error updating RFM features: {e}")
    
    async def _update_browsing_after_interaction(self, user_id: str, event_data: Dict) -> None:
        """Update browsing features after an interaction"""
        try:
            # This would trigger an update of browsing features
            # For now, we'll just mark for full recalculation
            pass
        except Exception as e:
            print(f"Error updating browsing features: {e}")
    
    async def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance statistics"""
        try:
            # This would typically come from trained ML models
            # For now, return default importance weights
            return {
                "rfm_recency": 0.2,
                "rfm_frequency": 0.25,
                "rfm_monetary": 0.25,
                "browsing_session_duration": 0.1,
                "browsing_pages_per_session": 0.08,
                "browsing_bounce_rate": 0.07,
                "category_affinity": 0.05
            }
        except Exception as e:
            print(f"Error getting feature importance: {e}")
            return {}
