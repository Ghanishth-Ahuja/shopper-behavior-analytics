from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.database.mongodb import MongoDB, Collections
from app.ml.nlp_analyzer import NLPAnalyzer
from app.feature_pipeline.feature_pipeline import FeaturePipeline
from bson import ObjectId


class AnalyticsService:
    """Service for business analytics and insights"""
    
    def __init__(self):
        self.db = MongoDB.get_database()
        self.nlp_analyzer = NLPAnalyzer()
        self.feature_pipeline = FeaturePipeline()
    
    async def get_affinity_matrix(self) -> List[Dict]:
        """Get category affinity matrix for all segments"""
        try:
            segments_collection = self.db[Collections.SEGMENTS]
            cursor = segments_collection.find({})
            segments = await cursor.to_list(length=None)
            
            affinity_matrix = []
            
            for segment in segments:
                segment_id = segment.get("segment_id")
                segment_name = segment.get("segment_name")
                
                # Get users in segment
                users_collection = self.db[Collections.USERS]
                cursor = users_collection.find({"segment_id": segment_id})
                users = await cursor.to_list(length=None)
                
                if not users:
                    continue
                
                user_ids = [user['user_id'] for user in users]
                
                # Calculate category affinities
                category_affinities = await self._calculate_segment_category_affinities(user_ids)
                
                # Get total users
                total_users = len(users)
                
                affinity_matrix.append({
                    "segment_id": segment_id,
                    "segment_name": segment_name,
                    "category_affinities": category_affinities,
                    "total_users": total_users
                })
            
            return affinity_matrix
            
        except Exception as e:
            print(f"Error getting affinity matrix: {e}")
            return []
    
    async def get_category_lift(self) -> List[Dict]:
        """Get category lift analysis for segments"""
        try:
            segments_collection = self.db[Collections.SEGMENTS]
            cursor = segments_collection.find({})
            segments = await cursor.to_list(length=None)
            
            category_lift = []
            
            for segment in segments:
                segment_id = segment.get("segment_id")
                segment_name = segment.get("segment_name")
                
                # Get users in segment
                users_collection = self.db[Collections.USERS]
                cursor = users_collection.find({"segment_id": segment_id})
                users = await cursor.to_list(length=None)
                
                if not users:
                    continue
                
                user_ids = [user['user_id'] for user in users]
                
                # Calculate lift for each category
                category_lifts = await self._calculate_category_lift_for_segment(user_ids)
                
                for category, lift_data in category_lifts.items():
                    category_lift.append({
                        "category": category,
                        "lift_score": lift_data["lift"],
                        "baseline_conversion": lift_data["baseline_conversion"],
                        "segment_conversion": lift_data["segment_conversion"],
                        "segment_id": segment_id,
                        "segment_name": segment_name
                    })
            
            return category_lift
            
        except Exception as e:
            print(f"Error getting category lift: {e}")
            return []
    
    async def get_customer_personas(self) -> List[Dict]:
        """Get customer personas based on behavioral analysis"""
        try:
            segments_collection = self.db[Collections.SEGMENTS]
            cursor = segments_collection.find({})
            segments = await cursor.to_list(length=None)
            
            personas = []
            
            for segment in segments:
                segment_id = segment.get("segment_id")
                segment_name = segment.get("segment_name")
                
                # Get users in segment
                users_collection = self.db[Collections.USERS]
                cursor = users_collection.find({"segment_id": segment_id})
                users = await cursor.to_list(length=None)
                
                if not users:
                    continue
                
                user_ids = [user['user_id'] for user in users]
                
                # Analyze characteristics
                characteristics = await self._analyze_segment_characteristics(user_ids)
                behaviors = await self._analyze_segment_behaviors(user_ids)
                preferences = await self._analyze_segment_preferences(user_ids)
                
                personas.append({
                    "persona_name": segment_name,
                    "characteristics": characteristics,
                    "behaviors": behaviors,
                    "preferences": preferences,
                    "segment_id": segment_id,
                    "user_count": len(users)
                })
            
            return personas
            
        except Exception as e:
            print(f"Error getting customer personas: {e}")
            return []
    
    async def get_rfm_analysis(self) -> Dict[str, Any]:
        """Get RFM (Recency, Frequency, Monetary) analysis"""
        try:
            from app.feature_pipeline.rfm_features import RFMFeatureExtractor
            
            rfm_extractor = RFMFeatureExtractor()
            rfm_segments = await rfm_extractor.get_rfm_segments()
            
            # Get segment statistics
            segment_stats = {}
            for segment_name, user_ids in rfm_segments.items():
                segment_stats[segment_name] = {
                    "user_count": len(user_ids),
                    "percentage": 0  # Will be calculated below
                }
            
            # Calculate percentages
            total_users = sum(stats["user_count"] for stats in segment_stats.values())
            for stats in segment_stats.values():
                stats["percentage"] = (stats["user_count"] / total_users * 100) if total_users > 0 else 0
            
            return {
                "rfm_segments": segment_stats,
                "total_customers": total_users,
                "analysis_date": datetime.utcnow()
            }
            
        except Exception as e:
            print(f"Error getting RFM analysis: {e}")
            return {}
    
    async def get_cohort_analysis(self) -> Dict[str, Any]:
        """Get cohort analysis for user retention"""
        try:
            # Get users grouped by signup month
            users_collection = self.db[Collections.USERS]
            cursor = users_collection.find({})
            users = await cursor.to_list(length=None)
            
            # Group by signup month
            cohorts = {}
            for user in users:
                signup_date = user.get("signup_date", datetime.utcnow())
                cohort_month = signup_date.strftime("%Y-%m")
                
                if cohort_month not in cohorts:
                    cohorts[cohort_month] = []
                cohorts[cohort_month].append(user['user_id'])
            
            # Calculate retention rates
            cohort_analysis = {}
            
            for cohort_month, user_ids in cohorts.items():
                cohort_data = {
                    "cohort_size": len(user_ids),
                    "retention_rates": {}
                }
                
                # Calculate retention for months 0-6
                for month_offset in range(7):
                    retained_users = await self._calculate_retention(user_ids, month_offset)
                    retention_rate = (retained_users / len(user_ids)) * 100 if user_ids else 0
                    cohort_data["retention_rates"][f"month_{month_offset}"] = retention_rate
                
                cohort_analysis[cohort_month] = cohort_data
            
            return {
                "cohort_analysis": cohort_analysis,
                "analysis_date": datetime.utcnow()
            }
            
        except Exception as e:
            print(f"Error getting cohort analysis: {e}")
            return {}
    
    async def get_conversion_funnel(self) -> Dict[str, Any]:
        """Get conversion funnel analysis"""
        try:
            # Get funnel metrics from sessions
            sessions_collection = self.db[Collections.SESSIONS]
            cursor = sessions_collection.find({})
            sessions = await cursor.to_list(length=None)
            
            total_sessions = len(sessions)
            
            # Count different funnel stages
            view_sessions = 0
            cart_sessions = 0
            purchase_sessions = 0
            
            for session in sessions:
                events = session.get("events", [])
                has_view = any(event.get("type") == "view" for event in events)
                has_cart = any(event.get("type") == "add_to_cart" for event in events)
                has_purchase = any(event.get("type") == "purchase" for event in events)
                
                if has_view:
                    view_sessions += 1
                if has_cart:
                    cart_sessions += 1
                if has_purchase:
                    purchase_sessions += 1
            
            # Calculate conversion rates
            funnel = {
                "total_sessions": total_sessions,
                "view_sessions": view_sessions,
                "cart_sessions": cart_sessions,
                "purchase_sessions": purchase_sessions,
                "view_rate": (view_sessions / total_sessions * 100) if total_sessions > 0 else 0,
                "cart_rate": (cart_sessions / total_sessions * 100) if total_sessions > 0 else 0,
                "purchase_rate": (purchase_sessions / total_sessions * 100) if total_sessions > 0 else 0,
                "cart_to_purchase_rate": (purchase_sessions / cart_sessions * 100) if cart_sessions > 0 else 0
            }
            
            return funnel
            
        except Exception as e:
            print(f"Error getting conversion funnel: {e}")
            return {}
    
    async def get_segment_performance(self, segment_id: str) -> Dict[str, Any]:
        """Get performance metrics for a specific segment"""
        try:
            # Get segment info
            segments_collection = self.db[Collections.SEGMENTS]
            segment = await segments_collection.find_one({"segment_id": segment_id})
            
            if not segment:
                return {"error": "Segment not found"}
            
            # Get users in segment
            users_collection = self.db[Collections.USERS]
            cursor = users_collection.find({"segment_id": segment_id})
            users = await cursor.to_list(length=None)
            
            if not users:
                return {"error": "No users in segment"}
            
            user_ids = [user['user_id'] for user in users]
            
            # Calculate metrics
            metrics = {}
            
            # Transaction metrics
            transaction_metrics = await self._calculate_transaction_metrics(user_ids)
            metrics.update(transaction_metrics)
            
            # Engagement metrics
            engagement_metrics = await self._calculate_engagement_metrics(user_ids)
            metrics.update(engagement_metrics)
            
            # Retention metrics
            retention_metrics = await self._calculate_retention_metrics(user_ids)
            metrics.update(retention_metrics)
            
            return {
                "segment_id": segment_id,
                "segment_name": segment.get("segment_name"),
                "user_count": len(users),
                "metrics": metrics,
                "analysis_date": datetime.utcnow()
            }
            
        except Exception as e:
            print(f"Error getting segment performance for {segment_id}: {e}")
            return {"error": str(e)}
    
    async def get_product_performance(self, category: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get product performance metrics"""
        try:
            products_collection = self.db[Collections.PRODUCTS]
            
            # Build filter
            filter_dict = {}
            if category:
                filter_dict["category"] = category
            
            cursor = products_collection.find(filter_dict).limit(limit)
            products = await cursor.to_list(length=None)
            
            product_performance = []
            
            for product in products:
                product_id = product.get("product_id")
                
                # Calculate metrics for this product
                metrics = await self._calculate_product_metrics(product_id)
                
                product_performance.append({
                    "product_id": product_id,
                    "category": product.get("category"),
                    "brand": product.get("brand"),
                    "metrics": metrics
                })
            
            # Sort by revenue
            product_performance.sort(key=lambda x: x["metrics"]["total_revenue"], reverse=True)
            
            return product_performance
            
        except Exception as e:
            print(f"Error getting product performance: {e}")
            return []
    
    async def get_sentiment_analysis(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get sentiment analysis insights"""
        try:
            sentiment_summary = await self.nlp_analyzer.get_sentiment_summary(category)
            
            # Add additional insights
            if not category:
                # Get sentiment trends over time
                sentiment_trends = await self._get_sentiment_trends()
                sentiment_summary["sentiment_trends"] = sentiment_trends
            
            return sentiment_summary
            
        except Exception as e:
            print(f"Error getting sentiment analysis: {e}")
            return {}
    
    async def get_price_sensitivity_analysis(self) -> Dict[str, Any]:
        """Get price sensitivity analysis by segment"""
        try:
            segments_collection = self.db[Collections.SEGMENTS]
            cursor = segments_collection.find({})
            segments = await cursor.to_list(length=None)
            
            price_sensitivity = {}
            
            for segment in segments:
                segment_id = segment.get("segment_id")
                segment_name = segment.get("segment_name")
                
                # Get users in segment
                users_collection = self.db[Collections.USERS]
                cursor = users_collection.find({"segment_id": segment_id})
                users = await cursor.to_list(length=None)
                
                if not users:
                    continue
                
                user_ids = [user['user_id'] for user in users]
                
                # Calculate price sensitivity metrics
                sensitivity_metrics = await self._calculate_price_sensitivity(user_ids)
                
                price_sensitivity[segment_id] = {
                    "segment_name": segment_name,
                    "user_count": len(users),
                    "price_sensitivity": sensitivity_metrics
                }
            
            return price_sensitivity
            
        except Exception as e:
            print(f"Error getting price sensitivity analysis: {e}")
            return {}
    
    async def get_behavioral_patterns(self) -> Dict[str, Any]:
        """Get behavioral patterns and insights"""
        try:
            patterns = {}
            
            # Time-based patterns
            time_patterns = await self._analyze_time_patterns()
            patterns["time_patterns"] = time_patterns
            
            # Device patterns
            device_patterns = await self._analyze_device_patterns()
            patterns["device_patterns"] = device_patterns
            
            # Category patterns
            category_patterns = await self._analyze_category_patterns()
            patterns["category_patterns"] = category_patterns
            
            # Purchase patterns
            purchase_patterns = await self._analyze_purchase_patterns()
            patterns["purchase_patterns"] = purchase_patterns
            
            return patterns
            
        except Exception as e:
            print(f"Error getting behavioral patterns: {e}")
            return {}
    
    async def get_segment_dashboard(self, segment_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data for a segment"""
        try:
            # Get segment performance
            performance = await self.get_segment_performance(segment_id)
            
            # Get segment insights
            from app.services.segmentation_service import SegmentationService
            segmentation_service = SegmentationService()
            insights = await segmentation_service.get_segment_insights(segment_id)
            
            # Get top products for segment
            top_products = await self._get_top_products_for_segment(segment_id)
            
            # Get recent activity
            recent_activity = await self._get_recent_segment_activity(segment_id)
            
            return {
                "performance": performance,
                "insights": insights.dict() if insights else {},
                "top_products": top_products,
                "recent_activity": recent_activity,
                "dashboard_date": datetime.utcnow()
            }
            
        except Exception as e:
            print(f"Error getting segment dashboard for {segment_id}: {e}")
            return {}
    
    # Helper methods
    async def _calculate_segment_category_affinities(self, user_ids: List[str]) -> Dict[str, float]:
        """Calculate category affinities for a segment"""
        try:
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
                affinities = {cat: score / total_score for cat, score in category_scores.items()}
            else:
                affinities = {}
            
            return affinities
            
        except Exception as e:
            print(f"Error calculating segment category affinities: {e}")
            return {}
    
    async def _calculate_category_lift_for_segment(self, user_ids: List[str]) -> Dict[str, Dict]:
        """Calculate category lift for a segment"""
        try:
            # This would compare segment behavior to baseline
            # For now, return placeholder data
            return {
                "Electronics": {
                    "lift": 1.5,
                    "baseline_conversion": 0.05,
                    "segment_conversion": 0.075
                }
            }
            
        except Exception as e:
            print(f"Error calculating category lift: {e}")
            return {}
    
    async def _analyze_segment_characteristics(self, user_ids: List[str]) -> List[str]:
        """Analyze segment characteristics"""
        try:
            characteristics = []
            
            # Sample users
            sample_users = user_ids[:20]
            
            # Analyze demographics
            users_collection = self.db[Collections.USERS]
            cursor = users_collection.find({"user_id": {"$in": sample_users}})
            users = await cursor.to_list(length=None)
            
            # Analyze acquisition channels
            channels = [user.get("acquisition_channel") for user in users]
            common_channel = max(set(channels), key=channels.count) if channels else "Unknown"
            characteristics.append(f"Primarily acquired via {common_channel}")
            
            # Analyze lifetime value
            ltvs = [user.get("lifetime_value", 0) for user in users]
            avg_ltv = sum(ltvs) / len(ltvs) if ltvs else 0
            
            if avg_ltv > 1000:
                characteristics.append("High lifetime value")
            elif avg_ltv > 500:
                characteristics.append("Medium lifetime value")
            else:
                characteristics.append("Low lifetime value")
            
            return characteristics
            
        except Exception as e:
            print(f"Error analyzing segment characteristics: {e}")
            return []
    
    async def _analyze_segment_behaviors(self, user_ids: List[str]) -> List[str]:
        """Analyze segment behaviors"""
        try:
            behaviors = []
            
            # Analyze RFM patterns
            from app.feature_pipeline.rfm_features import RFMFeatureExtractor
            rfm_extractor = RFMFeatureExtractor()
            
            # Get sample user features
            sample_users = user_ids[:20]
            rfm_features_list = []
            
            for user_id in sample_users:
                rfm_features = await rfm_extractor.calculate_rfm_for_user(user_id)
                rfm_features_list.append(rfm_features)
            
            if rfm_features_list:
                avg_recency = sum(rfm.recency for rfm in rfm_features_list) / len(rfm_features_list)
                avg_frequency = sum(rfm.frequency for rfm in rfm_features_list) / len(rfm_features_list)
                
                if avg_recency < 30:
                    behaviors.append("Recent purchasers")
                if avg_frequency > 3:
                    behaviors.append("Frequent buyers")
            
            return behaviors
            
        except Exception as e:
            print(f"Error analyzing segment behaviors: {e}")
            return []
    
    async def _analyze_segment_preferences(self, user_ids: List[str]) -> List[str]:
        """Analyze segment preferences"""
        try:
            preferences = []
            
            # Get category affinities
            category_affinities = await self._calculate_segment_category_affinities(user_ids)
            
            # Top categories
            top_categories = sorted(category_affinities.items(), key=lambda x: x[1], reverse=True)[:3]
            
            for category, affinity in top_categories:
                if affinity > 0.1:  # Threshold
                    preferences.append(f"Strong preference for {category}")
            
            return preferences
            
        except Exception as e:
            print(f"Error analyzing segment preferences: {e}")
            return []
    
    async def _calculate_retention(self, user_ids: List[str], month_offset: int) -> int:
        """Calculate retention for given month offset"""
        try:
            # This would check if users are still active after X months
            # For now, return placeholder
            return len(user_ids) // (month_offset + 1)  # Simple decay
            
        except Exception as e:
            print(f"Error calculating retention: {e}")
            return 0
    
    async def _calculate_transaction_metrics(self, user_ids: List[str]) -> Dict[str, Any]:
        """Calculate transaction metrics for users"""
        try:
            transactions_collection = self.db[Collections.TRANSACTIONS]
            cursor = transactions_collection.find({"user_id": {"$in": user_ids}})
            transactions = await cursor.to_list(length=None)
            
            if not transactions:
                return {
                    "total_transactions": 0,
                    "total_revenue": 0,
                    "avg_order_value": 0
                }
            
            total_transactions = len(transactions)
            total_revenue = sum(t.get("total_amount", 0) for t in transactions)
            avg_order_value = total_revenue / total_transactions
            
            return {
                "total_transactions": total_transactions,
                "total_revenue": total_revenue,
                "avg_order_value": avg_order_value
            }
            
        except Exception as e:
            print(f"Error calculating transaction metrics: {e}")
            return {}
    
    async def _calculate_engagement_metrics(self, user_ids: List[str]) -> Dict[str, Any]:
        """Calculate engagement metrics for users"""
        try:
            sessions_collection = self.db[Collections.SESSIONS]
            cursor = sessions_collection.find({"user_id": {"$in": user_ids}})
            sessions = await cursor.to_list(length=None)
            
            if not sessions:
                return {
                    "total_sessions": 0,
                    "avg_session_duration": 0,
                    "pages_per_session": 0
                }
            
            total_sessions = len(sessions)
            
            # Calculate average session duration
            durations = []
            for session in sessions:
                start_time = session.get("start_time")
                end_time = session.get("end_time")
                if start_time and end_time:
                    duration = (end_time - start_time).total_seconds() / 60  # minutes
                    durations.append(duration)
            
            avg_session_duration = sum(durations) / len(durations) if durations else 0
            
            # Calculate pages per session
            total_events = sum(len(session.get("events", [])) for session in sessions)
            pages_per_session = total_events / total_sessions if total_sessions > 0 else 0
            
            return {
                "total_sessions": total_sessions,
                "avg_session_duration": avg_session_duration,
                "pages_per_session": pages_per_session
            }
            
        except Exception as e:
            print(f"Error calculating engagement metrics: {e}")
            return {}
    
    async def _calculate_retention_metrics(self, user_ids: List[str]) -> Dict[str, Any]:
        """Calculate retention metrics for users"""
        try:
            # Calculate 30-day retention
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            sessions_collection = self.db[Collections.SESSIONS]
            cursor = sessions_collection.find({
                "user_id": {"$in": user_ids},
                "start_time": {"$gte": thirty_days_ago}
            })
            
            recent_sessions = await cursor.to_list(length=None)
            active_users = set(session.get("user_id") for session in recent_sessions)
            
            retention_rate = (len(active_users) / len(user_ids)) * 100 if user_ids else 0
            
            return {
                "retention_rate_30d": retention_rate,
                "active_users_30d": len(active_users)
            }
            
        except Exception as e:
            print(f"Error calculating retention metrics: {e}")
            return {}
    
    async def _calculate_product_metrics(self, product_id: str) -> Dict[str, Any]:
        """Calculate metrics for a specific product"""
        try:
            # Transaction metrics
            transactions_collection = self.db[Collections.TRANSACTIONS]
            pipeline = [
                {"$match": {"items.product_id": product_id}},
                {"$unwind": "$items"},
                {"$match": {"items.product_id": product_id}},
                {"$group": {
                    "_id": None,
                    "total_quantity": {"$sum": "$items.quantity"},
                    "total_revenue": {"$sum": {"$multiply": ["$items.price", "$items.quantity"]}},
                    "total_transactions": {"$sum": 1},
                    "unique_customers": {"$addToSet": "$user_id"}
                }},
                {"$project": {
                    "total_quantity": 1,
                    "total_revenue": 1,
                    "total_transactions": 1,
                    "unique_customers": {"$size": "$unique_customers"}
                }}
            ]
            
            cursor = transactions_collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            if results:
                return results[0]
            
            return {
                "total_quantity": 0,
                "total_revenue": 0,
                "total_transactions": 0,
                "unique_customers": 0
            }
            
        except Exception as e:
            print(f"Error calculating product metrics: {e}")
            return {}
    
    async def _get_sentiment_trends(self) -> Dict[str, Any]:
        """Get sentiment trends over time"""
        try:
            # This would analyze sentiment trends
            # For now, return placeholder
            return {
                "trend": "stable",
                "change": 0.02,
                "period": "30 days"
            }
            
        except Exception as e:
            print(f"Error getting sentiment trends: {e}")
            return {}
    
    async def _calculate_price_sensitivity(self, user_ids: List[str]) -> Dict[str, Any]:
        """Calculate price sensitivity for users"""
        try:
            # This would analyze discount usage and price patterns
            # For now, return placeholder
            return {
                "sensitivity_score": 0.6,
                "discount_usage_rate": 0.3,
                "avg_price_point": 50.0
            }
            
        except Exception as e:
            print(f"Error calculating price sensitivity: {e}")
            return {}
    
    async def _analyze_time_patterns(self) -> Dict[str, Any]:
        """Analyze time-based patterns"""
        try:
            # This would analyze purchase times, browsing patterns
            # For now, return placeholder
            return {
                "peak_hour": 14,  # 2 PM
                "peak_day": "Saturday",
                "seasonal_trend": "increasing"
            }
            
        except Exception as e:
            print(f"Error analyzing time patterns: {e}")
            return {}
    
    async def _analyze_device_patterns(self) -> Dict[str, Any]:
        """Analyze device usage patterns"""
        try:
            # This would analyze device preferences
            # For now, return placeholder
            return {
                "mobile_percentage": 65,
                "desktop_percentage": 30,
                "tablet_percentage": 5
            }
            
        except Exception as e:
            print(f"Error analyzing device patterns: {e}")
            return {}
    
    async def _analyze_category_patterns(self) -> Dict[str, Any]:
        """Analyze category interaction patterns"""
        try:
            # This would analyze cross-category behavior
            # For now, return placeholder
            return {
                "cross_category_rate": 0.4,
                "top_cross_categories": ["Electronics -> Accessories", "Clothing -> Shoes"]
            }
            
        except Exception as e:
            print(f"Error analyzing category patterns: {e}")
            return {}
    
    async def _analyze_purchase_patterns(self) -> Dict[str, Any]:
        """Analyze purchase patterns"""
        try:
            # This would analyze purchase cycles, basket sizes
            # For now, return placeholder
            return {
                "avg_purchase_cycle": 14,  # days
                "avg_basket_size": 2.3,
                "repeat_purchase_rate": 0.6
            }
            
        except Exception as e:
            print(f"Error analyzing purchase patterns: {e}")
            return {}
    
    async def _get_top_products_for_segment(self, segment_id: str) -> List[Dict]:
        """Get top products for a segment"""
        try:
            # This would get most purchased products by segment
            # For now, return placeholder
            return [
                {"product_id": "prod_001", "purchases": 150},
                {"product_id": "prod_002", "purchases": 120}
            ]
            
        except Exception as e:
            print(f"Error getting top products for segment: {e}")
            return []
    
    async def _get_recent_segment_activity(self, segment_id: str) -> List[Dict]:
        """Get recent activity for a segment"""
        try:
            # This would get recent events, purchases
            # For now, return placeholder
            return [
                {"type": "purchase", "count": 25, "date": "2024-01-15"},
                {"type": "session", "count": 100, "date": "2024-01-15"}
            ]
            
        except Exception as e:
            print(f"Error getting recent segment activity: {e}")
            return []
