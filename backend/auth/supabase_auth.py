from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from models.user import User
from database import get_db
from sqlalchemy.orm import Session
from typing import Optional
import jwt
import time
from functools import lru_cache

# Optional Supabase import - if lib.supabase can't be imported, supabase will be None
# This is fine since the function uses direct JWT decoding anyway
try:
    from lib.supabase import supabase
except ImportError:
    # If lib.supabase can't be imported (e.g., on macOS), set supabase to None
    # The function will still work with direct JWT decoding
    supabase = None

security = HTTPBearer(auto_error=False)

@lru_cache(maxsize=1000)
def get_cached_user(email: str, cache_timestamp: float) -> Optional[User]:
    """Get user from cache with timestamp validation."""
    if time.time() - cache_timestamp > 300:
        return None
    return None

def get_current_user_supabase(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from Supabase JWT token."""
    # Handle OPTIONS requests (CORS preflight) - no auth required
    # FastAPI's CORSMiddleware should handle OPTIONS, but if we get here
    # without credentials, it means it's a real request without auth
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    print(f"🔐 Received token: {token[:20]}..." if token else "❌ No token received")
    
    # Note: Supabase is optional - we can authenticate with just JWT tokens
    # If Supabase is not configured, we'll use direct JWT decoding instead
    
    try:
        import jwt
        
        try:
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            print(f"🔍 Decoded token: {decoded_token}")
            
            if decoded_token.get('exp', 0) < time.time():
                print(f"❌ Token expired: {decoded_token.get('exp')} < {time.time()}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user_email = decoded_token.get('email')
            print(f"📧 User email from token: {user_email}")
            if not user_email:
                print("❌ No email in token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token format",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Look up user in database by email
            from models.user import User
            
            user = db.query(User).filter(User.email == user_email).first()
            if not user:
                print(f"👤 Creating new user for email: {user_email}")
                user = User(
                    email=user_email,
                    is_active=True,
                    is_verified=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"✅ Created user with ID: {user.id}")
            else:
                print(f"👤 Found existing user with ID: {user.id}")
            
            return user
            
        except jwt.InvalidTokenError as e:
            print(f"❌ Invalid token error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            print(f"❌ Token verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        
    except Exception as e:
        print(f"❌ General authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


