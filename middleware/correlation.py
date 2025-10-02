"""
Correlation ID Middleware for Request Tracking
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
import logging
from contextvars import ContextVar

# Context variable to store correlation ID across async context
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default=None)

logger = logging.getLogger(__name__)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track requests with correlation IDs
    
    Features:
    - Generates or uses existing X-Correlation-ID header
    - Stores in context variable for access in nested calls
    - Adds to all responses
    - Logs correlation ID with every request
    """
    
    async def dispatch(self, request: Request, call_next):
        # Get or generate correlation ID
        correlation_id = request.headers.get('X-Correlation-ID') or str(uuid.uuid4())
        
        # Store in context variable for access throughout request lifecycle
        correlation_id_var.set(correlation_id)
        
        # Add to request state for easy access
        request.state.correlation_id = correlation_id
        
        # Process request
        response = await call_next(request)
        
        # Add correlation ID to response headers
        response.headers['X-Correlation-ID'] = correlation_id
        
        return response


def get_correlation_id() -> str:
    """
    Get current correlation ID from context
    
    Returns:
        Correlation ID string, or 'no-correlation-id' if not set
    """
    return correlation_id_var.get() or 'no-correlation-id'


class CorrelationIdFilter(logging.Filter):
    """
    Logging filter to add correlation ID to all log records
    """
    
    def filter(self, record):
        record.correlation_id = get_correlation_id()
        return True

