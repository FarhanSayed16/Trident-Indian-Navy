"""
Basic Authentication Middleware
Simple API key authentication for WAF integration endpoints.
"""

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from typing import Optional
from app.config import settings

# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Verify API key for WAF integration endpoints.
    
    For demo purposes, we use a simple API key check.
    In production, this should be replaced with proper authentication (JWT, OAuth, etc.).
    
    Args:
        api_key: API key from request header
        
    Returns:
        API key if valid
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    # Get API key from environment or use default for development
    valid_api_key = getattr(settings, 'WAF_API_KEY', 'trident-waf-api-key-2025')
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if api_key != valid_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    
    return api_key

