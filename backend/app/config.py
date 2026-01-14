"""
Configuration management for TRIDENT backend.
Handles environment variables and application settings.
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
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
    
    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """
        Validate SECRET_KEY is not default value in production and meets length requirements.
        
        Args:
            v: SECRET_KEY value
            info: Validation info containing other field values
            
        Returns:
            Validated SECRET_KEY
            
        Raises:
            ValueError: If SECRET_KEY is default in production or too short
        """
        default_key = "change-this-secret-key-in-production"
        
        # Get environment from info.data (other fields)
        environment = info.data.get('ENVIRONMENT', 'development') if hasattr(info, 'data') else 'development'
        
        # Check if default key is used in non-development environments
        if v == default_key and environment != 'development':
            raise ValueError(
                f"SECRET_KEY must be changed from default value in {environment} environment. "
                "Set a strong random secret key in environment variables."
            )
        
        # Check minimum length requirement
        if len(v) < 32:
            raise ValueError(
                f"SECRET_KEY must be at least 32 characters long. Current length: {len(v)}"
            )
        
        return v
    
    # ML Configuration
    ML_MODEL_PATH: str = "/app/ml_models"
    ANOMALY_THRESHOLD: float = 0.7
    BATCH_SIZE: int = 100
    
    # Feature Engineering
    FEATURE_CACHE_TTL: int = 3600
    BASELINE_UPDATE_INTERVAL: int = 3600
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 1000
    
    # WAF Integration
    WAF_API_KEY: str = "trident-waf-api-key-2025"  # Default API key for development
    MOCK_WAF_URL: str = "http://mock-waf:8001"  # Mock WAF service URL (for Docker)
    MOCK_WAF_ENABLED: bool = True  # Enable Mock WAF integration
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Allow extra environment variables (e.g., from docker-compose)


# Global settings instance
settings = Settings()

