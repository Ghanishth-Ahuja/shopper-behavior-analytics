from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # MongoDB Settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "shopper_analytics"
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Shopper Behavior Analytics"
    
    # ML Settings
    MODEL_PATH: str = "models/"
    FEATURE_STORE_PATH: str = "features/"
    
    # Background Jobs
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"


settings = Settings()
