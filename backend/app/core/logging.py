import logging
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pythonjsonlogger import jsonlogger
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import traceback
import uuid

# Log levels
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


class ContextFilter(logging.Filter):
    """Add context information to log records."""
    
    def __init__(self, app_name: str = "rideswift", environment: str = "development"):
        super().__init__()
        self.app_name = app_name
        self.environment = environment
    
    def filter(self, record):
        record.app_name = self.app_name
        record.environment = self.environment
        record.timestamp = datetime.utcnow().isoformat()
        
        # Add request context if available
        if hasattr(record, "request_id"):
            record.request_id = record.request_id
        else:
            record.request_id = None
        
        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        super().add_fields(log_record, record, message_dict)
        
        # Add custom fields
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["timestamp"] = datetime.utcnow().isoformat()
        
        # Add location information
        log_record["location"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }
        
        # Add exception information if present
        if record.exc_info:
            log_record["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }
        
        # Remove redundant fields
        for field in ["msg", "args", "created", "msecs", "relativeCreated", "exc_info", "exc_text"]:
            log_record.pop(field, None)


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    app_name: str = "rideswift",
    environment: str = "development"
):
    """Configure logging for the application."""
    
    # Get log level
    level = LOG_LEVELS.get(log_level.upper(), logging.INFO)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Add context filter
    context_filter = ContextFilter(app_name, environment)
    console_handler.addFilter(context_filter)
    
    # Set formatter based on format type
    if log_format == "json":
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s",
            timestamp=True,
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Set log levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
    
    return root_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses."""
    
    def __init__(self, app, logger: Optional[logging.Logger] = None):
        super().__init__(app)
        self.logger = logger or logging.getLogger(__name__)
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Start timer
        start_time = time.time()
        
        # Log request
        self.logger.info(
            "HTTP Request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            self.logger.info(
                "HTTP Response",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                }
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Log error
            self.logger.error(
                "HTTP Error",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration * 1000, 2),
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True
            )
            
            # Re-raise the exception
            raise


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    logger = logging.getLogger(name)
    
    # Add custom log methods
    def log_event(event_name: str, **kwargs):
        logger.info(f"Event: {event_name}", extra={"event": event_name, "event_data": kwargs})
    
    def log_metric(metric_name: str, value: float, **kwargs):
        logger.info(f"Metric: {metric_name}", extra={"metric": metric_name, "value": value, "tags": kwargs})
    
    logger.log_event = log_event
    logger.log_metric = log_metric
    
    return logger
