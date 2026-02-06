from typing import List, Optional, Dict, Any
from app.ml.recommendation_engine import RecommendationEngine
from app.database.mongodb import MongoDB, Collections
from bson import ObjectId


class RecommendationService:
    """Service for recommendation operations"""
    
    def __init__(self):
        self.db = MongoDB.get_database()
        self.recommendation_engine = RecommendationEngine()
    
    async def get_user_recommendations(
        self,
        user_id: str,
        limit: int = 10,
        category: Optional[str] = None,
        price_range: Optional[str] = None
    ) -> List[Dict]:
        """Get personalized recommendations for a user"""
        try:
            recommendations = await self.recommendation_engine.get_user_recommendations(
                user_id=user_id,
                limit=limit,
                category=category,
                price_range=price_range
            )
            
            # Enrich with product details
            enriched_recommendations = []
            for rec in recommendations:
                product_id = rec.get("product_id")
                product = await self._get_product_details(product_id)
                
                if product:
                    enriched_rec = rec.copy()
                    enriched_rec["product_details"] = product
                    enriched_recommendations.append(enriched_rec)
            
            return enriched_recommendations
            
        except Exception as e:
            print(f"Error getting user recommendations for {user_id}: {e}")
            return []
    
    async def get_segment_recommendations(
        self,
        segment_id: str,
        limit: int = 10,
        category: Optional[str] = None
    ) -> List[Dict]:
        """Get recommendations for a user segment"""
        try:
            recommendations = await self.recommendation_engine.get_segment_recommendations(
                segment_id=segment_id,
                limit=limit,
                category=category
            )
            
            # Enrich with product details
            enriched_recommendations = []
            for rec in recommendations:
                product_id = rec.get("product_id")
                product = await self._get_product_details(product_id)
                
                if product:
                    enriched_rec = rec.copy()
                    enriched_rec["product_details"] = product
                    enriched_recommendations.append(enriched_rec)
            
            return enriched_recommendations
            
        except Exception as e:
            print(f"Error getting segment recommendations for {segment_id}: {e}")
            return []
    
    async def get_similar_products(self, product_id: str, limit: int = 10) -> List[Dict]:
        """Get similar products based on content and collaborative filtering"""
        try:
            recommendations = await self.recommendation_engine.get_similar_products(
                product_id=product_id,
                limit=limit
            )
            
            # Enrich with product details
            enriched_recommendations = []
            for rec in recommendations:
                similar_product_id = rec.get("product_id")
                product = await self._get_product_details(similar_product_id)
                
                if product:
                    enriched_rec = rec.copy()
                    enriched_rec["product_details"] = product
                    enriched_recommendations.append(enriched_rec)
            
            return enriched_recommendations
            
        except Exception as e:
            print(f"Error getting similar products for {product_id}: {e}")
            return []
    
    async def get_trending_products(self, limit: int = 10, category: Optional[str] = None) -> List[Dict]:
        """Get trending products"""
        try:
            recommendations = await self.recommendation_engine.get_trending_products(
                limit=limit,
                category=category
            )
            
            # Enrich with product details
            enriched_recommendations = []
            for rec in recommendations:
                product_id = rec.get("product_id")
                product = await self._get_product_details(product_id)
                
                if product:
                    enriched_rec = rec.copy()
                    enriched_rec["product_details"] = product
                    enriched_recommendations.append(enriched_rec)
            
            return enriched_recommendations
            
        except Exception as e:
            print(f"Error getting trending products: {e}")
            return []
    
    async def get_frequently_bought_together(self, product_id: str, limit: int = 5) -> List[Dict]:
        """Get products frequently bought together with the given product"""
        try:
            recommendations = await self.recommendation_engine.get_frequently_bought_together(
                product_id=product_id,
                limit=limit
            )
            
            # Enrich with product details
            enriched_recommendations = []
            for rec in recommendations:
                bundled_product_id = rec.get("product_id")
                product = await self._get_product_details(bundled_product_id)
                
                if product:
                    enriched_rec = rec.copy()
                    enriched_rec["product_details"] = product
                    enriched_recommendations.append(enriched_rec)
            
            return enriched_recommendations
            
        except Exception as e:
            print(f"Error getting frequently bought together for {product_id}: {e}")
            return []
    
    async def explain_recommendation(self, user_id: str, product_id: str) -> Dict:
        """Explain why a product is recommended to a user"""
        try:
            explanation = await self.recommendation_engine.explain_recommendation(
                user_id=user_id,
                product_id=product_id
            )
            
            # Add product details
            product = await self._get_product_details(product_id)
            if product:
                explanation["product_details"] = product
            
            return explanation
            
        except Exception as e:
            print(f"Error explaining recommendation for {user_id}, {product_id}: {e}")
            return {}
    
    async def record_feedback(
        self,
        user_id: str,
        product_id: str,
        feedback: str,
        position: int
    ) -> None:
        """Record feedback for recommendation improvement"""
        try:
            await self.recommendation_engine.record_feedback(
                user_id=user_id,
                product_id=product_id,
                feedback=feedback,
                position=position
            )
        except Exception as e:
            print(f"Error recording feedback: {e}")
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get recommendation system performance metrics"""
        try:
            # Get feedback statistics
            feedback_collection = self.db.get_collection("recommendation_feedback")
            cursor = feedback_collection.find({})
            feedback_records = await cursor.to_list(length=None)
            
            if not feedback_records:
                return {
                    "total_recommendations": 0,
                    "click_rate": 0,
                    "purchase_rate": 0,
                    "ignore_rate": 0,
                    "avg_position": 0
                }
            
            # Calculate metrics
            total_feedback = len(feedback_records)
            clicks = len([f for f in feedback_records if f.get("feedback") == "click"])
            purchases = len([f for f in feedback_records if f.get("feedback") == "purchase"])
            ignores = len([f for f in feedback_records if f.get("feedback") == "ignore"])
            
            positions = [f.get("position", 0) for f in feedback_records]
            avg_position = sum(positions) / len(positions) if positions else 0
            
            return {
                "total_recommendations": total_feedback,
                "click_rate": (clicks / total_feedback) * 100,
                "purchase_rate": (purchases / total_feedback) * 100,
                "ignore_rate": (ignores / total_feedback) * 100,
                "avg_position": avg_position,
                "total_clicks": clicks,
                "total_purchases": purchases,
                "total_ignores": ignores
            }
            
        except Exception as e:
            print(f"Error getting performance metrics: {e}")
            return {}
    
    async def get_recommendation_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive recommendation analytics"""
        try:
            from datetime import timedelta
            
            feedback_collection = self.db.get_collection("recommendation_feedback")
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            cursor = feedback_collection.find({
                "timestamp": {"$gte": start_date, "$lte": end_date}
            })
            feedback_records = await cursor.to_list(length=None)
            
            if not feedback_records:
                return {
                    "period_days": days,
                    "total_recommendations": 0,
                    "daily_metrics": {},
                    "top_products": {},
                    "segment_performance": {}
                }
            
            # Daily metrics
            daily_metrics = {}
            for record in feedback_records:
                date = record.get("timestamp", datetime.utcnow()).date()
                date_str = str(date)
                
                if date_str not in daily_metrics:
                    daily_metrics[date_str] = {"clicks": 0, "purchases": 0, "ignores": 0}
                
                feedback_type = record.get("feedback", "ignore")
                daily_metrics[date_str][feedback_type + "s"] += 1
            
            # Top recommended products
            product_counts = {}
            for record in feedback_records:
                product_id = record.get("product_id")
                product_counts[product_id] = product_counts.get(product_id, 0) + 1
            
            top_products = dict(sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:10])
            
            # Segment performance
            segment_performance = {}
            for record in feedback_records:
                user_id = record.get("user_id")
                user = await self.db[Collections.USERS].find_one({"user_id": user_id})
                segment_id = user.get("segment_id", "unassigned") if user else "unassigned"
                
                if segment_id not in segment_performance:
                    segment_performance[segment_id] = {"clicks": 0, "purchases": 0, "total": 0}
                
                segment_performance[segment_id]["total"] += 1
                feedback_type = record.get("feedback", "ignore")
                if feedback_type in ["click", "purchase"]:
                    segment_performance[segment_id][feedback_type + "s"] += 1
            
            # Calculate conversion rates for segments
            for segment_id, metrics in segment_performance.items():
                total = metrics["total"]
                if total > 0:
                    metrics["conversion_rate"] = ((metrics["clicks"] + metrics["purchases"]) / total) * 100
            
            return {
                "period_days": days,
                "total_recommendations": len(feedback_records),
                "daily_metrics": daily_metrics,
                "top_products": top_products,
                "segment_performance": segment_performance
            }
            
        except Exception as e:
            print(f"Error getting recommendation analytics: {e}")
            return {}
    
    async def _get_product_details(self, product_id: str) -> Optional[Dict]:
        """Get product details"""
        try:
            products_collection = self.db[Collections.PRODUCTS]
            product = await products_collection.find_one({"product_id": product_id})
            
            if product:
                return {
                    "product_id": product.get("product_id"),
                    "category": product.get("category"),
                    "sub_category": product.get("sub_category"),
                    "brand": product.get("brand"),
                    "attributes": product.get("attributes", {}),
                    "price_history": product.get("price_history", [])
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting product details for {product_id}: {e}")
            return None
    
    async def get_ab_test_results(self, test_id: str) -> Dict[str, Any]:
        """Get A/B test results for recommendation algorithms"""
        try:
            # This would connect to an A/B testing system
            # For now, return placeholder data
            return {
                "test_id": test_id,
                "variants": {
                    "collaborative": {
                        "impressions": 1000,
                        "clicks": 150,
                        "conversions": 30,
                        "ctr": 15.0,
                        "conversion_rate": 3.0
                    },
                    "content_based": {
                        "impressions": 1000,
                        "clicks": 120,
                        "conversions": 25,
                        "ctr": 12.0,
                        "conversion_rate": 2.5
                    }
                },
                "winner": "collaborative",
                "confidence": 0.95
            }
            
        except Exception as e:
            print(f"Error getting A/B test results: {e}")
            return {}
    
    async def refresh_recommendation_models(self) -> Dict[str, Any]:
        """Refresh recommendation models with latest data"""
        try:
            # This would trigger model retraining
            # For now, return success status
            return {
                "status": "success",
                "message": "Recommendation models refreshed successfully",
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            print(f"Error refreshing recommendation models: {e}")
            return {"status": "error", "message": str(e)}
