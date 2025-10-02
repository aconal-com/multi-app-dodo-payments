"""
Structured Logging Configuration
"""
import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any
from config.config import get_settings

settings = get_settings()


class JsonFormatter(logging.Formatter):
    """
    JSON formatter for structured logging
    
    Outputs logs in JSON format for easy parsing and analysis
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, 'correlation_id', 'no-correlation-id'),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        # Add common fields
        log_data["module"] = record.module
        log_data["function"] = record.funcName
        log_data["line"] = record.lineno
        
        # Add environment
        log_data["environment"] = settings.ENVIRONMENT
        
        return json.dumps(log_data)


class DevelopmentFormatter(logging.Formatter):
    """
    Human-readable formatter for development
    """
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # Get correlation ID
        correlation_id = getattr(record, 'correlation_id', 'no-correlation-id')[:8]
        
        # Format timestamp
        timestamp = datetime.utcnow().strftime('%H:%M:%S.%f')[:-3]
        
        # Color the level
        level = record.levelname
        color = self.COLORS.get(level, self.COLORS['RESET'])
        colored_level = f"{color}{level:8s}{self.COLORS['RESET']}"
        
        # Format message
        message = record.getMessage()
        
        # Build log line
        log_line = f"{timestamp} | {correlation_id} | {colored_level} | {record.name:30s} | {message}"
        
        # Add exception if present
        if record.exc_info:
            log_line += "\n" + self.formatException(record.exc_info)
        
        return log_line


class MixpanelHandler(logging.Handler):
    """
    Logging handler that automatically sends logs to Mixpanel as events
    
    Converts structured logs into Mixpanel events without touching business logic.
    Only sends INFO+ logs with extra_fields containing user_id.
    """
    
    def __init__(self):
        super().__init__()
        self._mixpanel = None
        self._enabled = settings.MIXPANEL_ENABLED
        
    def _get_mixpanel(self):
        """Lazy load Mixpanel client"""
        if not self._enabled:
            return None
            
        if self._mixpanel is None:
            try:
                from mixpanel import Mixpanel, Consumer
                
                # Initialize with data residency support
                if settings.MIXPANEL_DATA_RESIDENCY == "EU":
                    consumer = Consumer(api_host="api-eu.mixpanel.com")
                elif settings.MIXPANEL_DATA_RESIDENCY == "IN":
                    consumer = Consumer(api_host="api-in.mixpanel.com")
                else:
                    consumer = None
                
                self._mixpanel = Mixpanel(
                    settings.MIXPANEL_PROJECT_TOKEN,
                    consumer=consumer
                ) if consumer else Mixpanel(settings.MIXPANEL_PROJECT_TOKEN)
                
            except ImportError:
                self._enabled = False
                return None
            except Exception:
                self._enabled = False
                return None
        
        return self._mixpanel
    
    def emit(self, record: logging.LogRecord):
        """Send log to Mixpanel as event"""
        try:
            # Only send INFO+ logs
            if record.levelno < logging.INFO:
                return
            
            # Only send logs with extra_fields containing user_id
            if not hasattr(record, 'extra_fields'):
                return
            
            extra = record.extra_fields
            user_id = extra.get('user_id')
            
            if not user_id:
                return
            
            mp = self._get_mixpanel()
            if not mp:
                return
            
            # Convert log message to event name
            event_name = self._extract_event_name(record.getMessage(), record.levelname)
            
            # Build event properties
            properties = {
                "service": "payments-microservice",
                "environment": settings.ENVIRONMENT,
                "level": record.levelname,
                "module": record.module,
                "function": record.funcName,
            }
            
            # Add correlation ID
            if hasattr(record, 'correlation_id'):
                properties["correlation_id"] = record.correlation_id
            
            # Add all extra_fields as properties
            properties.update(extra)
            
            # Send to Mixpanel (async, non-blocking)
            mp.track(user_id, event_name, properties)
            
        except Exception:
            # Never fail business logic due to analytics
            pass
    
    @staticmethod
    def _extract_event_name(message: str, level: str) -> str:
        """Convert log message to event name"""
        msg_lower = message.lower()
        
        # Payment events (order matters - most specific first)
        if "payment verification started" in msg_lower:
            return "Payment Verification Started"
        elif "payment failure detected" in msg_lower:
            return "Payment Failure Detected"
        elif "payment failure recorded" in msg_lower:
            return "Payment Failure Recorded"
        elif "payment" in msg_lower and "processed successfully" in msg_lower:
            return "Payment Succeeded"
        elif "payment" in msg_lower and ("fail" in msg_lower or "failure" in msg_lower):
            return "Payment Failed"
        
        # Checkout events
        elif "checkout" in msg_lower and "created" in msg_lower:
            return "Checkout Created"
        
        # Subscription events (order matters - most specific first)
        elif "subscription renewal verification started" in msg_lower:
            return "Subscription Renewal Started"
        elif "subscription" in msg_lower and "renewed successfully" in msg_lower:
            return "Subscription Renewed"
        elif "subscription cancellation detected" in msg_lower:
            return "Subscription Cancellation Detected"
        elif "subscription failure detected" in msg_lower:
            return "Subscription Failure Detected"
        elif "subscription" in msg_lower and "failure recorded" in msg_lower:
            return "Subscription Failure Recorded"
        elif "subscription" in msg_lower and ("cancel" in msg_lower or "cancelled" in msg_lower):
            return "Subscription Cancelled"
        elif "subscription" in msg_lower and ("fail" in msg_lower or "failure" in msg_lower):
            return "Subscription Failed"
        
        # Credit events
        elif "credits granted to user" in msg_lower:
            return "Credits Granted"
        elif "credit" in msg_lower and "added" in msg_lower:
            return "Credits Added"
        elif "credit" in msg_lower and "deducted" in msg_lower:
            return "Credits Deducted"
        
        # Webhook events
        elif "webhook received" in msg_lower:
            return "Webhook Received"
        
        # Fallback
        else:
            return f"{level}: {message[:50]}"


def setup_logging():
    """
    Configure logging for the application
    
    - Production: JSON structured logs
    - Development: Human-readable colored logs
    - Mixpanel: Automatic event tracking from logs
    """
    from middleware.correlation import CorrelationIdFilter
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Choose formatter based on environment
    if settings.is_production:
        formatter = JsonFormatter()
    else:
        formatter = DevelopmentFormatter()
    
    console_handler.setFormatter(formatter)
    
    # Add correlation ID filter
    console_handler.addFilter(CorrelationIdFilter())
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Add Mixpanel handler if enabled
    if settings.MIXPANEL_ENABLED:
        mixpanel_handler = MixpanelHandler()
        mixpanel_handler.setLevel(logging.INFO)  # Only INFO+ logs
        mixpanel_handler.addFilter(CorrelationIdFilter())
        root_logger.addHandler(mixpanel_handler)
    
    # Set levels for noisy libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter to add extra context to logs
    """
    
    def process(self, msg, kwargs):
        # Add extra_fields to record
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        
        # Merge context
        if self.extra:
            for key, value in self.extra.items():
                kwargs['extra'][key] = value
        
        return msg, kwargs


def get_logger_with_context(name: str, **context) -> LoggerAdapter:
    """
    Get a logger with additional context
    
    Args:
        name: Logger name
        **context: Additional context fields
    
    Returns:
        Logger adapter with context
    """
    logger = get_logger(name)
    return LoggerAdapter(logger, context)

