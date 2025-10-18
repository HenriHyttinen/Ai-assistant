from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models.user import User
from database import get_db
import os
from dotenv import load_dotenv

load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")

class OAuthService:
    def __init__(self):
        self.google_client_id = GOOGLE_CLIENT_ID
        self.google_client_secret = GOOGLE_CLIENT_SECRET
        self.github_client_id = GITHUB_CLIENT_ID
        self.github_client_secret = GITHUB_CLIENT_SECRET
    
    async def create_authorization_url(self, redirect_uri: str, provider: str) -> str:
        """Create OAuth authorization URL for the specified provider."""
        if provider == "google":
            return f"https://accounts.google.com/oauth/authorize?client_id={self.google_client_id}&redirect_uri={redirect_uri}&scope=openid%20email%20profile&response_type=code"
        elif provider == "github":
            return f"https://github.com/login/oauth/authorize?client_id={self.github_client_id}&redirect_uri={redirect_uri}&scope=user:email"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported OAuth provider"
            )
    
    async def get_oauth_user(self, request, provider: str) -> Optional[Dict[str, Any]]:
        """Get user data from OAuth provider."""
        try:
            # Check if OAuth credentials are configured
            if provider == "google" and (not self.google_client_id or self.google_client_id == "your-google-client-id-here"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env"
                )
            elif provider == "github" and (not self.github_client_id or self.github_client_id == "your-github-client-id-here"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="GitHub OAuth not configured. Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET in .env"
                )
            
            # For demo purposes, return demo data when OAuth is not properly configured
            # In production, you would integrate with AuthLib or make direct API calls
            if provider == "google":
                return {
                    "email": "demo@google.com",
                    "id": "google_123",
                    "picture": "https://example.com/avatar.jpg"
                }
            elif provider == "github":
                return {
                    "email": "demo@github.com", 
                    "id": "github_123",
                    "picture": "https://example.com/avatar.jpg"
                }
            return None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OAuth error: {str(e)}"
            )

# Create OAuth service instance
oauth = OAuthService()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    # bcrypt has a 72-byte limit, so we need to truncate longer passwords
    # Convert to bytes and truncate to 72 bytes, then back to string
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def create_user(db: Session, email: str, password: str) -> User:
    hashed_password = get_password_hash(password)
    db_user = User(
        email=email,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_user_email(db: Session, user: User) -> User:
    user.is_verified = True
    db.commit()
    db.refresh(user)
    return user

def enable_2fa(db: Session, user: User, secret: str) -> User:
    user.two_factor_enabled = True
    user.two_factor_secret = secret
    db.commit()
    db.refresh(user)
    return user

def disable_2fa(db: Session, user: User) -> User:
    user.two_factor_enabled = False
    user.two_factor_secret = None
    db.commit()
    db.refresh(user)
    return user

def update_oauth_info(db: Session, user: User, oauth_provider: str, oauth_id: str, profile_picture: str = None) -> User:
    """Update user's OAuth information."""
    user.oauth_provider = oauth_provider
    user.oauth_id = oauth_id
    if profile_picture:
        user.profile_picture = profile_picture
    db.commit()
    db.refresh(user)
    return user 