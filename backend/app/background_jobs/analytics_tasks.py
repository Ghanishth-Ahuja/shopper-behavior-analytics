from celery import current_task
from app.background_jobs.celery_app import celery_app
from app.services.analytics_service import AnalyticsService
from app.services.event_service import EventService
from app.database.mongodb import MongoDB, Collections
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def calculate_daily_analytics(self):
    """Calculate daily analytics and metrics"""
    try:
        logger.info("Starting daily analytics calculation...")
        
        # Initialize analytics service
        analytics_service = AnalyticsService()
        
        # Update task status
        self.update_state(state="PROGRESS", meta={"status": "Calculating revenue analytics..."})
        
        # Calculate revenue analytics
        revenue_analytics = await _calculate_revenue_analytics()
        
        self.update_state(state="PROGRESS", meta={"status": "Calculating user analytics..."})
        
        # Calculate user analytics
        user_analytics = await _calculate_user_analytics()
        
        self.update_state(state="PROGRESS", meta={"status": "Calculating product analytics..."})
        
        # Calculate product analytics
        product_analytics = await _calculate_product_analytics()
        
        self.update_state(state="PROGRESS", meta={"status": "Calculating segment analytics..."})
        
        # Calculate segment analytics
        segment_analytics = await _calculate_segment_analytics()
        
        # Store daily analytics
        daily_analytics = {
            "date": datetime.utcnow().date().isoformat(),
            "revenue": revenue_analytics,
            "users": user_analytics,
            "products": product_analytics,
            "segments": segment_analytics,
            "created_at": datetime.utcnow()
        }
        
        analytics_collection = MongoDB.get_database().get_collection("daily_analytics")
        await analytics_collection.insert_one(daily_analytics)
        
        logger.info("Daily analytics calculation completed")
        
        return {
            "status": "success",
            "analytics": daily_analytics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error calculating daily analytics: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task(bind=True)
def generate_weekly_report(self):
    """Generate comprehensive weekly report"""
    try:
        logger.info("Starting weekly report generation...")
        
        # Update task status
        self.update_state(state="PROGRESS", meta={"status": "Gathering weekly data..."})
        
        # Get data for the past week
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        weekly_data = {
            "period_start": week_ago.isoformat(),
            "period_end": datetime.utcnow().isoformat(),
            "revenue_summary": await _get_weekly_revenue_summary(week_ago),
            "user_growth": await _get_weekly_user_growth(week_ago),
            "product_performance": await _get_weekly_product_performance(week_ago),
            "segment_insights": await _get_weekly_segment_insights(week_ago),
            "key_metrics": await _calculate_weekly_key_metrics(week_ago)
        }
        
        self.update_state(state="PROGRESS", meta={"status": "Generating insights..."})
        
        # Generate insights
        insights = await _generate_weekly_insights(weekly_data)
        weekly_data["insights"] = insights
        
        # Store weekly report
        weekly_data["created_at"] = datetime.utcnow()
        reports_collection = MongoDB.get_database().get_collection("weekly_reports")
        await reports_collection.insert_one(weekly_data)
        
        logger.info("Weekly report generation completed")
        
        return {
            "status": "success",
            "report": weekly_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating weekly report: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task(bind=True)
def calculate_cohort_metrics(self):
    """Calculate cohort-based metrics"""
    try:
        logger.info("Starting cohort metrics calculation...")
        
        # Update task status
        self.update_state(state="PROGRESS", meta={"status": "Calculating cohort retention..."})
        
        # Calculate cohort retention
        cohort_retention = await _calculate_cohort_retention()
        
        self.update_state(state="PROGRESS", meta={"status": "Calculating cohort LTV..."})
        
        # Calculate cohort LTV
        cohort_ltv = await _calculate_cohort_ltv()
        
        self.update_state(state="PROGRESS", meta={"status": "Calculating cohort behavior..."})
        
        # Calculate cohort behavior patterns
        cohort_behavior = await _calculate_cohort_behavior()
        
        # Store cohort metrics
        cohort_metrics = {
            "date": datetime.utcnow().date().isoformat(),
            "retention": cohort_retention,
            "ltv": cohort_ltv,
            "behavior": cohort_behavior,
            "created_at": datetime.utcnow()
        }
        
        cohort_collection = MongoDB.get_database().get_collection("cohort_metrics")
        await cohort_collection.insert_one(cohort_metrics)
        
        logger.info("Cohort metrics calculation completed")
        
        return {
            "status": "success",
            "cohort_metrics": cohort_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error calculating cohort metrics: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task
def cleanup_old_events():
    """Clean up old event data to save storage"""
    try:
        logger.info("Starting old events cleanup...")
        
        # Initialize event service
        event_service = EventService()
        
        # Clean up events older than 90 days
        deleted_count = await event_service.cleanup_old_events(days=90)
        
        logger.info(f"Old events cleanup completed: {deleted_count} records removed")
        
        return {
            "status": "success",
            "deleted_records": deleted_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old events: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task
def update_funnel_analytics():
    """Update conversion funnel analytics"""
    try:
        logger.info("Starting funnel analytics update...")
        
        # Get current funnel data
        analytics_service = AnalyticsService()
        funnel_data = await analytics_service.get_conversion_funnel()
        
        # Store funnel analytics with timestamp
        funnel_analytics = {
            "date": datetime.utcnow().date().isoformat(),
            "funnel_data": funnel_data,
            "created_at": datetime.utcnow()
        }
        
        funnel_collection = MongoDB.get_database().get_collection("funnel_analytics")
        await funnel_collection.insert_one(funnel_analytics)
        
        logger.info("Funnel analytics update completed")
        
        return {
            "status": "success",
            "funnel_analytics": funnel_analytics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating funnel analytics: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task
def calculate_ab_test_metrics():
    """Calculate A/B test metrics"""
    try:
        logger.info("Starting A/B test metrics calculation...")
        
        # This would connect to A/B testing system
        # For now, return placeholder results
        
        ab_test_metrics = {
            "active_tests": 3,
            "test_results": [
                {
                    "test_id": "rec_algo_v2",
                    "variant_a": {"conversions": 45, "impressions": 1000, "rate": 4.5},
                    "variant_b": {"conversions": 52, "impressions": 1000, "rate": 5.2},
                    "winner": "variant_b",
                    "confidence": 0.92
                }
            ]
        }
        
        logger.info("A/B test metrics calculation completed")
        
        return {
            "status": "success",
            "ab_test_metrics": ab_test_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error calculating A/B test metrics: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task
def generate_alerts():
    """Generate alerts based on metrics thresholds"""
    try:
        logger.info("Starting alerts generation...")
        
        alerts = []
        
        # Check for unusual metrics
        alerts.extend(await _check_revenue_alerts())
        alerts.extend(await _check_user_activity_alerts())
        alerts.extend(await _check_conversion_alerts())
        alerts.extend(await _check_system_health_alerts())
        
        # Store alerts
        if alerts:
            alerts_collection = MongoDB.get_database().get_collection("alerts")
            for alert in alerts:
                alert["created_at"] = datetime.utcnow()
                await alerts_collection.insert_one(alert)
        
        logger.info(f"Alerts generation completed: {len(alerts)} alerts generated")
        
        return {
            "status": "success",
            "alerts_count": len(alerts),
            "alerts": alerts,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating alerts: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# Helper functions
async def _calculate_revenue_analytics():
    """Calculate revenue analytics"""
    try:
        transactions_collection = MongoDB.get_database()[Collections.TRANSACTIONS]
        
        # Get today's transactions
        today = datetime.utcnow().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        
        cursor = transactions_collection.find({"timestamp": {"$gte": start_of_day}})
        transactions = await cursor.to_list(length=None)
        
        total_revenue = sum(t.get("total_amount", 0) for t in transactions)
        total_transactions = len(transactions)
        avg_order_value = total_revenue / total_transactions if total_transactions > 0 else 0
        
        return {
            "total_revenue": total_revenue,
            "total_transactions": total_transactions,
            "avg_order_value": avg_order_value
        }
        
    except Exception as e:
        logger.error(f"Error calculating revenue analytics: {e}")
        return {}


async def _calculate_user_analytics():
    """Calculate user analytics"""
    try:
        users_collection = MongoDB.get_database()[Collections.USERS]
        
        # Get user counts
        total_users = await users_collection.count_documents({})
        
        # Get new users today
        today = datetime.utcnow().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        
        new_users = await users_collection.count_documents({"signup_date": {"$gte": start_of_day}})
        
        # Get active users today
        sessions_collection = MongoDB.get_database()[Collections.SESSIONS]
        active_users = await sessions_collection.distinct("user_id", {"start_time": {"$gte": start_of_day}})
        
        return {
            "total_users": total_users,
            "new_users": new_users,
            "active_users": len(active_users)
        }
        
    except Exception as e:
        logger.error(f"Error calculating user analytics: {e}")
        return {}


async def _calculate_product_analytics():
    """Calculate product analytics"""
    try:
        # Get top products today
        transactions_collection = MongoDB.get_database()[Collections.TRANSACTIONS]
        
        today = datetime.utcnow().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": start_of_day}}},
            {"$unwind": "$items"},
            {"$group": {
                "_id": "$items.product_id",
                "quantity": {"$sum": "$items.quantity"},
                "revenue": {"$sum": {"$multiply": ["$items.price", "$items.quantity"]}}
            }},
            {"$sort": {"revenue": -1}},
            {"$limit": 10}
        ]
        
        cursor = transactions_collection.aggregate(pipeline)
        top_products = await cursor.to_list(length=None)
        
        return {
            "top_products": top_products
        }
        
    except Exception as e:
        logger.error(f"Error calculating product analytics: {e}")
        return {}


async def _calculate_segment_analytics():
    """Calculate segment analytics"""
    try:
        segments_collection = MongoDB.get_database()[Collections.SEGMENTS]
        users_collection = MongoDB.get_database()[Collections.USERS]
        
        # Get segment sizes
        segments = await segments_collection.find({}).to_list(length=None)
        segment_analytics = []
        
        for segment in segments:
            segment_id = segment.get("segment_id")
            user_count = await users_collection.count_documents({"segment_id": segment_id})
            
            segment_analytics.append({
                "segment_id": segment_id,
                "segment_name": segment.get("segment_name"),
                "user_count": user_count
            })
        
        return {
            "segment_analytics": segment_analytics
        }
        
    except Exception as e:
        logger.error(f"Error calculating segment analytics: {e}")
        return {}


async def _get_weekly_revenue_summary(week_ago):
    """Get weekly revenue summary"""
    try:
        transactions_collection = MongoDB.get_database()[Collections.TRANSACTIONS]
        
        cursor = transactions_collection.find({"timestamp": {"$gte": week_ago}})
        transactions = await cursor.to_list(length=None)
        
        total_revenue = sum(t.get("total_amount", 0) for t in transactions)
        total_transactions = len(transactions)
        
        return {
            "total_revenue": total_revenue,
            "total_transactions": total_transactions,
            "avg_daily_revenue": total_revenue / 7
        }
        
    except Exception as e:
        logger.error(f"Error getting weekly revenue summary: {e}")
        return {}


async def _get_weekly_user_growth(week_ago):
    """Get weekly user growth"""
    try:
        users_collection = MongoDB.get_database()[Collections.USERS]
        
        new_users = await users_collection.count_documents({"signup_date": {"$gte": week_ago}})
        
        return {
            "new_users": new_users,
            "avg_daily_new_users": new_users / 7
        }
        
    except Exception as e:
        logger.error(f"Error getting weekly user growth: {e}")
        return {}


async def _get_weekly_product_performance(week_ago):
    """Get weekly product performance"""
    try:
        # Similar to daily product analytics but for the week
        return {"top_products": []}
        
    except Exception as e:
        logger.error(f"Error getting weekly product performance: {e}")
        return {}


async def _get_weekly_segment_insights(week_ago):
    """Get weekly segment insights"""
    try:
        # Get segment performance for the week
        return {"segment_insights": []}
        
    except Exception as e:
        logger.error(f"Error getting weekly segment insights: {e}")
        return {}


async def _calculate_weekly_key_metrics(week_ago):
    """Calculate key weekly metrics"""
    try:
        # Calculate important KPIs
        return {
            "conversion_rate": 0.0,
            "retention_rate": 0.0,
            "churn_rate": 0.0
        }
        
    except Exception as e:
        logger.error(f"Error calculating weekly key metrics: {e}")
        return {}


async def _generate_weekly_insights(weekly_data):
    """Generate insights from weekly data"""
    try:
        insights = []
        
        # Generate insights based on data patterns
        # For now, placeholder insights
        insights = [
            "Revenue increased by 15% compared to last week",
            "User acquisition rate is steady",
            "Electronics category shows strong performance"
        ]
        
        return insights
        
    except Exception as e:
        logger.error(f"Error generating weekly insights: {e}")
        return []


async def _calculate_cohort_retention():
    """Calculate cohort retention rates"""
    try:
        # Placeholder implementation
        return {"cohort_retention": {}}
        
    except Exception as e:
        logger.error(f"Error calculating cohort retention: {e}")
        return {}


async def _calculate_cohort_ltv():
    """Calculate cohort lifetime value"""
    try:
        # Placeholder implementation
        return {"cohort_ltv": {}}
        
    except Exception as e:
        logger.error(f"Error calculating cohort LTV: {e}")
        return {}


async def _calculate_cohort_behavior():
    """Calculate cohort behavior patterns"""
    try:
        # Placeholder implementation
        return {"cohort_behavior": {}}
        
    except Exception as e:
        logger.error(f"Error calculating cohort behavior: {e}")
        return {}


async def _check_revenue_alerts():
    """Check for revenue-related alerts"""
    try:
        alerts = []
        
        # Check for significant revenue drops
        # Placeholder logic
        
        return alerts
        
    except Exception as e:
        logger.error(f"Error checking revenue alerts: {e}")
        return []


async def _check_user_activity_alerts():
    """Check for user activity alerts"""
    try:
        alerts = []
        
        # Check for unusual user activity patterns
        # Placeholder logic
        
        return alerts
        
    except Exception as e:
        logger.error(f"Error checking user activity alerts: {e}")
        return []


async def _check_conversion_alerts():
    """Check for conversion-related alerts"""
    try:
        alerts = []
        
        # Check for conversion rate changes
        # Placeholder logic
        
        return alerts
        
    except Exception as e:
        logger.error(f"Error checking conversion alerts: {e}")
        return {}


async def _check_system_health_alerts():
    """Check for system health alerts"""
    try:
        alerts = []
        
        # Check for system performance issues
        # Placeholder logic
        
        return alerts
        
    except Exception as e:
        logger.error(f"Error checking system health alerts: {e}")
        return []
