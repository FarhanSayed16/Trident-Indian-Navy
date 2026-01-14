"""
TRIDENT Backend - Main FastAPI Application
ML-Enabled Network Anomaly Detection Module for WAF
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import check_db_connection
from app.logging_config import setup_logging
from app.middleware import RequestLoggingMiddleware, ErrorLoggingMiddleware
from app.middleware.rate_limiting import RateLimitingMiddleware
from app.services.model_manager import ModelManager

# Import routers
from app.routers import traffic, detection, baseline, recommendations, alerts, metrics, waf, feedback, retraining, model_version, feedback_analytics

# Setup structured logging
setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Check database connection
    if check_db_connection():
        logger.info("Database connection: OK")
    else:
        logger.warning("Database connection: FAILED - Check your DATABASE_URL")
    
    # Load ML models
    model_manager = ModelManager()
    app.state.model_manager = model_manager  # Store in app state for access
    
    if model_manager.load_latest_models():
        logger.info(f"ML models loaded successfully (version: {model_manager.model_version})")
    else:
        logger.warning("ML models not loaded - detection will not work until models are available")
        logger.warning("To train models, run: python scripts/train_models.py --config scripts/train_config.json")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")
    # Models will be cleaned up automatically


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="ML-Enabled Network Anomaly Detection Module for WAF Integration",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add middleware (order matters - first added is outermost)
# Rate limiting should be first to prevent abuse
# Use higher limits in development to avoid blocking dashboard auto-refresh
if settings.ENVIRONMENT == "development":
    # Development: Very high limits to avoid blocking during testing/demo
    app.add_middleware(
        RateLimitingMiddleware,
        requests_per_minute=1000,  # High limit for development
        requests_per_hour=100000    # Very high limit for development
    )
else:
    # Production: Use configured limits
    app.add_middleware(
        RateLimitingMiddleware,
        requests_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
        requests_per_hour=settings.RATE_LIMIT_REQUESTS_PER_HOUR
    )
app.add_middleware(ErrorLoggingMiddleware)  # Catch all exceptions
app.add_middleware(RequestLoggingMiddleware)  # Log all requests/responses

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns the health status of the application and its dependencies.
    """
    import asyncio
    
    # Check database with timeout to prevent hanging
    try:
        db_status = await asyncio.wait_for(
            asyncio.to_thread(check_db_connection),
            timeout=2.0
        )
    except asyncio.TimeoutError:
        db_status = False
        logger.warning("Database connection check timed out")
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        db_status = False
    
    # Check model availability from ModelManager
    try:
        model_manager = getattr(app.state, 'model_manager', None)
        if model_manager and model_manager.is_loaded():
            model_status = "available"
            model_info = model_manager.get_model_info()
        else:
            model_status = "unavailable"
            model_info = {"loaded": False}
    except Exception as e:
        logger.error(f"Model check failed: {e}")
        model_status = "unavailable"
        model_info = {"loaded": False, "error": str(e)}
    
    # Determine overall status
    overall_status = "healthy" if (db_status and model_status == "available") else "degraded"
    
    return {
        "status": overall_status,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected" if db_status else "disconnected",
        "model": model_status,
        "model_info": model_info,
        "service_status": "operational"
    }


# Include routers
app.include_router(traffic.router, prefix=settings.API_V1_PREFIX, tags=["traffic"])
app.include_router(baseline.router, prefix=settings.API_V1_PREFIX, tags=["baseline"])
app.include_router(recommendations.router, prefix=settings.API_V1_PREFIX, tags=["recommendations"])
app.include_router(detection.router, prefix=settings.API_V1_PREFIX, tags=["detection"])
app.include_router(metrics.router, prefix=settings.API_V1_PREFIX, tags=["metrics"])
app.include_router(alerts.router, prefix=settings.API_V1_PREFIX, tags=["alerts"])
app.include_router(waf.router, prefix=settings.API_V1_PREFIX, tags=["waf"])
app.include_router(feedback.router, prefix=settings.API_V1_PREFIX, tags=["feedback"])
app.include_router(retraining.router, prefix=settings.API_V1_PREFIX, tags=["retraining"])
app.include_router(model_version.router, prefix=settings.API_V1_PREFIX, tags=["model-versioning"])
app.include_router(feedback_analytics.router, prefix=settings.API_V1_PREFIX, tags=["feedback-analytics"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )

