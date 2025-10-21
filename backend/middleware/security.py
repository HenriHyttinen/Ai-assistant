"""
Security middleware for enforcing HTTPS and other security measures
"""
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce security measures"""
    
    def __init__(self, app, force_https: bool = False):
        super().__init__(app)
        self.force_https = force_https or os.getenv("FORCE_HTTPS", "false").lower() == "true"
    
    async def dispatch(self, request: Request, call_next):
        # Force HTTPS in production
        if self.force_https and not request.url.scheme == "https":
            # Redirect to HTTPS version
            https_url = request.url.replace(scheme="https")
            return RedirectResponse(url=str(https_url), status_code=301)
        
        # Add security headers
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Only add HSTS in production with HTTPS
        if self.force_https and request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

class DataEncryptionMiddleware(BaseHTTPMiddleware):
    """Middleware to ensure sensitive data is encrypted in responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # This middleware could be extended to automatically encrypt
        # sensitive fields in API responses, but for now we'll rely on
        # the model-level encryption
        
        return response
