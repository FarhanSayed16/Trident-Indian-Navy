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

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

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
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="ML-Enabled Network Anomaly Detection Module for WAF Integration",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

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
    db_status = check_db_connection()
    
    return {
        "status": "healthy" if db_status else "degraded",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected" if db_status else "disconnected",
    }


# Include routers (will be added in later phases)
# from app.routers import traffic, alerts, recommendations, dashboard, waf
# app.include_router(traffic.router, prefix=settings.API_V1_PREFIX, tags=["traffic"])
# app.include_router(alerts.router, prefix=settings.API_V1_PREFIX, tags=["alerts"])
# app.include_router(recommendations.router, prefix=settings.API_V1_PREFIX, tags=["recommendations"])
# app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX, tags=["dashboard"])
# app.include_router(waf.router, prefix=settings.API_V1_PREFIX, tags=["waf"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )

