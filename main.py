"""
Dodo Payments Microservice - Main Application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from config.config import get_settings
from services.database import init_db
from routers import payments, products, credits, apps
from middleware.correlation import CorrelationIdMiddleware
from utils.logger import setup_logging, get_logger

settings = get_settings()

# Setup structured logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events - startup and shutdown"""
    # Startup
    logger.info("🚀 Starting Dodo Payments Microservice...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Port: {settings.SERVICE_PORT}")
    
    # Initialize database
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down Dodo Payments Microservice...")


# Create FastAPI app
app = FastAPI(
    title="Dodo Payments Microservice",
    description="Autonomous payment processing service for multiple applications",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None
)

# Add correlation ID middleware (first, so it's available to all other middleware)
app.add_middleware(CorrelationIdMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with timing and correlation"""
    start_time = time.time()
    
    # Log request start
    logger.info(
        f"Request started: {request.method} {request.url.path}",
        extra={
            'extra_fields': {
                'method': request.method,
                'path': request.url.path,
                'query_params': dict(request.query_params),
                'client_host': request.client.host if request.client else None
            }
        }
    )
    
    # Process request
    try:
        response = await call_next(request)
    except Exception as e:
        # Log error and re-raise
        logger.error(
            f"Request failed: {request.method} {request.url.path}",
            exc_info=True,
            extra={
                'extra_fields': {
                    'method': request.method,
                    'path': request.url.path,
                    'error': str(e)
                }
            }
        )
        raise
    
    # Calculate process time
    process_time = (time.time() - start_time) * 1000
    
    # Log response
    logger.info(
        f"Request completed: {request.method} {request.url.path}",
        extra={
            'extra_fields': {
                'method': request.method,
                'path': request.url.path,
                'status_code': response.status_code,
                'process_time_ms': round(process_time, 2)
            }
        }
    )
    
    # Add custom headers
    response.headers["X-Process-Time"] = str(round(process_time, 2))
    
    return response


# Include routers
app.include_router(payments.router)
app.include_router(products.router)
app.include_router(credits.router)
app.include_router(apps.router)


# Root endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Dodo Payments Microservice",
        "version": "1.0.0",
        "status": "operational",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if not settings.is_production else "disabled"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    logger.error(f"❌ Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if not settings.is_production else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=not settings.is_production,
        log_level=settings.LOG_LEVEL.lower()
    )

