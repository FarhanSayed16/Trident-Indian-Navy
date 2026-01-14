"""
Rate Limiting Middleware for FastAPI
Prevents API abuse by limiting requests per IP address.
"""

import time
from typing import Callable
from collections import defaultdict
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm.
    """
    
    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        """
        Initialize rate limiting middleware.
        
        Args:
            app: FastAPI application
            requests_per_minute: Maximum requests per minute per IP
            requests_per_hour: Maximum requests per hour per IP
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.request_times: defaultdict = defaultdict(list)
    
    def _clean_old_requests(self, ip: str, window_seconds: int):
        """Remove requests older than window."""
        current_time = time.time()
        self.request_times[ip] = [
            req_time for req_time in self.request_times[ip]
            if current_time - req_time < window_seconds
        ]
    
    def _check_rate_limit(self, ip: str) -> tuple[bool, str]:
        """
        Check if IP has exceeded rate limits.
        
        Args:
            ip: Client IP address
            
        Returns:
            (allowed, message) tuple
        """
        current_time = time.time()
        
        # Clean old requests (keep 1 hour window)
        self._clean_old_requests(ip, 3600)
        
        # Check per-minute limit
        minute_requests = [
            req_time for req_time in self.request_times[ip]
            if current_time - req_time < 60
        ]
        if len(minute_requests) >= self.requests_per_minute:
            return False, "Rate limit exceeded: too many requests per minute"
        
        # Check per-hour limit
        hour_requests = [
            req_time for req_time in self.request_times[ip]
            if current_time - req_time < 3600
        ]
        if len(hour_requests) >= self.requests_per_hour:
            return False, "Rate limit exceeded: too many requests per hour"
        
        # Record this request
        self.request_times[ip].append(current_time)
        
        return True, "OK"
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Check rate limit
        allowed, message = self._check_rate_limit(client_ip)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for IP {client_ip}: {message}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": message,
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        
        # Calculate remaining requests
        current_time = time.time()
        minute_remaining = max(0, self.requests_per_minute - len([
            req_time for req_time in self.request_times[client_ip]
            if current_time - req_time < 60
        ]))
        hour_remaining = max(0, self.requests_per_hour - len([
            req_time for req_time in self.request_times[client_ip]
            if current_time - req_time < 3600
        ]))
        
        response.headers["X-RateLimit-Remaining-Minute"] = str(minute_remaining)
        response.headers["X-RateLimit-Remaining-Hour"] = str(hour_remaining)
        
        return response

