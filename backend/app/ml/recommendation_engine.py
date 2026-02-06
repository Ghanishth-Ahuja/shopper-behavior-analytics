from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os
from datetime import datetime, timedelta
from app.feature_pipeline.feature_pipeline import FeaturePipeline
from app.database.mongodb import MongoDB, Collections
from app.models.product import Product
from app.models.user import User


class RecommendationEngine:
    """Hybrid recommendation engine combining collaborative filtering, content-based, and segment-based recommendations"""
    
    def __init__(self, model_path: str = "models/recommendations/"):
        self.model_path = model_path
        self.feature_pipeline = FeaturePipeline()
        self.db = MongoDB.get_database()
        
        # Model components
        self.user_item_matrix = None
        self.item_features = None
        self.user_profiles = None
        
        # Ensure model directory exists
        os.makedirs(model_path, exist_ok=True)
    
    async def get_user_recommendations(
        self,
        user_id: str,
        limit: int = 10,
        category: Optional[str] = None,
        price_range: Optional[str] = None
    ) -> List[Dict]:
        """Get personalized recommendations for a user"""
        try:
            # Get user features and segment
            user_features = await self.feature_pipeline.get_user_features(user_id)
            if not user_features:
                return await self._get_popular_products(limit, category)
            
            user = await self.db[Collections.USERS].find_one({"user_id": user_id})
            segment_id = user.get('segment_id') if user else None
            
            # Get different recommendation types
            collaborative_scores = await self._get_collaborative_recommendations(user_id, limit * 2)
            content_scores = await self._get_content_based_recommendations(user_id, limit * 2)
            segment_scores = await self._get_segment_recommendations(segment_id, limit * 2) if segment_id else []
            
            # Combine scores with weights
            combined_scores = await self._combine_recommendation_scores(
                collaborative_scores,
                content_scores,
                segment_scores,
                user_features
            )
            
            # Apply filters
            if category:
                combined_scores = await self._filter_by_category(combined_scores, category)
            
            if price_range:
                combined_scores = await self._filter_by_price_range(combined_scores, price_range)
            
            # Sort and return top recommendations
            combined_scores.sort(key=lambda x: x['score'], reverse=True)
            
            return combined_scores[:limit]
            
        except Exception as e:
            print(f"Error getting recommendations for user {user_id}: {e}")
            return await self._get_popular_products(limit, category)
    
    async def get_segment_recommendations(
        self,
        segment_id: str,
        limit: int = 10,
        category: Optional[str] = None
    ) -> List[Dict]:
        """Get recommendations for a user segment"""
        try:
            # Get segment information
            segment = await self.db[Collections.SEGMENTS].find_one({"segment_id": segment_id})
            if not segment:
                return []
            
            # Get top categories for segment
            segment_categories = segment.get('top_categories', [])
            
            # Get popular products in segment's preferred categories
            recommendations = []
            
            for cat in segment_categories[:3]:  # Top 3 categories
                cat_products = await self._get_popular_products_by_category(cat, limit // 3)
                recommendations.extend(cat_products)
            
            # Remove duplicates and sort
            seen = set()
            unique_recommendations = []
            for rec in recommendations:
                if rec['product_id'] not in seen:
                    seen.add(rec['product_id'])
                    unique_recommendations.append(rec)
            
            unique_recommendations.sort(key=lambda x: x['score'], reverse=True)
            
            return unique_recommendations[:limit]
            
        except Exception as e:
            print(f"Error getting segment recommendations for {segment_id}: {e}")
            return []
    
    async def get_similar_products(self, product_id: str, limit: int = 10) -> List[Dict]:
        """Get products similar to a given product"""
        try:
            # Get target product
            target_product = await self.db[Collections.PRODUCTS].find_one({"product_id": product_id})
            if not target_product:
                return []
            
            # Get all products
            products_collection = self.db[Collections.PRODUCTS]
            cursor = products_collection.find({})
            all_products = await cursor.to_list(length=None)
            
            # Calculate similarities
            similarities = []
            for product in all_products:
                if product['product_id'] == product_id:
                    continue
                
                similarity = await self._calculate_product_similarity(target_product, product)
                similarities.append({
                    "product_id": product['product_id'],
                    "score": similarity,
                    "reason": f"Similar to {target_product.get('name', product_id)}"
                })
            
            # Sort and return top similar products
            similarities.sort(key=lambda x: x['score'], reverse=True)
            return similarities[:limit]
            
        except Exception as e:
            print(f"Error getting similar products for {product_id}: {e}")
            return []
    
    async def get_frequently_bought_together(self, product_id: str, limit: int = 5) -> List[Dict]:
        """Get products frequently bought together with the given product"""
        try:
            # Find transactions containing this product
            transactions_collection = self.db[Collections.TRANSACTIONS]
            cursor = transactions_collection.find({"items.product_id": product_id})
            transactions = await cursor.to_list(length=None)
            
            # Count co-purchased products
            co_purchase_counts = {}
            
            for transaction in transactions:
                items = transaction.get('items', [])
                for item in items:
                    other_product_id = item.get('product_id')
                    if other_product_id != product_id:
                        co_purchase_counts[other_product_id] = co_purchase_counts.get(other_product_id, 0) + 1
            
            # Convert to recommendations
            recommendations = []
            total_transactions = len(transactions)
            
            for other_product_id, count in co_purchase_counts.items():
                confidence = count / total_transactions if total_transactions > 0 else 0
                recommendations.append({
                    "product_id": other_product_id,
                    "score": confidence,
                    "reason": f"Frequently bought together with {product_id}"
                })
            
            # Sort and return top recommendations
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            print(f"Error getting frequently bought together for {product_id}: {e}")
            return []
    
    async def get_trending_products(self, limit: int = 10, category: Optional[str] = None) -> List[Dict]:
        """Get trending products based on recent activity"""
        try:
            # Get recent transactions (last 7 days)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            
            query = {"timestamp": {"$gte": seven_days_ago}}
            if category:
                # Need to join with products to filter by category
                pass
            
            transactions_collection = self.db[Collections.TRANSACTIONS]
            cursor = transactions_collection.find(query)
            recent_transactions = await cursor.to_list(length=None)
            
            # Count product purchases
            product_counts = {}
            
            for transaction in recent_transactions:
                items = transaction.get('items', [])
                for item in items:
                    product_id = item.get('product_id')
                    product_counts[product_id] = product_counts.get(product_id, 0) + 1
            
            # Convert to recommendations
            recommendations = []
            total_purchases = sum(product_counts.values())
            
            for product_id, count in product_counts.items():
                trend_score = count / total_purchases if total_purchases > 0 else 0
                recommendations.append({
                    "product_id": product_id,
                    "score": trend_score,
                    "reason": "Trending product"
                })
            
            # Sort and return top recommendations
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            print(f"Error getting trending products: {e}")
            return []
    
    async def explain_recommendation(self, user_id: str, product_id: str) -> Dict:
        """Explain why a product is recommended to a user"""
        try:
            explanation = {
                "user_id": user_id,
                "product_id": product_id,
                "factors": []
            }
            
            # Get user features
            user_features = await self.feature_pipeline.get_user_features(user_id)
            if not user_features:
                return explanation
            
            # Check category affinity
            product = await self.db[Collections.PRODUCTS].find_one({"product_id": product_id})
            if product:
                product_category = product.get('category')
                for ca in user_features.category_affinity_vector:
                    if ca.category == product_category and ca.affinity_score > 0.1:
                        explanation["factors"].append({
                            "type": "category_affinity",
                            "description": f"You frequently purchase from {product_category}",
                            "weight": ca.affinity_score
                        })
            
            # Check collaborative filtering
            similar_users = await self._find_similar_users(user_id, 5)
            if similar_users:
                explanation["factors"].append({
                    "type": "collaborative",
                    "description": f"Users similar to you also bought this product",
                    "weight": 0.3
                })
            
            # Check segment preferences
            user = await self.db[Collections.USERS].find_one({"user_id": user_id})
            segment_id = user.get('segment_id') if user else None
            
            if segment_id:
                segment = await self.db[Collections.SEGMENTS].find_one({"segment_id": segment_id})
                if segment and product_category in segment.get('top_categories', []):
                    explanation["factors"].append({
                        "type": "segment_preference",
                        "description": f"Popular in your segment: {segment.get('segment_name')}",
                        "weight": 0.2
                    })
            
            return explanation
            
        except Exception as e:
            print(f"Error explaining recommendation: {e}")
            return {"user_id": user_id, "product_id": product_id, "factors": []}
    
    async def record_feedback(self, user_id: str, product_id: str, feedback: str, position: int) -> None:
        """Record recommendation feedback for model improvement"""
        try:
            feedback_data = {
                "user_id": user_id,
                "product_id": product_id,
                "feedback": feedback,  # "click", "purchase", "ignore"
                "position": position,
                "timestamp": datetime.utcnow()
            }
            
            # Store feedback for later model retraining
            feedback_collection = self.db.get_collection("recommendation_feedback")
            await feedback_collection.insert_one(feedback_data)
            
        except Exception as e:
            print(f"Error recording feedback: {e}")
    
    async def _get_collaborative_recommendations(self, user_id: str, limit: int) -> List[Dict]:
        """Get collaborative filtering recommendations"""
        try:
            # Find similar users
            similar_users = await self._find_similar_users(user_id, 10)
            
            if not similar_users:
                return []
            
            # Get products purchased by similar users
            recommendations = {}
            
            for similar_user_id, similarity in similar_users:
                transactions_collection = self.db[Collections.TRANSACTIONS]
                cursor = transactions_collection.find({"user_id": similar_user_id})
                transactions = await cursor.to_list(length=None)
                
                for transaction in transactions:
                    items = transaction.get('items', [])
                    for item in items:
                        product_id = item.get('product_id')
                        if product_id not in recommendations:
                            recommendations[product_id] = 0
                        recommendations[product_id] += similarity
            
            # Convert to recommendation format
            result = []
            for product_id, score in recommendations.items():
                result.append({
                    "product_id": product_id,
                    "score": score,
                    "reason": "Users like you also bought this"
                })
            
            result.sort(key=lambda x: x['score'], reverse=True)
            return result[:limit]
            
        except Exception as e:
            print(f"Error getting collaborative recommendations: {e}")
            return []
    
    async def _get_content_based_recommendations(self, user_id: str, limit: int) -> List[Dict]:
        """Get content-based recommendations"""
        try:
            user_features = await self.feature_pipeline.get_user_features(user_id)
            if not user_features:
                return []
            
            # Get user's preferred categories
            preferred_categories = [ca.category for ca in user_features.category_affinity_vector[:5]]
            
            # Get products in preferred categories
            recommendations = []
            
            for category in preferred_categories:
                products_collection = self.db[Collections.PRODUCTS]
                cursor = products_collection.find({"category": category})
                products = await cursor.to_list(length=None)
                
                for product in products:
                    # Calculate content similarity based on category affinity
                    category_affinity = next(
                        (ca.affinity_score for ca in user_features.category_affinity_vector 
                         if ca.category == category), 0
                    )
                    
                    recommendations.append({
                        "product_id": product['product_id'],
                        "score": category_affinity,
                        "reason": f"Based on your interest in {category}"
                    })
            
            # Sort and return top recommendations
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            print(f"Error getting content-based recommendations: {e}")
            return []
    
    async def _get_segment_recommendations(self, segment_id: str, limit: int) -> List[Dict]:
        """Get segment-based recommendations"""
        try:
            segment = await self.db[Collections.SEGMENTS].find_one({"segment_id": segment_id})
            if not segment:
                return []
            
            # Get popular products in segment's top categories
            recommendations = []
            top_categories = segment.get('top_categories', [])
            
            for category in top_categories:
                category_products = await self._get_popular_products_by_category(category, limit // len(top_categories))
                recommendations.extend(category_products)
            
            return recommendations[:limit]
            
        except Exception as e:
            print(f"Error getting segment recommendations: {e}")
            return []
    
    async def _combine_recommendation_scores(
        self,
        collaborative_scores: List[Dict],
        content_scores: List[Dict],
        segment_scores: List[Dict],
        user_features
    ) -> List[Dict]:
        """Combine different recommendation types with weights"""
        try:
            combined_scores = {}
            
            # Weight different recommendation types
            weights = {
                "collaborative": 0.4,
                "content": 0.4,
                "segment": 0.2
            }
            
            # Add collaborative scores
            for rec in collaborative_scores:
                product_id = rec['product_id']
                combined_scores[product_id] = rec['score'] * weights['collaborative']
            
            # Add content scores
            for rec in content_scores:
                product_id = rec['product_id']
                if product_id in combined_scores:
                    combined_scores[product_id] += rec['score'] * weights['content']
                else:
                    combined_scores[product_id] = rec['score'] * weights['content']
            
            # Add segment scores
            for rec in segment_scores:
                product_id = rec['product_id']
                if product_id in combined_scores:
                    combined_scores[product_id] += rec['score'] * weights['segment']
                else:
                    combined_scores[product_id] = rec['score'] * weights['segment']
            
            # Convert back to recommendation format
            result = []
            for product_id, score in combined_scores.items():
                result.append({
                    "product_id": product_id,
                    "score": score,
                    "reason": "Personalized recommendation"
                })
            
            return result
            
        except Exception as e:
            print(f"Error combining recommendation scores: {e}")
            return []
    
    async def _find_similar_users(self, user_id: str, limit: int) -> List[Tuple[str, float]]:
        """Find users similar to the given user"""
        try:
            # Get target user features
            target_features = await self.feature_pipeline.get_user_features(user_id)
            if not target_features:
                return []
            
            target_vector = np.array(self.feature_pipeline._features_to_vector(target_features))
            
            # Get all other users
            users_collection = self.db[Collections.USERS]
            cursor = users_collection.find({"user_id": {"$ne": user_id}})
            users = await cursor.to_list(length=None)
            
            similarities = []
            
            for user in users[:100]:  # Limit to 100 users for performance
                other_user_id = user['user_id']
                other_features = await self.feature_pipeline.get_user_features(other_user_id)
                
                if other_features:
                    other_vector = np.array(self.feature_pipeline._features_to_vector(other_features))
                    
                    # Calculate cosine similarity
                    similarity = cosine_similarity(
                        target_vector.reshape(1, -1),
                        other_vector.reshape(1, -1)
                    )[0][0]
                    
                    similarities.append((other_user_id, float(similarity)))
            
            # Sort by similarity and return top users
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:limit]
            
        except Exception as e:
            print(f"Error finding similar users: {e}")
            return []
    
    async def _calculate_product_similarity(self, product1: Dict, product2: Dict) -> float:
        """Calculate similarity between two products"""
        try:
            similarity = 0.0
            
            # Category similarity
            if product1.get('category') == product2.get('category'):
                similarity += 0.4
            
            # Brand similarity
            if product1.get('brand') == product2.get('brand'):
                similarity += 0.3
            
            # Price similarity (within 20%)
            price1 = product1.get('price_history', [{}])[-1].get('price', 0)
            price2 = product2.get('price_history', [{}])[-1].get('price', 0)
            
            if price1 > 0 and price2 > 0:
                price_diff = abs(price1 - price2) / max(price1, price2)
                if price_diff < 0.2:
                    similarity += 0.3
            
            return similarity
            
        except Exception as e:
            print(f"Error calculating product similarity: {e}")
            return 0.0
    
    async def _get_popular_products(self, limit: int, category: Optional[str] = None) -> List[Dict]:
        """Get popular products as fallback"""
        try:
            products_collection = self.db[Collections.PRODUCTS]
            
            query = {}
            if category:
                query["category"] = category
            
            cursor = products_collection.find(query).limit(limit)
            products = await cursor.to_list(length=None)
            
            return [
                {
                    "product_id": product['product_id'],
                    "score": 0.5,  # Default score for popular products
                    "reason": "Popular product"
                }
                for product in products
            ]
            
        except Exception as e:
            print(f"Error getting popular products: {e}")
            return []
    
    async def _get_popular_products_by_category(self, category: str, limit: int) -> List[Dict]:
        """Get popular products in a specific category"""
        try:
            products_collection = self.db[Collections.PRODUCTS]
            cursor = products_collection.find({"category": category}).limit(limit)
            products = await cursor.to_list(length=None)
            
            return [
                {
                    "product_id": product['product_id'],
                    "score": 0.6,
                    "reason": f"Popular in {category}"
                }
                for product in products
            ]
            
        except Exception as e:
            print(f"Error getting popular products by category: {e}")
            return []
    
    async def _filter_by_category(self, recommendations: List[Dict], category: str) -> List[Dict]:
        """Filter recommendations by category"""
        try:
            filtered = []
            
            for rec in recommendations:
                product = await self.db[Collections.PRODUCTS].find_one({"product_id": rec['product_id']})
                if product and product.get('category') == category:
                    filtered.append(rec)
            
            return filtered
            
        except Exception as e:
            print(f"Error filtering by category: {e}")
            return recommendations
    
    async def _filter_by_price_range(self, recommendations: List[Dict], price_range: str) -> List[Dict]:
        """Filter recommendations by price range"""
        try:
            # Parse price range (e.g., "0-50", "50-100", "100+")
            if price_range.endswith('+'):
                min_price = float(price_range[:-1])
                max_price = float('inf')
            else:
                parts = price_range.split('-')
                if len(parts) == 2:
                    min_price = float(parts[0])
                    max_price = float(parts[1])
                else:
                    return recommendations
            
            filtered = []
            
            for rec in recommendations:
                product = await self.db[Collections.PRODUCTS].find_one({"product_id": rec['product_id']})
                if product:
                    price_history = product.get('price_history', [])
                    if price_history:
                        current_price = price_history[-1].get('price', 0)
                        if min_price <= current_price <= max_price:
                            filtered.append(rec)
            
            return filtered
            
        except Exception as e:
            print(f"Error filtering by price range: {e}")
            return recommendations
