"""
Configuration management for TRIDENT backend.
Handles environment variables and application settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "TRIDENT"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "postgresql://trident_user:trident_password@localhost:5432/trident_db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Redis (Optional)
    REDIS_URL: Optional[str] = "redis://localhost:6379"
    REDIS_ENABLED: bool = False
    
    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ML Configuration
    ML_MODEL_PATH: str = "/app/ml_models"
    ANOMALY_THRESHOLD: float = 0.7
    BATCH_SIZE: int = 100
    
    # Feature Engineering
    FEATURE_CACHE_TTL: int = 3600
    BASELINE_UPDATE_INTERVAL: int = 3600
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()

