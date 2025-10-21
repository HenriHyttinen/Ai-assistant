from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Tuple
import time
from collections import defaultdict, deque
import asyncio

class RateLimiter:
    """Simple in-memory rate limiter for API protection."""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(deque)
        self.lock = asyncio.Lock()
    
    async def is_allowed(self, client_ip: str) -> Tuple[bool, int]:
        """
        Check if request is allowed for the given client IP.
        
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        async with self.lock:
            now = time.time()
            client_requests = self.requests[client_ip]
            
            # Remove old requests outside the time window
            while client_requests and client_requests[0] <= now - self.time_window:
                client_requests.popleft()
            
            # Check if under the limit
            if len(client_requests) < self.max_requests:
                client_requests.append(now)
                remaining = self.max_requests - len(client_requests)
                return True, remaining
            else:
                remaining = 0
                return False, remaining
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check for forwarded headers first (for reverse proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"

# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=1000, time_window=60)  # 1000 requests per minute for development

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    
    # Skip rate limiting for certain endpoints
    skip_paths = ["/docs", "/openapi.json", "/health"]
    if request.url.path in skip_paths:
        return await call_next(request)
    
    client_ip = rate_limiter.get_client_ip(request)
    is_allowed, remaining = await rate_limiter.is_allowed(client_ip)
    
    if not is_allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Whoa there! You're making requests too fast. Take a breather and try again in a minute.",
                "retry_after": 60,
                "remaining_requests": remaining
            },
            headers={
                "Retry-After": "60",
                "X-RateLimit-Limit": str(rate_limiter.max_requests),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(int(time.time()) + rate_limiter.time_window)
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + rate_limiter.time_window)
    
    return response

# Specialized rate limiters for different endpoints
ai_rate_limiter = RateLimiter(max_requests=100, time_window=60)  # 100 AI requests per minute for development
auth_rate_limiter = RateLimiter(max_requests=50, time_window=60)  # 50 auth attempts per minute for development

async def ai_rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware specifically for AI endpoints."""
    
    if "/insights" in request.url.path or "/ai" in request.url.path:
        client_ip = ai_rate_limiter.get_client_ip(request)
        is_allowed, remaining = await ai_rate_limiter.is_allowed(client_ip)
        
        if not is_allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "AI rate limit exceeded. Too many AI requests.",
                    "retry_after": 60,
                    "remaining_requests": remaining
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(ai_rate_limiter.max_requests),
                    "X-RateLimit-Remaining": str(remaining)
                }
            )
    
    return await call_next(request)

async def auth_rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware specifically for authentication endpoints."""
    
    if "/auth/login" in request.url.path or "/auth/register" in request.url.path:
        client_ip = auth_rate_limiter.get_client_ip(request)
        is_allowed, remaining = await auth_rate_limiter.is_allowed(client_ip)
        
        if not is_allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Authentication rate limit exceeded. Too many login attempts.",
                    "retry_after": 60,
                    "remaining_requests": remaining
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(auth_rate_limiter.max_requests),
                    "X-RateLimit-Remaining": str(remaining)
                }
            )
    
    return await call_next(request)