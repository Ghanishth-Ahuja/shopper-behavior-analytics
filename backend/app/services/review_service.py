from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.review import Review, ReviewCreate, ReviewUpdate, ReviewAnalysis
from app.database.mongodb import MongoDB, Collections
from app.ml.nlp_analyzer import NLPAnalyzer
from bson import ObjectId


class ReviewService:
    """Service for review management operations"""
    
    def __init__(self):
        self.db = MongoDB.get_database()
        self.nlp_analyzer = NLPAnalyzer()
    
    async def create_review(self, review_data: ReviewCreate) -> Review:
        """Create a new review"""
        try:
            reviews_collection = self.db[Collections.REVIEWS]
            
            # Check if review already exists
            existing_review = await reviews_collection.find_one({"review_id": review_data.review_id})
            if existing_review:
                raise ValueError(f"Review with ID {review_data.review_id} already exists")
            
            # Create review document
            review_dict = review_data.dict()
            review_dict["_id"] = ObjectId()
            review_dict["created_at"] = datetime.utcnow()
            review_dict["updated_at"] = datetime.utcnow()
            
            # Perform NLP analysis
            analysis = await self.nlp_analyzer.analyze_review(review_data.review_text)
            review_dict["sentiment_score"] = analysis.sentiment_score
            review_dict["extracted_aspects"] = analysis.aspects
            
            # Insert review
            result = await reviews_collection.insert_one(review_dict)
            
            # Get created review
            created_review = await reviews_collection.find_one({"_id": result.inserted_id})
            
            return Review(**created_review)
            
        except Exception as e:
            print(f"Error creating review: {e}")
            raise
    
    async def get_review(self, review_id: str) -> Optional[Review]:
        """Get review by ID"""
        try:
            reviews_collection = self.db[Collections.REVIEWS]
            review_doc = await reviews_collection.find_one({"review_id": review_id})
            
            if review_doc:
                return Review(**review_doc)
            return None
            
        except Exception as e:
            print(f"Error getting review {review_id}: {e}")
            return None
    
    async def update_review(self, review_id: str, review_update: ReviewUpdate) -> Optional[Review]:
        """Update review information"""
        try:
            reviews_collection = self.db[Collections.REVIEWS]
            
            # Prepare update data
            update_data = review_update.dict(exclude_unset=True)
            if not update_data:
                return await self.get_review(review_id)
            
            update_data["updated_at"] = datetime.utcnow()
            
            # If review text is updated, re-analyze sentiment
            if "review_text" in update_data:
                analysis = await self.nlp_analyzer.analyze_review(update_data["review_text"])
                update_data["sentiment_score"] = analysis.sentiment_score
                update_data["extracted_aspects"] = analysis.aspects
            
            # Update review
            result = await reviews_collection.update_one(
                {"review_id": review_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_review(review_id)
            
            return None
            
        except Exception as e:
            print(f"Error updating review {review_id}: {e}")
            return None
    
    async def delete_review(self, review_id: str) -> bool:
        """Delete a review"""
        try:
            reviews_collection = self.db[Collections.REVIEWS]
            result = await reviews_collection.delete_one({"review_id": review_id})
            
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Error deleting review {review_id}: {e}")
            return False
    
    async def get_product_reviews(self, product_id: str, skip: int = 0, limit: int = 100) -> List[Review]:
        """Get all reviews for a product"""
        try:
            reviews_collection = self.db[Collections.REVIEWS]
            cursor = reviews_collection.find({"product_id": product_id}).skip(skip).limit(limit)
            reviews = await cursor.to_list(length=None)
            
            return [Review(**review) for review in reviews]
            
        except Exception as e:
            print(f"Error getting product reviews for {product_id}: {e}")
            return []
    
    async def get_reviews(self, skip: int = 0, limit: int = 100) -> List[Review]:
        """Get all reviews with pagination"""
        try:
            reviews_collection = self.db[Collections.REVIEWS]
            cursor = reviews_collection.find().skip(skip).limit(limit)
            reviews = await cursor.to_list(length=None)
            
            return [Review(**review) for review in reviews]
            
        except Exception as e:
            print(f"Error getting reviews: {e}")
            return []
    
    async def analyze_review(self, review_id: str) -> Optional[ReviewAnalysis]:
        """Analyze review sentiment and aspects"""
        try:
            review = await self.get_review(review_id)
            if not review:
                return None
            
            analysis = await self.nlp_analyzer.analyze_review(review.review_text)
            analysis.review_id = review_id
            
            # Update review with analysis results
            reviews_collection = self.db[Collections.REVIEWS]
            await reviews_collection.update_one(
                {"review_id": review_id},
                {
                    "$set": {
                        "sentiment_score": analysis.sentiment_score,
                        "extracted_aspects": analysis.aspects
                    }
                }
            )
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing review {review_id}: {e}")
            return None
    
    async def get_product_insights(self, product_id: str) -> Dict[str, Any]:
        """Get aggregated insights for a product"""
        try:
            insights = await self.nlp_analyzer.analyze_product_reviews(product_id)
            
            # Add additional metrics
            reviews_collection = self.db[Collections.REVIEWS]
            cursor = reviews_collection.find({"product_id": product_id})
            reviews = await cursor.to_list(length=None)
            
            if not reviews:
                return {"product_id": product_id, "message": "No reviews found"}
            
            # Rating distribution
            rating_counts = {}
            for review in reviews:
                rating = review.get("rating", 0)
                rating_counts[rating] = rating_counts.get(rating, 0) + 1
            
            # Verified purchase analysis
            verified_count = sum(1 for review in reviews if review.get("verified_purchase", False))
            
            # Helpfulness analysis
            helpful_votes = [review.get("helpful_count", 0) for review in reviews]
            avg_helpful = sum(helpful_votes) / len(helpful_votes) if helpful_votes else 0
            
            insights.update({
                "rating_distribution": rating_counts,
                "verified_purchase_percentage": (verified_count / len(reviews)) * 100,
                "avg_helpful_votes": avg_helpful
            })
            
            return insights
            
        except Exception as e:
            print(f"Error getting product insights for {product_id}: {e}")
            return {"error": str(e)}
    
    async def get_review_trends(self, product_id: str, days: int = 30) -> Dict[str, Any]:
        """Get review trends over time"""
        try:
            reviews_collection = self.db[Collections.REVIEWS]
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            cursor = reviews_collection.find({
                "product_id": product_id,
                "timestamp": {"$gte": start_date, "$lte": end_date}
            })
            reviews = await cursor.to_list(length=None)
            
            if not reviews:
                return {"product_id": product_id, "period_days": days, "message": "No reviews in period"}
            
            # Group by day
            daily_reviews = {}
            daily_sentiments = {}
            daily_ratings = {}
            
            for review in reviews:
                date = review.get("timestamp", datetime.utcnow()).date()
                
                # Count reviews
                daily_reviews[str(date)] = daily_reviews.get(str(date), 0) + 1
                
                # Average sentiment
                sentiment = review.get("sentiment_score", 0)
                if str(date) not in daily_sentiments:
                    daily_sentiments[str(date)] = []
                daily_sentiments[str(date)].append(sentiment)
                
                # Average rating
                rating = review.get("rating", 0)
                if str(date) not in daily_ratings:
                    daily_ratings[str(date)] = []
                daily_ratings[str(date)].append(rating)
            
            # Calculate averages
            trends = {}
            for date in daily_reviews:
                trends[date] = {
                    "review_count": daily_reviews[date],
                    "avg_sentiment": sum(daily_sentiments[date]) / len(daily_sentiments[date]) if daily_sentiments[date] else 0,
                    "avg_rating": sum(daily_ratings[date]) / len(daily_ratings[date]) if daily_ratings[date] else 0
                }
            
            return {
                "product_id": product_id,
                "period_days": days,
                "daily_trends": trends
            }
            
        except Exception as e:
            print(f"Error getting review trends for {product_id}: {e}")
            return {"error": str(e)}
    
    async def get_top_reviewed_products(self, limit: int = 10, min_reviews: int = 10) -> List[Dict]:
        """Get products with highest ratings"""
        try:
            reviews_collection = self.db[Collections.REVIEWS]
            
            # Aggregate reviews by product
            pipeline = [
                {"$group": {
                    "_id": "$product_id",
                    "avg_rating": {"$avg": "$rating"},
                    "total_reviews": {"$sum": 1},
                    "avg_sentiment": {"$avg": "$sentiment_score"}
                }},
                {"$match": {"total_reviews": {"$gte": min_reviews}}},
                {"$sort": {"avg_rating": -1}},
                {"$limit": limit}
            ]
            
            cursor = reviews_collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            # Get product details
            top_products = []
            for result in results:
                product_id = result["_id"]
                
                # Get product info
                products_collection = self.db[Collections.PRODUCTS]
                product = await products_collection.find_one({"product_id": product_id})
                
                if product:
                    top_products.append({
                        "product_id": product_id,
                        "product_info": {
                            "category": product.get("category"),
                            "brand": product.get("brand"),
                            "sub_category": product.get("sub_category")
                        },
                        "metrics": {
                            "avg_rating": result["avg_rating"],
                            "total_reviews": result["total_reviews"],
                            "avg_sentiment": result["avg_sentiment"]
                        }
                    })
            
            return top_products
            
        except Exception as e:
            print(f"Error getting top reviewed products: {e}")
            return []
    
    async def search_reviews(self, query: str, skip: int = 0, limit: int = 100) -> List[Review]:
        """Search reviews by text content"""
        try:
            reviews_collection = self.db[Collections.REVIEWS]
            
            # Create search filter
            search_filter = {
                "$or": [
                    {"review_text": {"$regex": query, "$options": "i"}},
                    {"review_id": {"$regex": query, "$options": "i"}}
                ]
            }
            
            cursor = reviews_collection.find(search_filter).skip(skip).limit(limit)
            reviews = await cursor.to_list(length=None)
            
            return [Review(**review) for review in reviews]
            
        except Exception as e:
            print(f"Error searching reviews: {e}")
            return []
    
    async def get_sentiment_summary(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get overall sentiment summary"""
        try:
            reviews_collection = self.db[Collections.REVIEWS]
            
            # Build filter
            filter_dict = {}
            if category:
                # Need to join with products to filter by category
                pipeline = [
                    {"$lookup": {
                        "from": "products",
                        "localField": "product_id",
                        "foreignField": "product_id",
                        "as": "product_info"
                    }},
                    {"$unwind": "$product_info"},
                    {"$match": {"product_info.category": category}},
                    {"$group": {
                        "_id": None,
                        "total_reviews": {"$sum": 1},
                        "avg_rating": {"$avg": "$rating"},
                        "avg_sentiment": {"$avg": "$sentiment_score"},
                        "positive_reviews": {
                            "$sum": {"$cond": [{"$gte": ["$sentiment_score", 0.05]}, 1, 0]}
                        },
                        "negative_reviews": {
                            "$sum": {"$cond": [{"$lte": ["$sentiment_score", -0.05]}, 1, 0]}
                        },
                        "neutral_reviews": {
                            "$sum": {"$cond": [
                                {"$and": [{"$gt": ["$sentiment_score", -0.05]}, {"$lt": ["$sentiment_score", 0.05]}]},
                                1, 0
                            ]}
                        }
                    }}
                ]
            else:
                pipeline = [
                    {"$group": {
                        "_id": None,
                        "total_reviews": {"$sum": 1},
                        "avg_rating": {"$avg": "$rating"},
                        "avg_sentiment": {"$avg": "$sentiment_score"},
                        "positive_reviews": {
                            "$sum": {"$cond": [{"$gte": ["$sentiment_score", 0.05]}, 1, 0]}
                        },
                        "negative_reviews": {
                            "$sum": {"$cond": [{"$lte": ["$sentiment_score", -0.05]}, 1, 0]}
                        },
                        "neutral_reviews": {
                            "$sum": {"$cond": [
                                {"$and": [{"$gt": ["$sentiment_score", -0.05]}, {"$lt": ["$sentiment_score", 0.05]}]},
                                1, 0
                            ]}
                        }
                    }}
                ]
            
            cursor = reviews_collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            if results:
                result = results[0]
                total_reviews = result["total_reviews"]
                
                return {
                    "category": category,
                    "total_reviews": total_reviews,
                    "avg_rating": result["avg_rating"],
                    "avg_sentiment": result["avg_sentiment"],
                    "sentiment_distribution": {
                        "positive": result["positive_reviews"],
                        "negative": result["negative_reviews"],
                        "neutral": result["neutral_reviews"],
                        "positive_percentage": (result["positive_reviews"] / total_reviews) * 100,
                        "negative_percentage": (result["negative_reviews"] / total_reviews) * 100,
                        "neutral_percentage": (result["neutral_reviews"] / total_reviews) * 100
                    }
                }
            
            return {"category": category, "message": "No reviews found"}
            
        except Exception as e:
            print(f"Error getting sentiment summary: {e}")
            return {"error": str(e)}
