from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client, create_client
from models.user import User
from database import get_db
from sqlalchemy.orm import Session
from typing import Optional
import jwt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Create Supabase client directly with error handling
try:
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        # CRITICAL FIX: Only pass url and key, not proxies or other deprecated args
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    else:
        supabase = None
        print("Warning: Supabase credentials not found in environment")
except Exception as e:
    print(f"Warning: Failed to initialize Supabase client: {e}")
    supabase = None

security = HTTPBearer()

async def get_current_user_supabase(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from Supabase JWT token.
    """
    try:
        # Verify the JWT token with Supabase
        token = credentials.credentials
        
        # Get user from Supabase
        response = supabase.auth.get_user(token)
        
        if response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = db.query(User).filter(User.email == response.user.email).first()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
        
    except Exception as e:
        print(f"Supabase auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
