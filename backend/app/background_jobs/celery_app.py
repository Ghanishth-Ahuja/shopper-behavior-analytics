from celery import Celery
from app.config.settings import settings
import os

# Create Celery app
celery_app = Celery(
    "shopper_analytics",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.background_jobs.ml_tasks",
        "app.background_jobs.feature_tasks",
        "app.background_jobs.analytics_tasks",
        "app.background_jobs.nlp_tasks"
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    # Daily ML model retraining
    "retrain-segmentation-model": {
        "task": "app.background_jobs.ml_tasks.retrain_segmentation_model",
        "schedule": 3600.0 * 24,  # Daily
    },
    
    # Feature updates
    "update-user-features": {
        "task": "app.background_jobs.feature_tasks.update_all_user_features",
        "schedule": 3600.0 * 6,  # Every 6 hours
    },
    
    # Analytics calculations
    "calculate-daily-analytics": {
        "task": "app.background_jobs.analytics_tasks.calculate_daily_analytics",
        "schedule": 3600.0 * 24,  # Daily
    },
    
    # NLP processing
    "process-new-reviews": {
        "task": "app.background_jobs.nlp_tasks.process_new_reviews",
        "schedule": 3600.0,  # Hourly
    },
    
    # Data cleanup
    "cleanup-old-events": {
        "task": "app.background_jobs.analytics_tasks.cleanup_old_events",
        "schedule": 3600.0 * 24 * 7,  # Weekly
    },
    
    # Recommendation model updates
    "update-recommendation-models": {
        "task": "app.background_jobs.ml_tasks.update_recommendation_models",
        "schedule": 3600.0 * 24,  # Daily
    },
}

# Optional: Configure queues for different task types
celery_app.conf.task_routes = {
    "app.background_jobs.ml_tasks.*": {"queue": "ml"},
    "app.background_jobs.feature_tasks.*": {"queue": "features"},
    "app.background_jobs.analytics_tasks.*": {"queue": "analytics"},
    "app.background_jobs.nlp_tasks.*": {"queue": "nlp"},
}

# Optional: Configure worker settings
celery_app.conf.worker_direct = True
celery_app.conf.worker_prefetch_multiplier = 1
