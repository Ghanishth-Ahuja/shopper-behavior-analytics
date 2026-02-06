import logging
import sys
from pathlib import Path
from app.config.settings import settings
from datetime import datetime


class CustomFormatter(logging.Formatter):
    """Custom formatter for detailed logging"""
    
    def format(self, record):
        # Add custom fields
        if hasattr(record, 'user_id'):
            record.user_id = f"[User:{record.user_id}]"
        else:
            record.user_id = ""
        
        if hasattr(record, 'request_id'):
            record.request_id = f"[Req:{record.request_id}]"
        else:
            record.request_id = ""
        
        # Format the message
        return (
            f"{datetime.utcnow().isoformat()}Z "
            f"[{record.levelname}] "
            f"{record.user_id}"
            f"{record.request_id} "
            f"[{record.name}] "
            f"{record.getMessage()}"
        )


def setup_logging():
    """Setup application logging"""
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = CustomFormatter()
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for all logs
    file_handler = logging.FileHandler(logs_dir / "app.log")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = CustomFormatter()
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = logging.FileHandler(logs_dir / "errors.log")
    error_handler.setLevel(logging.ERROR)
    error_formatter = CustomFormatter()
    error_handler.setFormatter(error_formatter)
    root_logger.addHandler(error_handler)
    
    # Specific loggers for different components
    setup_component_loggers()
    
    return root_logger


def setup_component_loggers():
    """Setup loggers for different components"""
    
    # ML components
    ml_logger = logging.getLogger("app.ml")
    ml_logger.setLevel(logging.INFO)
    
    # Feature pipeline
    feature_logger = logging.getLogger("app.feature_pipeline")
    feature_logger.setLevel(logging.INFO)
    
    # API endpoints
    api_logger = logging.getLogger("app.api")
    api_logger.setLevel(logging.INFO)
    
    # Background jobs
    bg_logger = logging.getLogger("app.background_jobs")
    bg_logger.setLevel(logging.INFO)
    
    # Database operations
    db_logger = logging.getLogger("app.database")
    db_logger.setLevel(logging.WARNING)  # Less verbose for DB


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class"""
    
    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__module__ + '.' + self.__class__.__name__)
        return self._logger


def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Function {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Function {func.__name__} failed with error: {e}")
            raise
    
    return wrapper


def log_api_request(endpoint: str, method: str, user_id: str = None, request_id: str = None):
    """Log API request"""
    logger = get_logger("app.api")
    
    extra = {}
    if user_id:
        extra['user_id'] = user_id
    if request_id:
        extra['request_id'] = request_id
    
    logger.info(f"API Request: {method} {endpoint}", extra=extra)


def log_api_response(endpoint: str, method: str, status_code: int, duration_ms: float, user_id: str = None, request_id: str = None):
    """Log API response"""
    logger = get_logger("app.api")
    
    extra = {}
    if user_id:
        extra['user_id'] = user_id
    if request_id:
        extra['request_id'] = request_id
    
    logger.info(
        f"API Response: {method} {endpoint} - {status_code} ({duration_ms:.2f}ms)",
        extra=extra
    )


def log_ml_operation(operation: str, model_type: str, metrics: dict = None):
    """Log ML operations"""
    logger = get_logger("app.ml")
    
    message = f"ML Operation: {operation} - Model: {model_type}"
    if metrics:
        message += f" - Metrics: {metrics}"
    
    logger.info(message)


def log_feature_computation(user_id: str, feature_type: str, duration_ms: float):
    """Log feature computation"""
    logger = get_logger("app.feature_pipeline")
    
    logger.info(
        f"Feature Computation: {feature_type} for user {user_id} ({duration_ms:.2f}ms)",
        extra={'user_id': user_id}
    )


def log_database_operation(operation: str, collection: str, duration_ms: float, affected_records: int = 0):
    """Log database operations"""
    logger = get_logger("app.database")
    
    logger.info(
        f"DB Operation: {operation} on {collection} - {affected_records} records ({duration_ms:.2f}ms)"
    )


def log_background_task(task_name: str, status: str, duration_ms: float = None, error: str = None):
    """Log background task execution"""
    logger = get_logger("app.background_jobs")
    
    message = f"Background Task: {task_name} - {status}"
    if duration_ms:
        message += f" ({duration_ms:.2f}ms)"
    if error:
        message += f" - Error: {error}"
    
    if status == "SUCCESS":
        logger.info(message)
    elif status == "FAILED":
        logger.error(message)
    else:
        logger.info(message)


def log_security_event(event_type: str, user_id: str = None, ip_address: str = None, details: str = None):
    """Log security events"""
    logger = get_logger("app.security")
    
    extra = {}
    if user_id:
        extra['user_id'] = user_id
    
    message = f"Security Event: {event_type}"
    if ip_address:
        message += f" - IP: {ip_address}"
    if details:
        message += f" - Details: {details}"
    
    logger.warning(message, extra=extra)


def log_performance_metric(metric_name: str, value: float, unit: str = None, tags: dict = None):
    """Log performance metrics"""
    logger = get_logger("app.performance")
    
    message = f"Performance Metric: {metric_name}={value}"
    if unit:
        message += unit
    if tags:
        message += f" - Tags: {tags}"
    
    logger.info(message)


# Initialize logging when module is imported
setup_logging()
