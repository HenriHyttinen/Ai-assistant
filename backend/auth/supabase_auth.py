from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from lib.supabase import supabase
from models.user import User
from database import get_db
from sqlalchemy.orm import Session
from typing import Optional
import jwt

security = HTTPBearer()

async def get_current_user_supabase(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from Supabase JWT token."""
    token = credentials.credentials
    
    try:
        # Verify the JWT token with Supabase
        user_data = supabase.auth.get_user(token)
        
        if not user_data.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get or create user in our database
        user = db.query(User).filter(User.email == user_data.user.email).first()
        
        if not user:
            # Create new user from Supabase data
            user = User(
                email=user_data.user.email,
                is_verified=user_data.user.email_confirmed_at is not None,
                two_factor_enabled=False,  # Supabase handles 2FA differently
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

