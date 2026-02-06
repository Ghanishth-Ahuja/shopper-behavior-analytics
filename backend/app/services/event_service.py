from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.session import Event
from app.database.mongodb import MongoDB, Collections
from app.feature_pipeline.feature_pipeline import FeaturePipeline
from bson import ObjectId


class EventService:
    """Service for event tracking and real-time processing"""
    
    def __init__(self):
        self.db = MongoDB.get_database()
        self.feature_pipeline = FeaturePipeline()
    
    async def track_event(self, event: Event) -> ObjectId:
        """Track user events in real-time"""
        try:
            events_collection = self.db.get_collection("events")
            
            # Create event document
            event_dict = event.dict()
            event_dict["_id"] = ObjectId()
            event_dict["processed"] = False
            
            # Insert event
            result = await events_collection.insert_one(event_dict)
            
            return result.inserted_id
            
        except Exception as e:
            print(f"Error tracking event: {e}")
            raise
    
    async def get_user_events(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Get events for a specific user"""
        try:
            events_collection = self.db.get_collection("events")
            cursor = events_collection.find({"user_id": user_id}).sort("timestamp", -1).skip(skip).limit(limit)
            events = await cursor.to_list(length=None)
            
            return events
            
        except Exception as e:
            print(f"Error getting user events for {user_id}: {e}")
            return []
    
    async def get_session_events(self, session_id: str, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Get events for a specific session"""
        try:
            events_collection = self.db.get_collection("events")
            cursor = events_collection.find({"session_id": session_id}).sort("timestamp", -1).skip(skip).limit(limit)
            events = await cursor.to_list(length=None)
            
            return events
            
        except Exception as e:
            print(f"Error getting session events for {session_id}: {e}")
            return []
    
    async def get_product_events(self, product_id: str, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Get events related to a specific product"""
        try:
            events_collection = self.db.get_collection("events")
            cursor = events_collection.find({"product_id": product_id}).sort("timestamp", -1).skip(skip).limit(limit)
            events = await cursor.to_list(length=None)
            
            return events
            
        except Exception as e:
            print(f"Error getting product events for {product_id}: {e}")
            return []
    
    async def get_events_by_type(self, event_type: str, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Get events by type (view, add_to_cart, purchase, etc.)"""
        try:
            events_collection = self.db.get_collection("events")
            cursor = events_collection.find({"type": event_type}).sort("timestamp", -1).skip(skip).limit(limit)
            events = await cursor.to_list(length=None)
            
            return events
            
        except Exception as e:
            print(f"Error getting events by type {event_type}: {e}")
            return []
    
    async def get_realtime_events(self, user_id: str, minutes: int = 30) -> List[Dict]:
        """Get recent events for real-time processing"""
        try:
            events_collection = self.db.get_collection("events")
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
            
            cursor = events_collection.find({
                "user_id": user_id,
                "timestamp": {"$gte": cutoff_time}
            }).sort("timestamp", -1)
            
            events = await cursor.to_list(length=None)
            
            return events
            
        except Exception as e:
            print(f"Error getting realtime events for {user_id}: {e}")
            return []
    
    async def update_user_features_realtime(self, user_id: str, event: Event) -> None:
        """Update user features in real-time based on events"""
        try:
            # Get current user features
            current_features = await self.feature_pipeline.get_user_features(user_id)
            
            if not current_features:
                # If no features exist, create them
                await self.feature_pipeline.process_user_features(user_id)
                return
            
            # Update features based on event type
            event_type = event.type
            
            if event_type == "purchase":
                await self._handle_purchase_event(user_id, event)
            elif event_type == "view":
                await self._handle_view_event(user_id, event)
            elif event_type == "add_to_cart":
                await self._handle_cart_event(user_id, event)
            elif event_type == "search":
                await self._handle_search_event(user_id, event)
            
            # Mark event as processed
            await self._mark_event_processed(event)
            
        except Exception as e:
            print(f"Error updating user features in real-time for {user_id}: {e}")
    
    async def get_event_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get event analytics and metrics"""
        try:
            events_collection = self.db.get_collection("events")
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            cursor = events_collection.find({
                "timestamp": {"$gte": start_date, "$lte": end_date}
            })
            events = await cursor.to_list(length=None)
            
            if not events:
                return {
                    "period_days": days,
                    "total_events": 0,
                    "event_types": {},
                    "daily_events": {},
                    "top_products": {}
                }
            
            # Event type breakdown
            event_types = {}
            for event in events:
                event_type = event.get("type", "unknown")
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            # Daily events
            daily_events = {}
            for event in events:
                date = event.get("timestamp", datetime.utcnow()).date()
                date_str = str(date)
                daily_events[date_str] = daily_events.get(date_str, 0) + 1
            
            # Top products
            product_events = {}
            for event in events:
                product_id = event.get("product_id")
                if product_id:
                    product_events[product_id] = product_events.get(product_id, 0) + 1
            
            top_products = dict(sorted(product_events.items(), key=lambda x: x[1], reverse=True)[:10])
            
            return {
                "period_days": days,
                "total_events": len(events),
                "event_types": event_types,
                "daily_events": daily_events,
                "top_products": top_products
            }
            
        except Exception as e:
            print(f"Error getting event analytics: {e}")
            return {}
    
    async def get_user_journey(self, user_id: str, days: int = 7) -> List[Dict]:
        """Get user journey with events and sessions"""
        try:
            events_collection = self.db.get_collection("events")
            sessions_collection = self.db[Collections.SESSIONS]
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get user events
            cursor = events_collection.find({
                "user_id": user_id,
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }).sort("timestamp", 1)
            
            events = await cursor.to_list(length=None)
            
            # Get user sessions
            cursor = sessions_collection.find({
                "user_id": user_id,
                "start_time": {"$gte": start_date, "$lte": end_date}
            }).sort("start_time", 1)
            
            sessions = await cursor.to_list(length=None)
            
            # Combine events and sessions into journey
            journey = []
            
            # Add session starts
            for session in sessions:
                journey.append({
                    "type": "session_start",
                    "timestamp": session.get("start_time"),
                    "session_id": session.get("session_id"),
                    "device_type": session.get("device_type")
                })
            
            # Add events
            for event in events:
                journey.append({
                    "type": "event",
                    "event_type": event.get("type"),
                    "timestamp": event.get("timestamp"),
                    "product_id": event.get("product_id"),
                    "metadata": event.get("metadata", {})
                })
            
            # Sort by timestamp
            journey.sort(key=lambda x: x["timestamp"])
            
            return journey
            
        except Exception as e:
            print(f"Error getting user journey for {user_id}: {e}")
            return []
    
    async def get_conversion_funnel_events(self, days: int = 30) -> Dict[str, Any]:
        """Get conversion funnel based on events"""
        try:
            events_collection = self.db.get_collection("events")
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            cursor = events_collection.find({
                "timestamp": {"$gte": start_date, "$lte": end_date}
            })
            events = await cursor.to_list(length=None)
            
            # Count events by type
            event_counts = {}
            for event in events:
                event_type = event.get("type", "unknown")
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            # Calculate funnel
            total_sessions = event_counts.get("session_start", 0)
            views = event_counts.get("view", 0)
            cart_additions = event_counts.get("add_to_cart", 0)
            purchases = event_counts.get("purchase", 0)
            
            funnel = {
                "sessions": total_sessions,
                "views": views,
                "cart_additions": cart_additions,
                "purchases": purchases,
                "view_rate": (views / total_sessions * 100) if total_sessions > 0 else 0,
                "cart_rate": (cart_additions / total_sessions * 100) if total_sessions > 0 else 0,
                "purchase_rate": (purchases / total_sessions * 100) if total_sessions > 0 else 0,
                "cart_to_purchase_rate": (purchases / cart_additions * 100) if cart_additions > 0 else 0
            }
            
            return funnel
            
        except Exception as e:
            print(f"Error getting conversion funnel events: {e}")
            return {}
    
    async def _handle_purchase_event(self, user_id: str, event: Event) -> None:
        """Handle purchase event for real-time feature updates"""
        try:
            # Update RFM features
            await self.feature_pipeline.process_user_features(user_id)
            
            # Update user lifetime value
            transactions_collection = self.db[Collections.TRANSACTIONS]
            # This would be handled by transaction service
            
        except Exception as e:
            print(f"Error handling purchase event: {e}")
    
    async def _handle_view_event(self, user_id: str, event: Event) -> None:
        """Handle view event for real-time feature updates"""
        try:
            # Update browsing features
            await self.feature_pipeline.process_user_features(user_id)
            
        except Exception as e:
            print(f"Error handling view event: {e}")
    
    async def _handle_cart_event(self, user_id: str, event: Event) -> None:
        """Handle cart event for real-time feature updates"""
        try:
            # Update browsing features
            await self.feature_pipeline.process_user_features(user_id)
            
        except Exception as e:
            print(f"Error handling cart event: {e}")
    
    async def _handle_search_event(self, user_id: str, event: Event) -> None:
        """Handle search event for real-time feature updates"""
        try:
            # Update browsing features
            await self.feature_pipeline.process_user_features(user_id)
            
        except Exception as e:
            print(f"Error handling search event: {e}")
    
    async def _mark_event_processed(self, event: Event) -> None:
        """Mark event as processed"""
        try:
            events_collection = self.db.get_collection("events")
            await events_collection.update_one(
                {"_id": event.get("_id")},
                {"$set": {"processed": True}}
            )
        except Exception as e:
            print(f"Error marking event as processed: {e}")
    
    async def cleanup_old_events(self, days: int = 90) -> int:
        """Clean up old events to save storage"""
        try:
            events_collection = self.db.get_collection("events")
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = await events_collection.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            return result.deleted_count
            
        except Exception as e:
            print(f"Error cleaning up old events: {e}")
            return 0
    
    async def get_event_heatmap(self, days: int = 7) -> Dict[str, Any]:
        """Get event heatmap by hour and day"""
        try:
            events_collection = self.db.get_collection("events")
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            cursor = events_collection.find({
                "timestamp": {"$gte": start_date, "$lte": end_date}
            })
            events = await cursor.to_list(length=None)
            
            # Create heatmap data
            heatmap = {}
            for event in events:
                timestamp = event.get("timestamp", datetime.utcnow())
                hour = timestamp.hour
                day = timestamp.strftime("%A")  # Monday, Tuesday, etc.
                
                key = f"{day}_{hour}"
                heatmap[key] = heatmap.get(key, 0) + 1
            
            return {
                "period_days": days,
                "heatmap": heatmap,
                "total_events": len(events)
            }
            
        except Exception as e:
            print(f"Error getting event heatmap: {e}")
            return {}
