from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.session import Session, SessionCreate, SessionUpdate, Event
from app.database.mongodb import MongoDB, Collections
from bson import ObjectId


class SessionService:
    """Service for session management operations"""
    
    def __init__(self):
        self.db = MongoDB.get_database()
    
    async def create_session(self, session_data: SessionCreate) -> Session:
        """Create a new session"""
        try:
            sessions_collection = self.db[Collections.SESSIONS]
            
            # Check if session already exists
            existing_session = await sessions_collection.find_one({"session_id": session_data.session_id})
            if existing_session:
                raise ValueError(f"Session with ID {session_data.session_id} already exists")
            
            # Create session document
            session_dict = session_data.dict()
            session_dict["_id"] = ObjectId()
            
            # Insert session
            result = await sessions_collection.insert_one(session_dict)
            
            # Get created session
            created_session = await sessions_collection.find_one({"_id": result.inserted_id})
            
            return Session(**created_session)
            
        except Exception as e:
            print(f"Error creating session: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        try:
            sessions_collection = self.db[Collections.SESSIONS]
            session_doc = await sessions_collection.find_one({"session_id": session_id})
            
            if session_doc:
                return Session(**session_doc)
            return None
            
        except Exception as e:
            print(f"Error getting session {session_id}: {e}")
            return None
    
    async def update_session(self, session_id: str, session_update: SessionUpdate) -> Optional[Session]:
        """Update session information"""
        try:
            sessions_collection = self.db[Collections.SESSIONS]
            
            # Prepare update data
            update_data = session_update.dict(exclude_unset=True)
            if not update_data:
                return await self.get_session(session_id)
            
            # Update session
            result = await sessions_collection.update_one(
                {"session_id": session_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_session(session_id)
            
            return None
            
        except Exception as e:
            print(f"Error updating session {session_id}: {e}")
            return None
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            sessions_collection = self.db[Collections.SESSIONS]
            result = await sessions_collection.delete_one({"session_id": session_id})
            
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False
    
    async def get_user_sessions(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Session]:
        """Get all sessions for a user"""
        try:
            sessions_collection = self.db[Collections.SESSIONS]
            cursor = sessions_collection.find({"user_id": user_id}).skip(skip).limit(limit)
            sessions = await cursor.to_list(length=None)
            
            return [Session(**session) for session in sessions]
            
        except Exception as e:
            print(f"Error getting user sessions for {user_id}: {e}")
            return []
    
    async def add_event(self, session_id: str, event: Event) -> Optional[Session]:
        """Add an event to a session"""
        try:
            sessions_collection = self.db[Collections.SESSIONS]
            
            # Add event to session
            result = await sessions_collection.update_one(
                {"session_id": session_id},
                {"$push": {"events": event.dict()}}
            )
            
            if result.modified_count > 0:
                return await self.get_session(session_id)
            
            return None
            
        except Exception as e:
            print(f"Error adding event to session {session_id}: {e}")
            return None
    
    async def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get analytics for a specific session"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return {"error": "Session not found"}
            
            analytics = {
                "session_id": session_id,
                "user_id": session.user_id,
                "start_time": session.start_time,
                "end_time": session.end_time
            }
            
            # Calculate session duration
            if session.start_time and session.end_time:
                duration = (session.end_time - session.start_time).total_seconds() / 60  # minutes
                analytics["duration_minutes"] = duration
            else:
                analytics["duration_minutes"] = 0
            
            # Analyze events
            events = session.events
            analytics["total_events"] = len(events)
            
            # Event type breakdown
            event_types = {}
            for event in events:
                event_type = event.type
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            analytics["event_types"] = event_types
            
            # Products viewed
            viewed_products = set()
            for event in events:
                if event.type == "view" and event.product_id:
                    viewed_products.add(event.product_id)
            
            analytics["products_viewed"] = list(viewed_products)
            analytics["unique_products_viewed"] = len(viewed_products)
            
            # Cart additions
            cart_additions = [event for event in events if event.type == "add_to_cart"]
            analytics["cart_additions"] = len(cart_additions)
            
            # Purchases
            purchases = [event for event in events if event.type == "purchase"]
            analytics["purchases"] = len(purchases)
            
            # Conversion (cart to purchase)
            if len(cart_additions) > 0:
                analytics["conversion_rate"] = (len(purchases) / len(cart_additions)) * 100
            else:
                analytics["conversion_rate"] = 0
            
            return analytics
            
        except Exception as e:
            print(f"Error getting session analytics for {session_id}: {e}")
            return {"error": str(e)}
    
    async def get_user_session_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get session summary for a user over time period"""
        try:
            from datetime import timedelta
            
            sessions_collection = self.db[Collections.SESSIONS]
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            cursor = sessions_collection.find({
                "user_id": user_id,
                "start_time": {"$gte": start_date, "$lte": end_date}
            })
            sessions = await cursor.to_list(length=None)
            
            if not sessions:
                return {
                    "user_id": user_id,
                    "period_days": days,
                    "total_sessions": 0,
                    "message": "No sessions found in period"
                }
            
            # Calculate summary metrics
            total_sessions = len(sessions)
            total_events = sum(len(session.get("events", [])) for session in sessions)
            
            # Calculate average session duration
            durations = []
            for session in sessions:
                start_time = session.get("start_time")
                end_time = session.get("end_time")
                if start_time and end_time:
                    duration = (end_time - start_time).total_seconds() / 60
                    durations.append(duration)
            
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            # Event type breakdown
            all_events = []
            for session in sessions:
                all_events.extend(session.get("events", []))
            
            event_types = {}
            for event in all_events:
                event_type = event.get("type", "unknown")
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            # Device breakdown
            device_types = {}
            for session in sessions:
                device_type = session.get("device_type", "unknown")
                device_types[device_type] = device_types.get(device_type, 0) + 1
            
            return {
                "user_id": user_id,
                "period_days": days,
                "total_sessions": total_sessions,
                "total_events": total_events,
                "avg_session_duration": avg_duration,
                "avg_events_per_session": total_events / total_sessions if total_sessions > 0 else 0,
                "event_types": event_types,
                "device_types": device_types
            }
            
        except Exception as e:
            print(f"Error getting user session summary for {user_id}: {e}")
            return {"error": str(e)}
    
    async def get_active_sessions(self, minutes: int = 30) -> List[Session]:
        """Get currently active sessions (last activity within X minutes)"""
        try:
            from datetime import timedelta
            
            sessions_collection = self.db[Collections.SESSIONS]
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
            
            # Find sessions with recent activity or no end time
            cursor = sessions_collection.find({
                "$or": [
                    {"end_time": None},
                    {"end_time": {"$gte": cutoff_time}}
                ]
            })
            sessions = await cursor.to_list(length=None)
            
            return [Session(**session) for session in sessions]
            
        except Exception as e:
            print(f"Error getting active sessions: {e}")
            return []
    
    async def end_session(self, session_id: str) -> bool:
        """End a session by setting end_time"""
        try:
            sessions_collection = self.db[Collections.SESSIONS]
            result = await sessions_collection.update_one(
                {"session_id": session_id, "end_time": None},
                {"$set": {"end_time": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error ending session {session_id}: {e}")
            return False
    
    async def get_session_funnel(self, user_id: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """Get conversion funnel analysis from sessions"""
        try:
            from datetime import timedelta
            
            sessions_collection = self.db[Collections.SESSIONS]
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Build filter
            filter_dict = {"start_time": {"$gte": start_date, "$lte": end_date}}
            if user_id:
                filter_dict["user_id"] = user_id
            
            cursor = sessions_collection.find(filter_dict)
            sessions = await cursor.to_list(length=None)
            
            # Funnel stages
            total_sessions = len(sessions)
            sessions_with_views = 0
            sessions_with_cart = 0
            sessions_with_purchase = 0
            
            for session in sessions:
                events = session.get("events", [])
                has_view = any(event.get("type") == "view" for event in events)
                has_cart = any(event.get("type") == "add_to_cart" for event in events)
                has_purchase = any(event.get("type") == "purchase" for event in events)
                
                if has_view:
                    sessions_with_views += 1
                if has_cart:
                    sessions_with_cart += 1
                if has_purchase:
                    sessions_with_purchase += 1
            
            # Calculate conversion rates
            funnel = {
                "total_sessions": total_sessions,
                "sessions_with_views": sessions_with_views,
                "sessions_with_cart": sessions_with_cart,
                "sessions_with_purchase": sessions_with_purchase,
                "view_rate": (sessions_with_views / total_sessions * 100) if total_sessions > 0 else 0,
                "cart_rate": (sessions_with_cart / total_sessions * 100) if total_sessions > 0 else 0,
                "purchase_rate": (sessions_with_purchase / total_sessions * 100) if total_sessions > 0 else 0,
                "cart_to_purchase_rate": (sessions_with_purchase / sessions_with_cart * 100) if sessions_with_cart > 0 else 0
            }
            
            return funnel
            
        except Exception as e:
            print(f"Error getting session funnel: {e}")
            return {"error": str(e)}
