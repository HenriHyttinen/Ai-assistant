from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from lib.supabase import supabase
from models.user import User
from database import get_db
from sqlalchemy.orm import Session
from typing import Optional
import jwt
import time
from functools import lru_cache

security = HTTPBearer()

@lru_cache(maxsize=1000)
def get_cached_user(email: str, cache_timestamp: float) -> Optional[User]:
    """Get user from cache with timestamp validation."""
    if time.time() - cache_timestamp > 300:
        return None
    return None

def get_current_user_supabase(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from Supabase JWT token."""
    token = credentials.credentials
    
    print(f"🔐 Received token: {token[:20]}..." if token else "❌ No token received")
    
    # Check if Supabase client is available
    if supabase is None:
        print("❌ Supabase client not available")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service temporarily unavailable",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        import jwt
        from jwt import PyJWKClient
        
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
            from database import SessionLocal
            from models.user import User
            
            db = SessionLocal()
            try:
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
                
            finally:
                db.close()
            
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


