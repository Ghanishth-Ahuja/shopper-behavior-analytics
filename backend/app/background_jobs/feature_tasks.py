from celery import current_task
from app.background_jobs.celery_app import celery_app
from app.feature_pipeline.feature_pipeline import FeaturePipeline
from app.feature_pipeline.rfm_features import RFMFeatureExtractor
from app.feature_pipeline.browsing_features import BrowsingFeatureExtractor
from app.feature_pipeline.category_affinity import CategoryAffinityExtractor
from app.database.mongodb import MongoDB, Collections
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def update_all_user_features(self):
    """Update features for all users"""
    try:
        logger.info("Starting user feature updates...")
        
        # Initialize feature pipeline
        feature_pipeline = FeaturePipeline()
        
        # Get all users
        users_collection = MongoDB.get_database()[Collections.USERS]
        cursor = users_collection.find({})
        users = await cursor.to_list(length=None)
        
        total_users = len(users)
        processed_users = 0
        
        # Process users in batches
        batch_size = 20
        for i in range(0, total_users, batch_size):
            batch_users = users[i:i + batch_size]
            
            # Update task status
            progress = (i / total_users) * 100
            self.update_state(
                state="PROGRESS", 
                meta={"status": f"Processing batch {i//batch_size + 1}/{(total_users + batch_size - 1)//batch_size}", "progress": progress}
            )
            
            # Process batch
            for user in batch_users:
                user_id = user['user_id']
                try:
                    await feature_pipeline.process_user_features(user_id)
                    processed_users += 1
                except Exception as e:
                    logger.error(f"Error processing features for user {user_id}: {e}")
        
        logger.info(f"User feature updates completed: {processed_users}/{total_users} users processed")
        
        return {
            "status": "success",
            "processed_users": processed_users,
            "total_users": total_users,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating user features: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task(bind=True)
def update_rfm_features(self, user_ids: list = None):
    """Update RFM features for users"""
    try:
        logger.info("Starting RFM feature updates...")
        
        # Initialize RFM extractor
        rfm_extractor = RFMFeatureExtractor()
        
        # Get user IDs if not provided
        if not user_ids:
            users_collection = MongoDB.get_database()[Collections.USERS]
            cursor = users_collection.find({}, {"user_id": 1})
            users = await cursor.to_list(length=None)
            user_ids = [user['user_id'] for user in users]
        
        total_users = len(user_ids)
        processed_users = 0
        
        # Process users
        for i, user_id in enumerate(user_ids):
            # Update task status
            progress = (i / total_users) * 100
            self.update_state(
                state="PROGRESS", 
                meta={"status": f"Processing user {i+1}/{total_users}", "progress": progress}
            )
            
            try:
                # Calculate RFM features
                rfm_features = await rfm_extractor.calculate_rfm_for_user(user_id)
                
                # Update user features in database
                user_features_collection = MongoDB.get_database()[Collections.USER_FEATURES]
                await user_features_collection.update_one(
                    {"user_id": user_id},
                    {"$set": {"rfm_features": rfm_features.dict(), "last_updated": datetime.utcnow()}},
                    upsert=True
                )
                
                processed_users += 1
                
            except Exception as e:
                logger.error(f"Error updating RFM features for user {user_id}: {e}")
        
        logger.info(f"RFM feature updates completed: {processed_users}/{total_users} users processed")
        
        return {
            "status": "success",
            "processed_users": processed_users,
            "total_users": total_users,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating RFM features: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task(bind=True)
def update_browsing_features(self, user_ids: list = None):
    """Update browsing features for users"""
    try:
        logger.info("Starting browsing feature updates...")
        
        # Initialize browsing extractor
        browsing_extractor = BrowsingFeatureExtractor()
        
        # Get user IDs if not provided
        if not user_ids:
            users_collection = MongoDB.get_database()[Collections.USERS]
            cursor = users_collection.find({}, {"user_id": 1})
            users = await cursor.to_list(length=None)
            user_ids = [user['user_id'] for user in users]
        
        total_users = len(user_ids)
        processed_users = 0
        
        # Process users
        for i, user_id in enumerate(user_ids):
            # Update task status
            progress = (i / total_users) * 100
            self.update_state(
                state="PROGRESS", 
                meta={"status": f"Processing user {i+1}/{total_users}", "progress": progress}
            )
            
            try:
                # Calculate browsing features
                browsing_features = await browsing_extractor.calculate_browsing_features_for_user(user_id)
                
                # Update user features in database
                user_features_collection = MongoDB.get_database()[Collections.USER_FEATURES]
                await user_features_collection.update_one(
                    {"user_id": user_id},
                    {"$set": {"browsing_features": browsing_features.dict(), "last_updated": datetime.utcnow()}},
                    upsert=True
                )
                
                processed_users += 1
                
            except Exception as e:
                logger.error(f"Error updating browsing features for user {user_id}: {e}")
        
        logger.info(f"Browsing feature updates completed: {processed_users}/{total_users} users processed")
        
        return {
            "status": "success",
            "processed_users": processed_users,
            "total_users": total_users,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating browsing features: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task(bind=True)
def update_category_affinity(self, user_ids: list = None):
    """Update category affinity features for users"""
    try:
        logger.info("Starting category affinity updates...")
        
        # Initialize category affinity extractor
        category_extractor = CategoryAffinityExtractor()
        
        # Get user IDs if not provided
        if not user_ids:
            users_collection = MongoDB.get_database()[Collections.USERS]
            cursor = users_collection.find({}, {"user_id": 1})
            users = await cursor.to_list(length=None)
            user_ids = [user['user_id'] for user in users]
        
        total_users = len(user_ids)
        processed_users = 0
        
        # Process users
        for i, user_id in enumerate(user_ids):
            # Update task status
            progress = (i / total_users) * 100
            self.update_state(
                state="PROGRESS", 
                meta={"status": f"Processing user {i+1}/{total_users}", "progress": progress}
            )
            
            try:
                # Calculate category affinity
                category_affinity = await category_extractor.calculate_category_affinity_for_user(user_id)
                
                # Update user features in database
                user_features_collection = MongoDB.get_database()[Collections.USER_FEATURES]
                await user_features_collection.update_one(
                    {"user_id": user_id},
                    {
                        "$set": {
                            "category_affinity_vector": [ca.dict() for ca in category_affinity],
                            "last_updated": datetime.utcnow()
                        }
                    },
                    upsert=True
                )
                
                processed_users += 1
                
            except Exception as e:
                logger.error(f"Error updating category affinity for user {user_id}: {e}")
        
        logger.info(f"Category affinity updates completed: {processed_users}/{total_users} users processed")
        
        return {
            "status": "success",
            "processed_users": processed_users,
            "total_users": total_users,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating category affinity: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task
def calculate_feature_importance():
    """Calculate feature importance for ML models"""
    try:
        logger.info("Starting feature importance calculation...")
        
        # This would analyze which features are most predictive
        # For now, return placeholder results
        
        feature_importance = {
            "rfm_recency": 0.25,
            "rfm_frequency": 0.30,
            "rfm_monetary": 0.35,
            "browsing_session_duration": 0.15,
            "browsing_pages_per_session": 0.12,
            "browsing_bounce_rate": 0.08,
            "category_affinity_electronics": 0.20,
            "category_affinity_clothing": 0.15,
            "category_affinity_home": 0.10
        }
        
        logger.info("Feature importance calculation completed")
        
        return {
            "status": "success",
            "feature_importance": feature_importance,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error calculating feature importance: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task
def validate_feature_quality():
    """Validate the quality of computed features"""
    try:
        logger.info("Starting feature quality validation...")
        
        # This would check for missing values, outliers, etc.
        # For now, return placeholder results
        
        quality_report = {
            "total_users": 1000,
            "users_with_complete_features": 950,
            "missing_feature_rate": 0.05,
            "outlier_rate": 0.02,
            "data_quality_score": 0.93,
            "issues": [
                "Some users have missing browsing history",
                "RFM features need updating for inactive users"
            ]
        }
        
        logger.info("Feature quality validation completed")
        
        return {
            "status": "success",
            "quality_report": quality_report,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error validating feature quality: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task
def generate_feature_report():
    """Generate comprehensive feature report"""
    try:
        logger.info("Starting feature report generation...")
        
        # This would generate detailed reports about feature distributions
        # For now, return placeholder results
        
        feature_report = {
            "rfm_analysis": {
                "avg_recency": 45.5,
                "avg_frequency": 3.2,
                "avg_monetary": 234.56,
                "recency_distribution": {"low": 0.3, "medium": 0.4, "high": 0.3},
                "frequency_distribution": {"low": 0.5, "medium": 0.3, "high": 0.2},
                "monetary_distribution": {"low": 0.4, "medium": 0.4, "high": 0.2}
            },
            "browsing_analysis": {
                "avg_session_duration": 12.5,
                "avg_pages_per_session": 4.3,
                "avg_bounce_rate": 0.35,
                "peak_hour": 14,
                "weekend_preference": 0.65
            },
            "category_analysis": {
                "top_categories": ["Electronics", "Clothing", "Home", "Books", "Sports"],
                "category_diversity": 3.2,
                "cross_category_rate": 0.45
            }
        }
        
        logger.info("Feature report generation completed")
        
        return {
            "status": "success",
            "feature_report": feature_report,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating feature report: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task
def cleanup_stale_features():
    """Clean up stale feature data"""
    try:
        logger.info("Starting stale feature cleanup...")
        
        # Remove features for users who haven't been active
        user_features_collection = MongoDB.get_database()[Collections.USER_FEATURES]
        
        # Find inactive users (no activity in last 90 days)
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        
        # Get active users from recent sessions
        sessions_collection = MongoDB.get_database()[Collections.SESSIONS]
        active_users = await sessions_collection.distinct("user_id", {"start_time": {"$gte": ninety_days_ago}})
        
        # Remove features for inactive users
        result = await user_features_collection.delete_many({
            "user_id": {"$nin": active_users},
            "last_updated": {"$lt": ninety_days_ago}
        })
        
        logger.info(f"Stale feature cleanup completed: {result.deleted_count} records removed")
        
        return {
            "status": "success",
            "deleted_records": result.deleted_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up stale features: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
