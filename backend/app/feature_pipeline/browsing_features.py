from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.models.user_features import BrowsingFeatures
from app.database.mongodb import MongoDB, Collections
import pandas as pd
import numpy as np


class BrowsingFeatureExtractor:
    """Extract browsing behavior features for users"""
    
    def __init__(self):
        self.db = MongoDB.get_database()
    
    async def calculate_browsing_features_for_user(self, user_id: str) -> BrowsingFeatures:
        """Calculate browsing features for a specific user"""
        try:
            # Get user sessions
            sessions_collection = self.db[Collections.SESSIONS]
            cursor = sessions_collection.find({"user_id": user_id})
            sessions = await cursor.to_list(length=None)
            
            if not sessions:
                return BrowsingFeatures(
                    avg_session_duration=0.0,
                    pages_per_session=0.0,
                    bounce_rate=1.0,
                    cart_abandonment_rate=0.0,
                    search_frequency=0.0,
                    preferred_hour=12,
                    weekend_vs_weekday_ratio=1.0
                )
            
            # Extract session metrics
            session_durations = []
            page_counts = []
            bounce_sessions = 0
            cart_additions = 0
            purchases = 0
            searches = 0
            hour_counts = [0] * 24
            weekend_sessions = 0
            weekday_sessions = 0
            
            for session in sessions:
                # Calculate session duration
                start_time = session.get('start_time')
                end_time = session.get('end_time')
                
                if start_time and end_time:
                    duration = (end_time - start_time).total_seconds() / 60  # minutes
                    session_durations.append(duration)
                else:
                    session_durations.append(0)
                
                # Count events
                events = session.get('events', [])
                page_views = len([e for e in events if e.get('type') == 'view'])
                page_counts.append(page_views)
                
                # Check for bounce (single page view)
                if page_views <= 1:
                    bounce_sessions += 1
                
                # Count cart additions and purchases
                cart_additions += len([e for e in events if e.get('type') == 'add_to_cart'])
                purchases += len([e for e in events if e.get('type') == 'purchase'])
                searches += len([e for e in events if e.get('type') == 'search'])
                
                # Extract hour preference
                if start_time:
                    hour = start_time.hour
                    hour_counts[hour] += 1
                    
                    # Weekend vs weekday
                    if start_time.weekday() >= 5:  # Saturday, Sunday
                        weekend_sessions += 1
                    else:
                        weekday_sessions += 1
            
            # Calculate metrics
            total_sessions = len(sessions)
            
            # Average session duration
            avg_session_duration = np.mean(session_durations) if session_durations else 0.0
            
            # Pages per session
            pages_per_session = np.mean(page_counts) if page_counts else 0.0
            
            # Bounce rate
            bounce_rate = bounce_sessions / total_sessions if total_sessions > 0 else 1.0
            
            # Cart abandonment rate
            total_cart_events = cart_additions + purchases
            cart_abandonment_rate = (cart_additions - purchases) / total_cart_events if total_cart_events > 0 else 0.0
            
            # Search frequency (searches per session)
            search_frequency = searches / total_sessions if total_sessions > 0 else 0.0
            
            # Preferred hour (hour with most activity)
            preferred_hour = np.argmax(hour_counts) if hour_counts else 12
            
            # Weekend vs weekday ratio
            total_active_sessions = weekend_sessions + weekday_sessions
            weekend_vs_weekday_ratio = weekend_sessions / weekday_sessions if weekday_sessions > 0 else 1.0
            
            return BrowsingFeatures(
                avg_session_duration=float(avg_session_duration),
                pages_per_session=float(pages_per_session),
                bounce_rate=float(bounce_rate),
                cart_abandonment_rate=float(cart_abandonment_rate),
                search_frequency=float(search_frequency),
                preferred_hour=int(preferred_hour),
                weekend_vs_weekday_ratio=float(weekend_vs_weekday_ratio)
            )
            
        except Exception as e:
            print(f"Error calculating browsing features for user {user_id}: {e}")
            return BrowsingFeatures(
                avg_session_duration=0.0,
                pages_per_session=0.0,
                bounce_rate=1.0,
                cart_abandonment_rate=0.0,
                search_frequency=0.0,
                preferred_hour=12,
                weekend_vs_weekday_ratio=1.0
            )
    
    async def get_user_engagement_score(self, user_id: str) -> float:
        """Calculate overall engagement score (0-1) for a user"""
        try:
            features = await self.calculate_browsing_features_for_user(user_id)
            
            # Normalize and weight different features
            duration_score = min(features.avg_session_duration / 30, 1.0)  # 30 min = max score
            pages_score = min(features.pages_per_session / 10, 1.0)  # 10 pages = max score
            bounce_penalty = features.bounce_rate  # Higher bounce = lower engagement
            search_score = min(features.search_frequency / 5, 1.0)  # 5 searches = max score
            
            # Weighted average (bounce rate is penalized)
            engagement_score = (
                duration_score * 0.3 +
                pages_score * 0.3 +
                (1 - bounce_penalty) * 0.2 +
                search_score * 0.2
            )
            
            return max(0.0, min(1.0, engagement_score))
            
        except Exception as e:
            print(f"Error calculating engagement score for user {user_id}: {e}")
            return 0.0
    
    async def get_device_preference(self, user_id: str) -> Dict[str, float]:
        """Get device preference breakdown for a user"""
        try:
            sessions_collection = self.db[Collections.SESSIONS]
            cursor = sessions_collection.find({"user_id": user_id})
            sessions = await cursor.to_list(length=None)
            
            device_counts = {}
            total_sessions = len(sessions)
            
            if total_sessions == 0:
                return {"desktop": 0.33, "mobile": 0.33, "tablet": 0.34}
            
            for session in sessions:
                device_type = session.get('device_type', 'unknown')
                device_counts[device_type] = device_counts.get(device_type, 0) + 1
            
            # Calculate percentages
            device_preferences = {}
            for device, count in device_counts.items():
                device_preferences[device] = count / total_sessions
            
            return device_preferences
            
        except Exception as e:
            print(f"Error calculating device preference for user {user_id}: {e}")
            return {"desktop": 0.33, "mobile": 0.33, "tablet": 0.34}
    
    async def get_time_patterns(self, user_id: str) -> Dict[str, any]:
        """Get time-based browsing patterns"""
        try:
            sessions_collection = self.db[Collections.SESSIONS]
            cursor = sessions_collection.find({"user_id": user_id})
            sessions = await cursor.to_list(length=None)
            
            if not sessions:
                return {
                    "most_active_hour": 12,
                    "most_active_day": "Monday",
                    "activity_distribution": {str(i): 0 for i in range(24)},
                    "weekend_preference": 0.5
                }
            
            hour_counts = [0] * 24
            day_counts = [0] * 7
            weekend_sessions = 0
            
            for session in sessions:
                start_time = session.get('start_time')
                if start_time:
                    hour_counts[start_time.hour] += 1
                    day_counts[start_time.weekday()] += 1
                    
                    if start_time.weekday() >= 5:
                        weekend_sessions += 1
            
            most_active_hour = np.argmax(hour_counts)
            most_active_day_idx = np.argmax(day_counts)
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            most_active_day = days[most_active_day_idx]
            
            activity_distribution = {str(i): count for i, count in enumerate(hour_counts)}
            weekend_preference = weekend_sessions / len(sessions)
            
            return {
                "most_active_hour": int(most_active_hour),
                "most_active_day": most_active_day,
                "activity_distribution": activity_distribution,
                "weekend_preference": float(weekend_preference)
            }
            
        except Exception as e:
            print(f"Error calculating time patterns for user {user_id}: {e}")
            return {
                "most_active_hour": 12,
                "most_active_day": "Monday",
                "activity_distribution": {str(i): 0 for i in range(24)},
                "weekend_preference": 0.5
            }
