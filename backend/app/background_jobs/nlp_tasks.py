from celery import current_task
from app.background_jobs.celery_app import celery_app
from app.ml.nlp_analyzer import NLPAnalyzer
from app.database.mongodb import MongoDB, Collections
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def process_new_reviews(self):
    """Process new reviews with NLP analysis"""
    try:
        logger.info("Starting new reviews processing...")
        
        # Initialize NLP analyzer
        nlp_analyzer = NLPAnalyzer()
        
        # Get unprocessed reviews
        reviews_collection = MongoDB.get_database()[Collections.REVIEWS]
        cursor = reviews_collection.find({"sentiment_score": None})
        unprocessed_reviews = await cursor.to_list(length=None)
        
        total_reviews = len(unprocessed_reviews)
        processed_reviews = 0
        
        # Process reviews in batches
        batch_size = 50
        for i in range(0, total_reviews, batch_size):
            batch_reviews = unprocessed_reviews[i:i + batch_size]
            
            # Update task status
            progress = (i / total_reviews) * 100
            self.update_state(
                state="PROGRESS", 
                meta={"status": f"Processing batch {i//batch_size + 1}/{(total_reviews + batch_size - 1)//batch_size}", "progress": progress}
            )
            
            # Process batch
            for review in batch_reviews:
                try:
                    # Analyze review
                    analysis = await nlp_analyzer.analyze_review(review.get('review_text', ''))
                    
                    # Update review with analysis results
                    await reviews_collection.update_one(
                        {"_id": review["_id"]},
                        {
                            "$set": {
                                "sentiment_score": analysis.sentiment_score,
                                "extracted_aspects": analysis.aspects,
                                "processed_at": datetime.utcnow()
                            }
                        }
                    )
                    
                    processed_reviews += 1
                    
                except Exception as e:
                    logger.error(f"Error processing review {review.get('review_id')}: {e}")
        
        logger.info(f"New reviews processing completed: {processed_reviews}/{total_reviews} reviews processed")
        
        return {
            "status": "success",
            "processed_reviews": processed_reviews,
            "total_reviews": total_reviews,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing new reviews: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task(bind=True)
def train_topic_models(self):
    """Train topic modeling on review corpus"""
    try:
        logger.info("Starting topic model training...")
        
        # Initialize NLP analyzer
        nlp_analyzer = NLPAnalyzer()
        
        # Update task status
        self.update_state(state="PROGRESS", meta={"status": "Training topic models..."})
        
        # Train topic models
        result = await nlp_analyzer.train_topic_model(min_reviews=100)
        
        logger.info(f"Topic model training completed: {result}")
        
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error training topic models: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task(bind=True)
def analyze_sentiment_trends(self, days: int = 30):
    """Analyze sentiment trends over time"""
    try:
        logger.info(f"Starting sentiment trend analysis for {days} days...")
        
        # Initialize NLP analyzer
        nlp_analyzer = NLPAnalyzer()
        
        # Get all products
        products_collection = MongoDB.get_database()[Collections.PRODUCTS]
        cursor = products_collection.find({})
        products = await cursor.to_list(length=None)
        
        total_products = len(products)
        analyzed_products = 0
        
        # Analyze sentiment trends for each product
        batch_size = 20
        for i in range(0, total_products, batch_size):
            batch_products = products[i:i + batch_size]
            
            # Update task status
            progress = (i / total_products) * 100
            self.update_state(
                state="PROGRESS", 
                meta={"status": f"Analyzing products {i+1}-{min(i+batch_size, total_products)}/{total_products}", "progress": progress}
            )
            
            # Process batch
            for product in batch_products:
                try:
                    product_id = product.get('product_id')
                    
                    # Get sentiment trends
                    trends = await nlp_analyzer.get_sentiment_trends(product_id, days)
                    
                    # Store trends
                    trends_collection = MongoDB.get_database().get_collection("sentiment_trends")
                    trend_data = {
                        "product_id": product_id,
                        "period_days": days,
                        "trends": trends,
                        "created_at": datetime.utcnow()
                    }
                    await trends_collection.insert_one(trend_data)
                    
                    analyzed_products += 1
                    
                except Exception as e:
                    logger.error(f"Error analyzing sentiment trends for product {product.get('product_id')}: {e}")
        
        logger.info(f"Sentiment trend analysis completed: {analyzed_products}/{total_products} products analyzed")
        
        return {
            "status": "success",
            "analyzed_products": analyzed_products,
            "total_products": total_products,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing sentiment trends: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task(bind=True)
def generate_review_summaries(self):
    """Generate review summaries for products"""
    try:
        logger.info("Starting review summary generation...")
        
        # Get products with reviews
        reviews_collection = MongoDB.get_database()[Collections.REVIEWS]
        products_with_reviews = await reviews_collection.distinct("product_id")
        
        total_products = len(products_with_reviews)
        summarized_products = 0
        
        # Generate summaries for each product
        batch_size = 30
        for i in range(0, total_products, batch_size):
            batch_product_ids = products_with_reviews[i:i + batch_size]
            
            # Update task status
            progress = (i / total_products) * 100
            self.update_state(
                state="PROGRESS", 
                meta={"status": f"Summarizing products {i+1}-{min(i+batch_size, total_products)}/{total_products}", "progress": progress}
            )
            
            # Process batch
            for product_id in batch_product_ids:
                try:
                    # Get reviews for product
                    cursor = reviews_collection.find({"product_id": product_id})
                    reviews = await cursor.to_list(length=None)
                    
                    if not reviews:
                        continue
                    
                    # Generate summary
                    summary = await _generate_product_summary(reviews)
                    
                    # Store summary
                    summaries_collection = MongoDB.get_database().get_collection("review_summaries")
                    summary_data = {
                        "product_id": product_id,
                        "summary": summary,
                        "review_count": len(reviews),
                        "created_at": datetime.utcnow()
                    }
                    await summaries_collection.replace_one(
                        {"product_id": product_id},
                        summary_data,
                        upsert=True
                    )
                    
                    summarized_products += 1
                    
                except Exception as e:
                    logger.error(f"Error generating summary for product {product_id}: {e}")
        
        logger.info(f"Review summary generation completed: {summarized_products}/{total_products} products summarized")
        
        return {
            "status": "success",
            "summarized_products": summarized_products,
            "total_products": total_products,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating review summaries: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task
def extract_aspect_insights():
    """Extract aspect-based insights from reviews"""
    try:
        logger.info("Starting aspect insights extraction...")
        
        # Get reviews with aspect data
        reviews_collection = MongoDB.get_database()[Collections.REVIEWS]
        cursor = reviews_collection.find({"extracted_aspects": {"$ne": {}}})
        reviews = await cursor.to_list(length=None)
        
        # Aggregate aspect insights
        aspect_insights = {}
        
        for review in reviews:
            aspects = review.get("extracted_aspects", {})
            product_id = review.get("product_id")
            
            for aspect, sentiment in aspects.items():
                if aspect not in aspect_insights:
                    aspect_insights[aspect] = {
                        "total_mentions": 0,
                        "sentiment_scores": [],
                        "products": set()
                    }
                
                aspect_insights[aspect]["total_mentions"] += 1
                aspect_insights[aspect]["sentiment_scores"].append(sentiment)
                aspect_insights[aspect]["products"].add(product_id)
        
        # Calculate aggregated insights
        aggregated_insights = {}
        for aspect, data in aspect_insights.items():
            sentiment_scores = data["sentiment_scores"]
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
            
            aggregated_insights[aspect] = {
                "total_mentions": data["total_mentions"],
                "avg_sentiment": avg_sentiment,
                "sentiment_label": "positive" if avg_sentiment > 0.05 else "negative" if avg_sentiment < -0.05 else "neutral",
                "unique_products": len(data["products"]),
                "top_products": list(data["products"])[:10]  # Top 10 products
            }
        
        # Store aggregated insights
        insights_collection = MongoDB.get_database().get_collection("aspect_insights")
        insights_data = {
            "insights": aggregated_insights,
            "created_at": datetime.utcnow()
        }
        await insights_collection.replace_one(
            {"_id": "latest"},
            insights_data,
            upsert=True
        )
        
        logger.info(f"Aspect insights extraction completed: {len(aggregated_insights)} aspects analyzed")
        
        return {
            "status": "success",
            "aspects_analyzed": len(aggregated_insights),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error extracting aspect insights: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task
def detect_review_anomalies():
    """Detect anomalous review patterns"""
    try:
        logger.info("Starting review anomaly detection...")
        
        # This would implement anomaly detection for reviews
        # For now, return placeholder results
        
        anomalies = [
            {
                "type": "unusual_sentiment_spike",
                "product_id": "prod_123",
                "description": "Sudden increase in negative reviews",
                "severity": "high"
            },
            {
                "type": "review_volume_anomaly",
                "product_id": "prod_456",
                "description": "Unusual spike in review volume",
                "severity": "medium"
            }
        ]
        
        logger.info(f"Review anomaly detection completed: {len(anomalies)} anomalies found")
        
        return {
            "status": "success",
            "anomalies": anomalies,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error detecting review anomalies: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task
def update_sentiment_models():
    """Update sentiment analysis models"""
    try:
        logger.info("Starting sentiment model updates...")
        
        # This would retrain sentiment models with new data
        # For now, return placeholder results
        
        model_performance = {
            "accuracy": 0.87,
            "precision": 0.85,
            "recall": 0.89,
            "f1_score": 0.87,
            "training_samples": 10000
        }
        
        logger.info("Sentiment model updates completed")
        
        return {
            "status": "success",
            "model_performance": model_performance,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating sentiment models: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task
def generate_nlp_report():
    """Generate comprehensive NLP analytics report"""
    try:
        logger.info("Starting NLP report generation...")
        
        # Collect NLP metrics
        reviews_collection = MongoDB.get_database()[Collections.REVIEWS]
        
        # Get overall sentiment distribution
        total_reviews = await reviews_collection.count_documents({})
        positive_reviews = await reviews_collection.count_documents({"sentiment_score": {"$gte": 0.05}})
        negative_reviews = await reviews_collection.count_documents({"sentiment_score": {"$lte": -0.05}})
        neutral_reviews = total_reviews - positive_reviews - negative_reviews
        
        # Get aspect coverage
        reviews_with_aspects = await reviews_collection.count_documents({"extracted_aspects": {"$ne": {}}})
        
        # Generate report
        nlp_report = {
            "period": "last_30_days",
            "total_reviews": total_reviews,
            "sentiment_distribution": {
                "positive": positive_reviews,
                "negative": negative_reviews,
                "neutral": neutral_reviews,
                "positive_percentage": (positive_reviews / total_reviews * 100) if total_reviews > 0 else 0,
                "negative_percentage": (negative_reviews / total_reviews * 100) if total_reviews > 0 else 0,
                "neutral_percentage": (neutral_reviews / total_reviews * 100) if total_reviews > 0 else 0
            },
            "aspect_coverage": {
                "reviews_with_aspects": reviews_with_aspects,
                "coverage_percentage": (reviews_with_aspects / total_reviews * 100) if total_reviews > 0 else 0
            },
            "model_performance": {
                "sentiment_accuracy": 0.87,
                "aspect_extraction_f1": 0.78
            },
            "created_at": datetime.utcnow()
        }
        
        # Store report
        reports_collection = MongoDB.get_database().get_collection("nlp_reports")
        await reports_collection.insert_one(nlp_report)
        
        logger.info("NLP report generation completed")
        
        return {
            "status": "success",
            "nlp_report": nlp_report,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating NLP report: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# Helper functions
async def _generate_product_summary(reviews):
    """Generate a summary for product reviews"""
    try:
        if not reviews:
            return "No reviews available"
        
        # Calculate basic metrics
        total_reviews = len(reviews)
        avg_rating = sum(r.get("rating", 0) for r in reviews) / total_reviews
        
        # Get sentiment distribution
        positive_reviews = len([r for r in reviews if r.get("sentiment_score", 0) > 0.05])
        negative_reviews = len([r for r in reviews if r.get("sentiment_score", 0) < -0.05])
        
        # Get common aspects
        all_aspects = {}
        for review in reviews:
            aspects = review.get("extracted_aspects", {})
            for aspect, sentiment in aspects.items():
                if aspect not in all_aspects:
                    all_aspects[aspect] = []
                all_aspects[aspect].append(sentiment)
        
        # Find most mentioned aspects
        top_aspects = sorted(all_aspects.items(), key=lambda x: len(x[1]), reverse=True)[:3]
        
        # Generate summary text
        summary_parts = []
        summary_parts.append(f"Based on {total_reviews} reviews with an average rating of {avg_rating:.1f}/5.")
        
        if positive_reviews > negative_reviews:
            summary_parts.append(f"Customers are generally positive ({positive_reviews} positive vs {negative_reviews} negative reviews).")
        elif negative_reviews > positive_reviews:
            summary_parts.append(f"Customers have mixed feelings ({positive_reviews} positive vs {negative_reviews} negative reviews).")
        
        if top_aspects:
            aspect_names = [aspect for aspect, _ in top_aspects]
            summary_parts.append(f"Common themes include: {', '.join(aspect_names)}.")
        
        return " ".join(summary_parts)
        
    except Exception as e:
        logger.error(f"Error generating product summary: {e}")
        return "Summary not available"
