from typing import List, Optional, Dict, Any
from app.models.user import User, UserCreate, UserUpdate
from app.database.mongodb import MongoDB, Collections
from bson import ObjectId


class UserService:
    """Service for user management operations"""
    
    def __init__(self):
        self.db = MongoDB.get_database()
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        try:
            users_collection = self.db[Collections.USERS]
            
            # Check if user already exists
            existing_user = await users_collection.find_one({"user_id": user_data.user_id})
            if existing_user:
                raise ValueError(f"User with ID {user_data.user_id} already exists")
            
            # Create user document
            user_dict = user_data.dict()
            user_dict["_id"] = ObjectId()
            
            # Insert user
            result = await users_collection.insert_one(user_dict)
            
            # Get created user
            created_user = await users_collection.find_one({"_id": result.inserted_id})
            
            return User(**created_user)
            
        except Exception as e:
            print(f"Error creating user: {e}")
            raise
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            users_collection = self.db[Collections.USERS]
            user_doc = await users_collection.find_one({"user_id": user_id})
            
            if user_doc:
                return User(**user_doc)
            return None
            
        except Exception as e:
            print(f"Error getting user {user_id}: {e}")
            return None
    
    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """Update user information"""
        try:
            users_collection = self.db[Collections.USERS]
            
            # Prepare update data
            update_data = user_update.dict(exclude_unset=True)
            if not update_data:
                return await self.get_user(user_id)
            
            # Update user
            result = await users_collection.update_one(
                {"user_id": user_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_user(user_id)
            
            return None
            
        except Exception as e:
            print(f"Error updating user {user_id}: {e}")
            return None
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        try:
            users_collection = self.db[Collections.USERS]
            result = await users_collection.delete_one({"user_id": user_id})
            
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Error deleting user {user_id}: {e}")
            return False
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        try:
            users_collection = self.db[Collections.USERS]
            cursor = users_collection.find().skip(skip).limit(limit)
            users = await cursor.to_list(length=None)
            
            return [User(**user) for user in users]
            
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    async def get_user_segment(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's segment information"""
        try:
            # Get user
            user = await self.get_user(user_id)
            if not user:
                return None
            
            segment_id = user.segment_id
            if not segment_id:
                return {"user_id": user_id, "segment_id": None, "message": "User not assigned to any segment"}
            
            # Get segment details
            segments_collection = self.db[Collections.SEGMENTS]
            segment = await segments_collection.find_one({"segment_id": segment_id})
            
            if segment:
                return {
                    "user_id": user_id,
                    "segment_id": segment_id,
                    "segment_name": segment.get("segment_name"),
                    "segment_characteristics": segment.get("characteristics"),
                    "top_categories": segment.get("top_categories"),
                    "price_sensitivity": segment.get("price_sensitivity")
                }
            
            return {"user_id": user_id, "segment_id": segment_id, "message": "Segment not found"}
            
        except Exception as e:
            print(f"Error getting user segment for {user_id}: {e}")
            return None
    
    async def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a user"""
        try:
            analytics = {}
            
            # Get user info
            user = await self.get_user(user_id)
            if not user:
                return {"error": "User not found"}
            
            analytics["user_info"] = {
                "user_id": user.user_id,
                "signup_date": user.signup_date,
                "acquisition_channel": user.acquisition_channel,
                "lifetime_value": user.lifetime_value,
                "segment_id": user.segment_id
            }
            
            # Get transaction summary
            transactions_collection = self.db[Collections.TRANSACTIONS]
            cursor = transactions_collection.find({"user_id": user_id})
            transactions = await cursor.to_list(length=None)
            
            total_spent = sum(t.get("total_amount", 0) for t in transactions)
            total_transactions = len(transactions)
            
            analytics["transaction_summary"] = {
                "total_transactions": total_transactions,
                "total_spent": total_spent,
                "avg_order_value": total_spent / total_transactions if total_transactions > 0 else 0
            }
            
            # Get review summary
            reviews_collection = self.db[Collections.REVIEWS]
            cursor = reviews_collection.find({"user_id": user_id})
            reviews = await cursor.to_list(length=None)
            
            if reviews:
                avg_rating = sum(r.get("rating", 0) for r in reviews) / len(reviews)
                analytics["review_summary"] = {
                    "total_reviews": len(reviews),
                    "avg_rating": avg_rating
                }
            else:
                analytics["review_summary"] = {
                    "total_reviews": 0,
                    "avg_rating": 0
                }
            
            # Get session summary
            sessions_collection = self.db[Collections.SESSIONS]
            cursor = sessions_collection.find({"user_id": user_id})
            sessions = await cursor.to_list(length=None)
            
            total_sessions = len(sessions)
            if sessions:
                # Calculate session duration
                total_duration = 0
                for session in sessions:
                    start_time = session.get("start_time")
                    end_time = session.get("end_time")
                    if start_time and end_time:
                        duration = (end_time - start_time).total_seconds() / 60  # minutes
                        total_duration += duration
                
                analytics["session_summary"] = {
                    "total_sessions": total_sessions,
                    "avg_session_duration": total_duration / total_sessions if total_sessions > 0 else 0
                }
            else:
                analytics["session_summary"] = {
                    "total_sessions": 0,
                    "avg_session_duration": 0
                }
            
            return analytics
            
        except Exception as e:
            print(f"Error getting user analytics for {user_id}: {e}")
            return {"error": str(e)}
    
    async def search_users(self, query: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Search users by various fields"""
        try:
            users_collection = self.db[Collections.USERS]
            
            # Create search filter
            search_filter = {
                "$or": [
                    {"user_id": {"$regex": query, "$options": "i"}},
                    {"acquisition_channel": {"$regex": query, "$options": "i"}}
                ]
            }
            
            cursor = users_collection.find(search_filter).skip(skip).limit(limit)
            users = await cursor.to_list(length=None)
            
            return [User(**user) for user in users]
            
        except Exception as e:
            print(f"Error searching users: {e}")
            return []
    
    async def get_users_by_segment(self, segment_id: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by segment"""
        try:
            users_collection = self.db[Collections.USERS]
            cursor = users_collection.find({"segment_id": segment_id}).skip(skip).limit(limit)
            users = await cursor.to_list(length=None)
            
            return [User(**user) for user in users]
            
        except Exception as e:
            print(f"Error getting users by segment {segment_id}: {e}")
            return []
    
    async def update_user_lifetime_value(self, user_id: str, additional_value: float) -> bool:
        """Update user's lifetime value"""
        try:
            users_collection = self.db[Collections.USERS]
            
            result = await users_collection.update_one(
                {"user_id": user_id},
                {"$inc": {"lifetime_value": additional_value}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error updating user lifetime value for {user_id}: {e}")
            return False
    
    async def get_user_count_by_segment(self) -> Dict[str, int]:
        """Get count of users in each segment"""
        try:
            users_collection = self.db[Collections.USERS]
            
            pipeline = [
                {"$group": {"_id": "$segment_id", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            cursor = users_collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            segment_counts = {}
            for result in results:
                segment_id = result["_id"]
                count = result["count"]
                segment_counts[segment_id or "unassigned"] = count
            
            return segment_counts
            
        except Exception as e:
            print(f"Error getting user count by segment: {e}")
            return {}
