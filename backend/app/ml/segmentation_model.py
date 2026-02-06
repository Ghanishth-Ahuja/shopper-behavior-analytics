from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import joblib
import os
from datetime import datetime
from app.feature_pipeline.feature_pipeline import FeaturePipeline
from app.database.mongodb import MongoDB, Collections
from app.models.segment import Segment, SegmentCreate
from app.models.user import User


class SegmentationModel:
    """Customer segmentation using various clustering algorithms"""
    
    def __init__(self, model_path: str = "models/segmentation/"):
        self.model_path = model_path
        self.scaler = StandardScaler()
        self.model = None
        self.feature_pipeline = FeaturePipeline()
        self.db = MongoDB.get_database()
        
        # Ensure model directory exists
        os.makedirs(model_path, exist_ok=True)
    
    async def train_segmentation_model(
        self, 
        algorithm: str = "kmeans",
        n_clusters: int = 5,
        use_pca: bool = True
    ) -> Dict[str, any]:
        """Train segmentation model"""
        try:
            print("Starting segmentation model training...")
            
            # Get all user features
            users_collection = self.db[Collections.USERS]
            cursor = users_collection.find({})
            users = await cursor.to_list(length=None)
            
            if len(users) < 10:
                raise ValueError("Need at least 10 users for segmentation")
            
            user_ids = [user['user_id'] for user in users]
            
            # Get feature matrix
            feature_matrix = await self.feature_pipeline.get_feature_matrix(user_ids)
            
            if feature_matrix.size == 0:
                raise ValueError("No features available for training")
            
            print(f"Feature matrix shape: {feature_matrix.shape}")
            
            # Handle missing values
            feature_matrix = np.nan_to_num(feature_matrix, nan=0.0)
            
            # Standardize features
            features_scaled = self.scaler.fit_transform(feature_matrix)
            
            # Optional PCA for dimensionality reduction
            if use_pca and features_scaled.shape[1] > 10:
                pca = PCA(n_components=0.95)  # Keep 95% variance
                features_scaled = pca.fit_transform(features_scaled)
                print(f"Reduced to {features_scaled.shape[1]} components with PCA")
            
            # Train clustering model
            if algorithm == "kmeans":
                self.model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            elif algorithm == "dbscan":
                self.model = DBSCAN(eps=0.5, min_samples=5)
            else:
                raise ValueError(f"Unknown algorithm: {algorithm}")
            
            # Fit model
            cluster_labels = self.model.fit_predict(features_scaled)
            
            # Calculate metrics
            if algorithm == "kmeans":
                silhouette_avg = silhouette_score(features_scaled, cluster_labels)
                print(f"Silhouette Score: {silhouette_avg:.3f}")
            else:
                silhouette_avg = 0.0
            
            # Create segments
            segments = await self._create_segments_from_clusters(
                user_ids, cluster_labels, features_scaled
            )
            
            # Save model
            await self._save_model(algorithm, silhouette_avg)
            
            # Assign users to segments
            await self._assign_users_to_segments(user_ids, cluster_labels)
            
            return {
                "status": "success",
                "algorithm": algorithm,
                "n_clusters": len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0),
                "silhouette_score": silhouette_avg,
                "segments_created": len(segments),
                "users_segmented": len(user_ids)
            }
            
        except Exception as e:
            print(f"Error training segmentation model: {e}")
            return {"status": "error", "message": str(e)}
    
    async def predict_segment(self, user_id: str) -> Optional[str]:
        """Predict segment for a single user"""
        try:
            if self.model is None:
                await self._load_model()
            
            if self.model is None:
                return None
            
            # Get user features
            user_features = await self.feature_pipeline.get_user_features(user_id)
            if not user_features:
                return None
            
            # Convert to vector
            feature_vector = self.feature_pipeline._features_to_vector(user_features)
            feature_vector = np.array(feature_vector).reshape(1, -1)
            feature_vector = np.nan_to_num(feature_vector, nan=0.0)
            
            # Scale features
            feature_vector_scaled = self.scaler.transform(feature_vector)
            
            # Predict cluster
            cluster_label = self.model.predict(feature_vector_scaled)[0]
            
            # Get segment ID for this cluster
            segment_id = await self._get_segment_id_for_cluster(cluster_label)
            
            return segment_id
            
        except Exception as e:
            print(f"Error predicting segment for user {user_id}: {e}")
            return None
    
    async def _create_segments_from_clusters(
        self, 
        user_ids: List[str], 
        cluster_labels: np.ndarray,
        features_scaled: np.ndarray
    ) -> List[Segment]:
        """Create segment objects from clustering results"""
        try:
            segments = []
            unique_clusters = set(cluster_labels)
            
            for cluster_id in unique_clusters:
                if cluster_id == -1:  # DBSCAN noise points
                    continue
                
                # Get users in this cluster
                cluster_mask = cluster_labels == cluster_id
                cluster_user_ids = [user_ids[i] for i in range(len(user_ids)) if cluster_mask[i]]
                cluster_features = features_scaled[cluster_mask]
                
                # Analyze cluster characteristics
                segment_name, characteristics = await self._analyze_cluster(
                    cluster_user_ids, cluster_features
                )
                
                # Create segment
                segment_id = f"segment_{cluster_id}"
                segment = SegmentCreate(
                    segment_id=segment_id,
                    segment_name=segment_name,
                    characteristics=characteristics,
                    top_categories=await self._get_top_categories_for_cluster(cluster_user_ids),
                    price_sensitivity=await self._get_price_sensitivity_for_cluster(cluster_user_ids),
                    avg_lifetime_value=await self._get_avg_ltv_for_cluster(cluster_user_ids),
                    size=len(cluster_user_ids),
                    description=f"Auto-generated segment: {segment_name}"
                )
                
                # Save to database
                segments_collection = self.db[Collections.SEGMENTS]
                await segments_collection.replace_one(
                    {"segment_id": segment_id},
                    segment.dict(),
                    upsert=True
                )
                
                segments.append(Segment(**segment.dict()))
            
            return segments
            
        except Exception as e:
            print(f"Error creating segments from clusters: {e}")
            return []
    
    async def _analyze_cluster(self, user_ids: List[str], cluster_features: np.ndarray) -> Tuple[str, Dict]:
        """Analyze cluster to determine segment name and characteristics"""
        try:
            # Calculate cluster statistics
            avg_features = np.mean(cluster_features, axis=0)
            
            # Determine segment characteristics based on feature patterns
            characteristics = {
                "avg_recency": float(avg_features[0]) if len(avg_features) > 0 else 0,
                "avg_frequency": float(avg_features[1]) if len(avg_features) > 1 else 0,
                "avg_monetary": float(avg_features[2]) if len(avg_features) > 2 else 0,
                "avg_session_duration": float(avg_features[3]) if len(avg_features) > 3 else 0,
                "bounce_rate": float(avg_features[6]) if len(avg_features) > 6 else 0,
            }
            
            # Determine segment name based on characteristics
            recency = characteristics["avg_recency"]
            frequency = characteristics["avg_frequency"]
            monetary = characteristics["avg_monetary"]
            
            if frequency > 0.7 and monetary > 0.7:
                segment_name = "High Value Champions"
            elif frequency > 0.5 and recency < 0.3:
                segment_name = "Active Regulars"
            elif monetary > 0.6:
                segment_name = "Big Spenders"
            elif recency < 0.3:
                segment_name = "New Customers"
            elif frequency < 0.3 and recency > 0.7:
                segment_name = "At Risk"
            else:
                segment_name = "Average Customers"
            
            return segment_name, characteristics
            
        except Exception as e:
            print(f"Error analyzing cluster: {e}")
            return "Unknown Segment", {}
    
    async def _get_top_categories_for_cluster(self, user_ids: List[str]) -> List[str]:
        """Get top categories for users in a cluster"""
        try:
            category_counts = {}
            
            for user_id in user_ids[:50]:  # Sample to avoid memory issues
                user_features = await self.feature_pipeline.get_user_features(user_id)
                if user_features:
                    for ca in user_features.category_affinity_vector[:5]:  # Top 5 categories
                        category = ca.category
                        category_counts[category] = category_counts.get(category, 0) + ca.affinity_score
            
            # Sort by total affinity score
            sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
            return [cat for cat, score in sorted_categories[:5]]
            
        except Exception as e:
            print(f"Error getting top categories for cluster: {e}")
            return []
    
    async def _get_price_sensitivity_for_cluster(self, user_ids: List[str]) -> str:
        """Determine price sensitivity for cluster"""
        try:
            # Analyze average order values and discount usage
            transactions_collection = self.db[Collections.TRANSACTIONS]
            
            total_amounts = []
            discount_amounts = []
            
            for user_id in user_ids[:50]:  # Sample
                cursor = transactions_collection.find({"user_id": user_id})
                transactions = await cursor.to_list(length=None)
                
                for transaction in transactions:
                    total_amounts.append(transaction.get('total_amount', 0))
                    discount_amounts.append(transaction.get('discount_amount', 0))
            
            if not total_amounts:
                return "medium"
            
            avg_order_value = np.mean(total_amounts)
            avg_discount_usage = np.mean(discount_amounts) / avg_order_value if avg_order_value > 0 else 0
            
            # Determine price sensitivity
            if avg_discount_usage > 0.2:
                return "high"
            elif avg_discount_usage < 0.05:
                return "low"
            else:
                return "medium"
                
        except Exception as e:
            print(f"Error determining price sensitivity: {e}")
            return "medium"
    
    async def _get_avg_ltv_for_cluster(self, user_ids: List[str]) -> float:
        """Calculate average lifetime value for cluster"""
        try:
            users_collection = self.db[Collections.USERS]
            
            ltvs = []
            for user_id in user_ids:
                user = await users_collection.find_one({"user_id": user_id})
                if user:
                    ltvs.append(user.get('lifetime_value', 0))
            
            return float(np.mean(ltvs)) if ltvs else 0.0
            
        except Exception as e:
            print(f"Error calculating average LTV: {e}")
            return 0.0
    
    async def _assign_users_to_segments(self, user_ids: List[str], cluster_labels: np.ndarray) -> None:
        """Assign users to their segments"""
        try:
            users_collection = self.db[Collections.USERS]
            
            for i, user_id in enumerate(user_ids):
                cluster_id = cluster_labels[i]
                segment_id = await self._get_segment_id_for_cluster(cluster_id)
                
                if segment_id:
                    await users_collection.update_one(
                        {"user_id": user_id},
                        {"$set": {"segment_id": segment_id}}
                    )
            
        except Exception as e:
            print(f"Error assigning users to segments: {e}")
    
    async def _get_segment_id_for_cluster(self, cluster_id: int) -> Optional[str]:
        """Get segment ID for a cluster label"""
        try:
            segments_collection = self.db[Collections.SEGMENTS]
            segment = await segments_collection.find_one({"segment_id": f"segment_{cluster_id}"})
            return segment.get('segment_id') if segment else None
        except Exception:
            return None
    
    async def _save_model(self, algorithm: str, silhouette_score: float) -> None:
        """Save trained model"""
        try:
            model_data = {
                "model": self.model,
                "scaler": self.scaler,
                "algorithm": algorithm,
                "silhouette_score": silhouette_score,
                "trained_at": datetime.utcnow()
            }
            
            model_file = os.path.join(self.model_path, "segmentation_model.joblib")
            joblib.dump(model_data, model_file)
            print(f"Model saved to {model_file}")
            
        except Exception as e:
            print(f"Error saving model: {e}")
    
    async def _load_model(self) -> bool:
        """Load trained model"""
        try:
            model_file = os.path.join(self.model_path, "segmentation_model.joblib")
            
            if not os.path.exists(model_file):
                return False
            
            model_data = joblib.load(model_file)
            self.model = model_data["model"]
            self.scaler = model_data["scaler"]
            
            print(f"Model loaded from {model_file}")
            return True
            
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    async def get_segment_statistics(self) -> Dict[str, any]:
        """Get statistics about current segmentation"""
        try:
            segments_collection = self.db[Collections.SEGMENTS]
            segments = await segments_collection.find({}).to_list(length=None)
            
            users_collection = self.db[Collections.USERS]
            total_users = await users_collection.count_documents({})
            
            segment_stats = []
            for segment in segments:
                segment_users = await users_collection.count_documents({"segment_id": segment['segment_id']})
                segment_stats.append({
                    "segment_id": segment['segment_id'],
                    "segment_name": segment['segment_name'],
                    "size": segment_users,
                    "percentage": (segment_users / total_users * 100) if total_users > 0 else 0
                })
            
            return {
                "total_segments": len(segments),
                "total_users": total_users,
                "segments": segment_stats
            }
            
        except Exception as e:
            print(f"Error getting segment statistics: {e}")
            return {}
