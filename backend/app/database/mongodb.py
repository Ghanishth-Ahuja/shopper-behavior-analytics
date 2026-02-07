from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings
from typing import Optional


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None

    @classmethod
    async def connect_to_mongo(cls):
        """Create database connection"""
        cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
        cls.database = cls.client[settings.DATABASE_NAME]
        print(f"Connected to MongoDB: {settings.DATABASE_NAME}")
        
        # Create indexes
        await cls.database[Collections.DASHBOARD_USERS].create_index("email", unique=True)

    @classmethod
    async def close_mongo_connection(cls):
        """Close database connection"""
        if cls.client:
            cls.client.close()
            print("Disconnected from MongoDB")

    @classmethod
    def get_database(cls):
        """Get database instance"""
        return cls.database

    @classmethod
    def get_collection(cls, collection_name: str):
        """Get collection instance"""
        return cls.database[collection_name]


# Collection names
class Collections:
    USERS = "users"
    SESSIONS = "sessions"
    TRANSACTIONS = "transactions"
    PRODUCTS = "products"
    REVIEWS = "reviews"
    SEGMENTS = "segments"
    USER_FEATURES = "user_features"
    EVENTS = "events"
    DASHBOARD_USERS = "dashboard_users"
