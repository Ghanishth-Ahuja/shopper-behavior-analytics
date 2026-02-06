from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import psutil
import asyncio
from app.utils.logger import get_logger
from app.database.mongodb import MongoDB, Collections

logger = get_logger(__name__)


class MetricsCollector:
    """Collect and store application metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.counters = {}
        self.gauges = {}
        self.histograms = {}
    
    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Increment a counter metric"""
        key = self._make_key(name, tags)
        self.counters[key] = self.counters.get(key, 0) + value
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric"""
        key = self._make_key(name, tags)
        self.gauges[key] = value
    
    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a histogram metric"""
        key = self._make_key(name, tags)
        if key not in self.histograms:
            self.histograms[key] = []
        self.histograms[key].append(value)
        
        # Keep only last 1000 values to prevent memory issues
        if len(self.histograms[key]) > 1000:
            self.histograms[key] = self.histograms[key][-1000:]
    
    def _make_key(self, name: str, tags: Dict[str, str] = None) -> str:
        """Create metric key with tags"""
        if tags:
            tag_str = ",".join([f"{k}={v}" for k, v in sorted(tags.items())])
            return f"{name}{{{tag_str}}}"
        return name
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        summary = {
            "counters": self.counters.copy(),
            "gauges": self.gauges.copy(),
            "histograms": {}
        }
        
        # Calculate histogram statistics
        for key, values in self.histograms.items():
            if values:
                summary["histograms"][key] = {
                    "count": len(values),
                    "sum": sum(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "p50": self._percentile(values, 50),
                    "p95": self._percentile(values, 95),
                    "p99": self._percentile(values, 99)
                }
        
        return summary
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()


class PerformanceMonitor:
    """Monitor application performance"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
    
    async def collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics_collector.set_gauge("system_cpu_percent", cpu_percent)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.metrics_collector.set_gauge("system_memory_percent", memory.percent)
            self.metrics_collector.set_gauge("system_memory_used_bytes", memory.used)
            self.metrics_collector.set_gauge("system_memory_available_bytes", memory.available)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            self.metrics_collector.set_gauge("system_disk_percent", disk.percent)
            self.metrics_collector.set_gauge("system_disk_used_bytes", disk.used)
            self.metrics_collector.set_gauge("system_disk_free_bytes", disk.free)
            
            # Process metrics
            process = psutil.Process()
            self.metrics_collector.set_gauge("process_cpu_percent", process.cpu_percent())
            self.metrics_collector.set_gauge("process_memory_rss", process.memory_info().rss)
            self.metrics_collector.set_gauge("process_memory_vms", process.memory_info().vms)
            self.metrics_collector.set_gauge("process_num_threads", process.num_threads())
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def collect_database_metrics(self):
        """Collect database metrics"""
        try:
            db = MongoDB.get_database()
            
            # Collection counts
            collections = [
                Collections.USERS,
                Collections.PRODUCTS,
                Collections.TRANSACTIONS,
                Collections.REVIEWS,
                Collections.SESSIONS,
                Collections.SEGMENTS,
                Collections.USER_FEATURES
            ]
            
            for collection_name in collections:
                count = await db[collection_name].count_documents({})
                self.metrics_collector.set_gauge(
                    "db_collection_count", 
                    count, 
                    {"collection": collection_name}
                )
            
            # Database stats (if available)
            try:
                stats = await db.command("dbStats")
                self.metrics_collector.set_gauge("db_data_size", stats.get("dataSize", 0))
                self.metrics_collector.set_gauge("db_index_size", stats.get("indexSize", 0))
                self.metrics_collector.set_gauge("db_storage_size", stats.get("storageSize", 0))
            except Exception:
                pass  # Stats command might not be available
            
        except Exception as e:
            logger.error(f"Error collecting database metrics: {e}")
    
    async def collect_application_metrics(self):
        """Collect application-level metrics"""
        try:
            # Active users (last 5 minutes)
            five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
            sessions_collection = MongoDB.get_database()[Collections.SESSIONS]
            active_sessions = await sessions_collection.count_documents({
                "start_time": {"$gte": five_minutes_ago}
            })
            self.metrics_collector.set_gauge("active_users", active_sessions)
            
            # Recent transactions (last hour)
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            transactions_collection = MongoDB.get_database()[Collections.TRANSACTIONS]
            recent_transactions = await transactions_collection.count_documents({
                "timestamp": {"$gte": one_hour_ago}
            })
            self.metrics_collector.set_gauge("recent_transactions", recent_transactions)
            
            # Model performance metrics
            await self._collect_ml_metrics()
            
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
    
    async def _collect_ml_metrics(self):
        """Collect ML model performance metrics"""
        try:
            # Get recent recommendation feedback
            feedback_collection = MongoDB.get_database().get_collection("recommendation_feedback")
            one_day_ago = datetime.utcnow() - timedelta(days=1)
            
            cursor = feedback_collection.find({"timestamp": {"$gte": one_day_ago}})
            feedback = await cursor.to_list(length=None)
            
            if feedback:
                total_feedback = len(feedback)
                clicks = len([f for f in feedback if f.get("feedback") == "click"])
                purchases = len([f for f in feedback if f.get("feedback") == "purchase"])
                
                self.metrics_collector.set_gauge("recommendation_click_rate", clicks / total_feedback * 100)
                self.metrics_collector.set_gauge("recommendation_conversion_rate", purchases / total_feedback * 100)
                self.metrics_collector.set_gauge("recommendation_total_feedback", total_feedback)
            
        except Exception as e:
            logger.error(f"Error collecting ML metrics: {e}")


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP request metrics"""
    
    def __init__(self, app, metrics_collector: MetricsCollector):
        super().__init__(app)
        self.metrics_collector = metrics_collector
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        duration_ms = duration * 1000
        
        # Record metrics
        method = request.method
        path = request.url.path
        status_code = response.status_code
        
        # Request counter
        self.metrics_collector.increment_counter(
            "http_requests_total",
            tags={"method": method, "path": path, "status": str(status_code)}
        )
        
        # Request duration histogram
        self.metrics_collector.record_histogram(
            "http_request_duration_ms",
            duration_ms,
            tags={"method": method, "path": path}
        )
        
        # Error counter
        if status_code >= 400:
            self.metrics_collector.increment_counter(
                "http_errors_total",
                tags={"method": method, "path": path, "status": str(status_code)}
            )
        
        return response


class HealthChecker:
    """Health check utilities"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
    
    async def check_health(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }
        
        # Check database connection
        db_health = await self._check_database()
        health_status["checks"]["database"] = db_health
        
        # Check Redis connection
        redis_health = await self._check_redis()
        health_status["checks"]["redis"] = redis_health
        
        # Check system resources
        system_health = await self._check_system()
        health_status["checks"]["system"] = system_health
        
        # Check ML models
        ml_health = await self._check_ml_models()
        health_status["checks"]["ml_models"] = ml_health
        
        # Determine overall status
        unhealthy_checks = [
            name for name, check in health_status["checks"].items()
            if check["status"] != "healthy"
        ]
        
        if unhealthy_checks:
            health_status["status"] = "unhealthy"
            health_status["unhealthy_checks"] = unhealthy_checks
        
        return health_status
    
    async def _check_database(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            db = MongoDB.get_database()
            
            # Test connection with ping
            await db.command("ping")
            
            # Check if we can read from a collection
            await db[Collections.USERS].count_documents({"limit": 1})
            
            return {
                "status": "healthy",
                "message": "Database connection successful",
                "response_time_ms": 0  # Would measure actual response time
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}"
            }
    
    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis health"""
        try:
            from app.utils.security import get_redis_client
            
            r = await get_redis_client()
            
            # Test connection
            await r.ping()
            
            # Test set/get
            test_key = "health_check_test"
            await r.set(test_key, "test", ex=10)
            value = await r.get(test_key)
            await r.delete(test_key)
            
            if value:
                return {
                    "status": "healthy",
                    "message": "Redis connection successful"
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": "Redis read/write test failed"
                }
                
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Redis connection failed: {str(e)}"
            }
    
    async def _check_system(self) -> Dict[str, Any]:
        """Check system resources"""
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Check memory usage
            memory = psutil.virtual_memory()
            
            # Check disk usage
            disk = psutil.disk_usage('/')
            
            # Determine if resources are healthy
            cpu_healthy = cpu_percent < 90
            memory_healthy = memory.percent < 90
            disk_healthy = disk.percent < 90
            
            overall_healthy = cpu_healthy and memory_healthy and disk_healthy
            
            return {
                "status": "healthy" if overall_healthy else "warning",
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "message": "System resources within limits" if overall_healthy else "High resource usage detected"
            }
            
        except Exception as e:
            logger.error(f"System health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"System check failed: {str(e)}"
            }
    
    async def _check_ml_models(self) -> Dict[str, Any]:
        """Check ML model health"""
        try:
            # Check if segmentation model exists
            from app.ml.segmentation_model import SegmentationModel
            
            segmentation_model = SegmentationModel()
            model_loaded = await segmentation_model._load_model()
            
            # Check if recommendation engine is accessible
            from app.ml.recommendation_engine import RecommendationEngine
            
            recommendation_engine = RecommendationEngine()
            
            # Simple health check - try to get recommendations for a dummy user
            try:
                recommendations = await recommendation_engine.get_user_recommendations("dummy_user", limit=1)
                recommendations_healthy = True
            except:
                recommendations_healthy = False
            
            overall_healthy = model_loaded and recommendations_healthy
            
            return {
                "status": "healthy" if overall_healthy else "warning",
                "segmentation_model_loaded": model_loaded,
                "recommendation_engine_healthy": recommendations_healthy,
                "message": "ML models operational" if overall_healthy else "Some ML models not available"
            }
            
        except Exception as e:
            logger.error(f"ML models health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"ML models check failed: {str(e)}"
            }


# Global instances
metrics_collector = MetricsCollector()
performance_monitor = PerformanceMonitor()
health_checker = HealthChecker()


async def start_monitoring():
    """Start background monitoring tasks"""
    asyncio.create_task(_monitoring_loop())


async def _monitoring_loop():
    """Background monitoring loop"""
    while True:
        try:
            # Collect all metrics
            await performance_monitor.collect_system_metrics()
            await performance_monitor.collect_database_metrics()
            await performance_monitor.collect_application_metrics()
            
            # Sleep for 30 seconds
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            await asyncio.sleep(60)  # Wait longer on error
