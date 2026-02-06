"""
Utility modules for the Shopper Behavior Analytics application.

This package contains:
- logger: Logging configuration and utilities
- security: Security management and authentication
- monitoring: Performance monitoring and health checks
"""

from .logger import (
    get_logger,
    LoggerMixin,
    log_function_call,
    log_api_request,
    log_api_response,
    log_ml_operation,
    log_feature_computation,
    log_database_operation,
    log_background_task,
    log_security_event,
    log_performance_metric
)

from .security import (
    SecurityManager,
    RateLimiter,
    DataMasking,
    InputValidator,
    SecurityHeaders,
    AuditLogger,
    security_manager,
    rate_limiter,
    data_masking,
    input_validator,
    security_headers,
    audit_logger
)

from .monitoring import (
    MetricsCollector,
    PerformanceMonitor,
    MetricsMiddleware,
    HealthChecker,
    metrics_collector,
    performance_monitor,
    health_checker,
    start_monitoring
)

__all__ = [
    # Logger
    "get_logger",
    "LoggerMixin",
    "log_function_call",
    "log_api_request",
    "log_api_response",
    "log_ml_operation",
    "log_feature_computation",
    "log_database_operation",
    "log_background_task",
    "log_security_event",
    "log_performance_metric",
    
    # Security
    "SecurityManager",
    "RateLimiter",
    "DataMasking",
    "InputValidator",
    "SecurityHeaders",
    "AuditLogger",
    "security_manager",
    "rate_limiter",
    "data_masking",
    "input_validator",
    "security_headers",
    "audit_logger",
    
    # Monitoring
    "MetricsCollector",
    "PerformanceMonitor",
    "MetricsMiddleware",
    "HealthChecker",
    "metrics_collector",
    "performance_monitor",
    "health_checker",
    "start_monitoring"
]
