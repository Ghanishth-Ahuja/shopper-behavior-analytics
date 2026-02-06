from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.segment import Segment, SegmentCreate, SegmentUpdate, SegmentInsight
from app.database.mongodb import MongoDB, Collections
from app.ml.segmentation_model import SegmentationModel
from app.feature_pipeline.feature_pipeline import FeaturePipeline
from bson import ObjectId


class SegmentationService:
    """Service for customer segmentation operations"""
    
    def __init__(self):
        self.db = MongoDB.get_database()
        self.segmentation_model = SegmentationModel()
        self.feature_pipeline = FeaturePipeline()
    
    async def train_segmentation_model(self) -> Dict[str, Any]:
        """Train the segmentation model"""
        try:
            result = await self.segmentation_model.train_segmentation_model()
            return result
        except Exception as e:
            print(f"Error training segmentation model: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_segments(self, skip: int = 0, limit: int = 100) -> List[Segment]:
        """Get all segments"""
        try:
            segments_collection = self.db[Collections.SEGMENTS]
            cursor = segments_collection.find().skip(skip).limit(limit)
            segments = await cursor.to_list(length=None)
            
            return [Segment(**segment) for segment in segments]
            
        except Exception as e:
            print(f"Error getting segments: {e}")
            return []
    
    async def get_segment(self, segment_id: str) -> Optional[Segment]:
        """Get segment by ID"""
        try:
            segments_collection = self.db[Collections.SEGMENTS]
            segment_doc = await segments_collection.find_one({"segment_id": segment_id})
            
            if segment_doc:
                return Segment(**segment_doc)
            return None
            
        except Exception as e:
            print(f"Error getting segment {segment_id}: {e}")
            return None
    
    async def create_segment(self, segment_data: SegmentCreate) -> Segment:
        """Create a new segment (manual)"""
        try:
            segments_collection = self.db[Collections.SEGMENTS]
            
            # Check if segment already exists
            existing_segment = await segments_collection.find_one({"segment_id": segment_data.segment_id})
            if existing_segment:
                raise ValueError(f"Segment with ID {segment_data.segment_id} already exists")
            
            # Create segment document
            segment_dict = segment_data.dict()
            segment_dict["_id"] = ObjectId()
            segment_dict["created_at"] = datetime.utcnow()
            segment_dict["updated_at"] = datetime.utcnow()
            
            # Insert segment
            result = await segments_collection.insert_one(segment_dict)
            
            # Get created segment
            created_segment = await segments_collection.find_one({"_id": result.inserted_id})
            
            return Segment(**created_segment)
            
        except Exception as e:
            print(f"Error creating segment: {e}")
            raise
    
    async def update_segment(self, segment_id: str, segment_update: SegmentUpdate) -> Optional[Segment]:
        """Update segment information"""
        try:
            segments_collection = self.db[Collections.SEGMENTS]
            
            # Prepare update data
            update_data = segment_update.dict(exclude_unset=True)
            if not update_data:
                return await self.get_segment(segment_id)
            
            update_data["updated_at"] = datetime.utcnow()
            
            # Update segment
            result = await segments_collection.update_one(
                {"segment_id": segment_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_segment(segment_id)
            
            return None
            
        except Exception as e:
            print(f"Error updating segment {segment_id}: {e}")
            return None
    
    async def delete_segment(self, segment_id: str) -> bool:
        """Delete a segment"""
        try:
            segments_collection = self.db[Collections.SEGMENTS]
            result = await segments_collection.delete_one({"segment_id": segment_id})
            
            # Remove segment assignment from users
            if result.deleted_count > 0:
                users_collection = self.db[Collections.USERS]
                await users_collection.update_many(
                    {"segment_id": segment_id},
                    {"$unset": {"segment_id": ""}}
                )
            
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Error deleting segment {segment_id}: {e}")
            return False
    
    async def get_segment_insights(self, segment_id: str) -> Optional[SegmentInsight]:
        """Get detailed insights for a segment"""
        try:
            segment = await self.get_segment(segment_id)
            if not segment:
                return None
            
            # Get users in segment
            users_collection = self.db[Collections.USERS]
            cursor = users_collection.find({"segment_id": segment_id})
            users = await cursor.to_list(length=None)
            
            if not users:
                return SegmentInsight(
                    segment_id=segment_id,
                    segment_name=segment.segment_name,
                    key_behaviors=[],
                    preferences={},
                    pain_points=[],
                    recommendations=[],
                    conversion_rate=0,
                    avg_order_value=0,
                    churn_risk="low"
                )
            
            user_ids = [user['user_id'] for user in users]
            
            # Analyze behaviors
            key_behaviors = await self._analyze_key_behaviors(user_ids)
            
            # Analyze preferences
            preferences = await self._analyze_preferences(user_ids)
            
            # Identify pain points
            pain_points = await self._identify_pain_points(user_ids)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(segment, user_ids)
            
            # Calculate metrics
            conversion_rate = await self._calculate_conversion_rate(user_ids)
            avg_order_value = await self._calculate_avg_order_value(user_ids)
            churn_risk = await self._assess_churn_risk(user_ids)
            
            return SegmentInsight(
                segment_id=segment_id,
                segment_name=segment.segment_name,
                key_behaviors=key_behaviors,
                preferences=preferences,
                pain_points=pain_points,
                recommendations=recommendations,
                conversion_rate=conversion_rate,
                avg_order_value=avg_order_value,
                churn_risk=churn_risk
            )
            
        except Exception as e:
            print(f"Error getting segment insights for {segment_id}: {e}")
            return None
    
    async def get_segment_users(self, segment_id: str, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Get users in a specific segment"""
        try:
            users_collection = self.db[Collections.USERS]
            cursor = users_collection.find({"segment_id": segment_id}).skip(skip).limit(limit)
            users = await cursor.to_list(length=None)
            
            return [
                {
                    "user_id": user['user_id'],
                    "signup_date": user.get('signup_date'),
                    "lifetime_value": user.get('lifetime_value', 0),
                    "acquisition_channel": user.get('acquisition_channel')
                }
                for user in users
            ]
            
        except Exception as e:
            print(f"Error getting segment users for {segment_id}: {e}")
            return []
    
    async def assign_user_to_segment(self, user_id: str, segment_id: str) -> bool:
        """Assign a user to a segment"""
        try:
            # Check if segment exists
            segment = await self.get_segment(segment_id)
            if not segment:
                return False
            
            # Check if user exists
            users_collection = self.db[Collections.USERS]
            user = await users_collection.find_one({"user_id": user_id})
            if not user:
                return False
            
            # Update user segment
            result = await users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"segment_id": segment_id}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error assigning user {user_id} to segment {segment_id}: {e}")
            return False
    
    async def _analyze_key_behaviors(self, user_ids: List[str]) -> List[str]:
        """Analyze key behaviors for users in segment"""
        try:
            behaviors = []
            
            # Analyze RFM patterns
            rfm_behaviors = await self._analyze_rfm_behaviors(user_ids)
            behaviors.extend(rfm_behaviors)
            
            # Analyze browsing patterns
            browsing_behaviors = await self._analyze_browsing_behaviors(user_ids)
            behaviors.extend(browsing_behaviors)
            
            # Analyze purchase patterns
            purchase_behaviors = await self._analyze_purchase_behaviors(user_ids)
            behaviors.extend(purchase_behaviors)
            
            return behaviors[:5]  # Return top 5 behaviors
            
        except Exception as e:
            print(f"Error analyzing key behaviors: {e}")
            return []
    
    async def _analyze_preferences(self, user_ids: List[str]) -> Dict[str, float]:
        """Analyze preferences for users in segment"""
        try:
            # Aggregate category affinities
            category_scores = {}
            
            for user_id in user_ids[:50]:  # Sample for performance
                user_features = await self.feature_pipeline.get_user_features(user_id)
                if user_features:
                    for ca in user_features.category_affinity_vector:
                        category = ca.category
                        score = ca.affinity_score
                        category_scores[category] = category_scores.get(category, 0) + score
            
            # Normalize scores
            total_score = sum(category_scores.values())
            if total_score > 0:
                preferences = {cat: score / total_score for cat, score in category_scores.items()}
            else:
                preferences = {}
            
            # Sort and return top preferences
            sorted_preferences = dict(sorted(preferences.items(), key=lambda x: x[1], reverse=True)[:10])
            return sorted_preferences
            
        except Exception as e:
            print(f"Error analyzing preferences: {e}")
            return {}
    
    async def _identify_pain_points(self, user_ids: List[str]) -> List[str]:
        """Identify pain points from reviews and behavior"""
        try:
            pain_points = []
            
            # Analyze negative reviews
            reviews_collection = self.db[Collections.REVIEWS]
            cursor = reviews_collection.find({
                "user_id": {"$in": user_ids},
                "sentiment_score": {"$lte": -0.05}
            })
            negative_reviews = await cursor.to_list(length=None)
            
            if negative_reviews:
                # Common pain points from negative reviews
                pain_points.append("High product prices mentioned in reviews")
                pain_points.append("Quality concerns in recent feedback")
                pain_points.append("Shipping/delivery issues reported")
            
            # Analyze cart abandonment
            sessions_collection = self.db[Collections.SESSIONS]
            cursor = sessions_collection.find({"user_id": {"$in": user_ids}})
            sessions = await cursor.to_list(length=None)
            
            cart_additions = 0
            purchases = 0
            
            for session in sessions:
                events = session.get("events", [])
                cart_additions += len([e for e in events if e.get("type") == "add_to_cart"])
                purchases += len([e for e in events if e.get("type") == "purchase"])
            
            if cart_additions > 0:
                abandonment_rate = ((cart_additions - purchases) / cart_additions) * 100
                if abandonment_rate > 70:
                    pain_points.append("High cart abandonment rate")
            
            return pain_points[:3]  # Return top 3 pain points
            
        except Exception as e:
            print(f"Error identifying pain points: {e}")
            return []
    
    async def _generate_recommendations(self, segment: Segment, user_ids: List[str]) -> List[str]:
        """Generate recommendations for segment"""
        try:
            recommendations = []
            
            # Based on price sensitivity
            price_sensitivity = segment.price_sensitivity
            if price_sensitivity == "high":
                recommendations.append("Offer discounts and promotions")
                recommendations.append("Highlight value-for-money products")
            elif price_sensitivity == "low":
                recommendations.append("Focus on premium products")
                recommendations.append("Emphasize quality and features")
            
            # Based on top categories
            top_categories = segment.top_categories[:3]
            if top_categories:
                recommendations.append(f"Promote products in {', '.join(top_categories)}")
            
            # Based on segment characteristics
            if "champions" in segment.segment_name.lower():
                recommendations.append("Create loyalty programs")
                recommendations.append("Offer early access to new products")
            elif "at risk" in segment.segment_name.lower():
                recommendations.append("Send re-engagement campaigns")
                recommendations.append("Offer special incentives")
            
            return recommendations[:5]  # Return top 5 recommendations
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return []
    
    async def _calculate_conversion_rate(self, user_ids: List[str]) -> float:
        """Calculate conversion rate for segment"""
        try:
            sessions_collection = self.db[Collections.SESSIONS]
            cursor = sessions_collection.find({"user_id": {"$in": user_ids}})
            sessions = await cursor.to_list(length=None)
            
            total_sessions = len(sessions)
            if total_sessions == 0:
                return 0.0
            
            purchase_sessions = 0
            for session in sessions:
                events = session.get("events", [])
                if any(e.get("type") == "purchase" for e in events):
                    purchase_sessions += 1
            
            return (purchase_sessions / total_sessions) * 100
            
        except Exception as e:
            print(f"Error calculating conversion rate: {e}")
            return 0.0
    
    async def _calculate_avg_order_value(self, user_ids: List[str]) -> float:
        """Calculate average order value for segment"""
        try:
            transactions_collection = self.db[Collections.TRANSACTIONS]
            cursor = transactions_collection.find({"user_id": {"$in": user_ids}})
            transactions = await cursor.to_list(length=None)
            
            if not transactions:
                return 0.0
            
            total_amount = sum(t.get("total_amount", 0) for t in transactions)
            return total_amount / len(transactions)
            
        except Exception as e:
            print(f"Error calculating average order value: {e}")
            return 0.0
    
    async def _assess_churn_risk(self, user_ids: List[str]) -> str:
        """Assess churn risk for segment"""
        try:
            # Analyze recent activity
            from datetime import timedelta
            
            sessions_collection = self.db[Collections.SESSIONS]
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            cursor = sessions_collection.find({
                "user_id": {"$in": user_ids},
                "start_time": {"$gte": thirty_days_ago}
            })
            recent_sessions = await cursor.to_list(length=None)
            
            active_users = set()
            for session in recent_sessions:
                active_users.add(session.get("user_id"))
            
            active_percentage = (len(active_users) / len(user_ids)) * 100
            
            if active_percentage > 70:
                return "low"
            elif active_percentage > 40:
                return "medium"
            else:
                return "high"
            
        except Exception as e:
            print(f"Error assessing churn risk: {e}")
            return "medium"
    
    async def _analyze_rfm_behaviors(self, user_ids: List[str]) -> List[str]:
        """Analyze RFM behaviors"""
        try:
            behaviors = []
            
            # Get RFM features for sample users
            sample_users = user_ids[:20]
            rfm_features = []
            
            for user_id in sample_users:
                user_features = await self.feature_pipeline.get_user_features(user_id)
                if user_features:
                    rfm_features.append(user_features.rfm_features)
            
            if not rfm_features:
                return behaviors
            
            # Analyze patterns
            avg_recency = sum(rfm.recency for rfm in rfm_features) / len(rfm_features)
            avg_frequency = sum(rfm.frequency for rfm in rfm_features) / len(rfm_features)
            avg_monetary = sum(rfm.monetary for rfm in rfm_features) / len(rfm_features)
            
            if avg_recency < 30:
                behaviors.append("Recent purchasers")
            if avg_frequency > 5:
                behaviors.append("Frequent buyers")
            if avg_monetary > 500:
                behaviors.append("High spenders")
            
            return behaviors
            
        except Exception as e:
            print(f"Error analyzing RFM behaviors: {e}")
            return []
    
    async def _analyze_browsing_behaviors(self, user_ids: List[str]) -> List[str]:
        """Analyze browsing behaviors"""
        try:
            behaviors = []
            
            # Get browsing features for sample users
            sample_users = user_ids[:20]
            browsing_features = []
            
            for user_id in sample_users:
                user_features = await self.feature_pipeline.get_user_features(user_id)
                if user_features:
                    browsing_features.append(user_features.browsing_features)
            
            if not browsing_features:
                return behaviors
            
            # Analyze patterns
            avg_session_duration = sum(bf.avg_session_duration for bf in browsing_features) / len(browsing_features)
            avg_bounce_rate = sum(bf.bounce_rate for bf in browsing_features) / len(browsing_features)
            avg_search_frequency = sum(bf.search_frequency for bf in browsing_features) / len(browsing_features)
            
            if avg_session_duration > 15:
                behaviors.append("Long browsing sessions")
            if avg_bounce_rate < 0.3:
                behaviors.append("Low bounce rate")
            if avg_search_frequency > 2:
                behaviors.append("Frequent searchers")
            
            return behaviors
            
        except Exception as e:
            print(f"Error analyzing browsing behaviors: {e}")
            return []
    
    async def _analyze_purchase_behaviors(self, user_ids: List[str]) -> List[str]:
        """Analyze purchase behaviors"""
        try:
            behaviors = []
            
            # Analyze purchase patterns
            transactions_collection = self.db[Collections.TRANSACTIONS]
            cursor = transactions_collection.find({"user_id": {"$in": user_ids}})
            transactions = await cursor.to_list(length=None)
            
            if not transactions:
                return behaviors
            
            # Category diversity
            categories = set()
            for transaction in transactions:
                items = transaction.get("items", [])
                for item in items:
                    product_id = item.get("product_id")
                    category = await self._get_product_category(product_id)
                    if category:
                        categories.add(category)
            
            if len(categories) > 5:
                behaviors.append("Diverse category purchasers")
            elif len(categories) < 2:
                behaviors.append("Category-focused purchasers")
            
            # Discount usage
            discount_transactions = len([t for t in transactions if t.get("discount_amount", 0) > 0])
            discount_rate = (discount_transactions / len(transactions)) * 100
            
            if discount_rate > 50:
                behaviors.append("Discount-driven purchasers")
            
            return behaviors
            
        except Exception as e:
            print(f"Error analyzing purchase behaviors: {e}")
            return []
    
    async def _get_product_category(self, product_id: str) -> Optional[str]:
        """Get category for a product"""
        try:
            products_collection = self.db[Collections.PRODUCTS]
            product = await products_collection.find_one({"product_id": product_id})
            return product.get("category") if product else None
        except Exception:
            return None
