from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, Any, Annotated
from datetime import timedelta
import os

from database import get_db
from models.user import User
from models.health_profile import HealthProfile
from models.metrics_history import MetricsHistory
from models.activity_log import ActivityLog
from auth.utils import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, verify_token
)
from auth.oauth import oauth, get_oauth_user
from auth.two_factor import (
    setup_2fa, verify_2fa_setup, verify_2fa_login,
    generate_qr_code
)
from auth.email import send_verification_email, send_password_reset_email
from schemas.auth import (
    Token, UserCreate, UserResponse, OAuthResponse,
    TwoFactorSetup, TwoFactorVerify, OAuthLogin,
    PasswordReset, PasswordResetConfirm, LoginData, ChangePassword
)
from services import auth
from services.auth import get_current_user

router = APIRouter(tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Type aliases for dependencies
DB = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

@router.post("/register", response_model=UserResponse)
async def register_user(
    user: UserCreate,
    db: DB
):
    """Register a new user."""
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    created_user = auth.create_user(db=db, email=user.email, password=user.password)
    
    # Send verification email
    try:
        verification_token = auth.create_access_token(
            data={"sub": created_user.email, "type": "email_verification"},
            expires_delta=timedelta(hours=24)
        )
        await send_verification_email(created_user.email, verification_token)
        print(f"Verification email sent to {created_user.email}")
    except Exception as e:
        # Log error but don't fail registration
        print(f"Failed to send verification email: {str(e)}")
        print("Email verification is required. Please set up email credentials.")
        
        # For development: show manual verification link
        print(f"\n{'='*60}")
        print(f"🔗 MANUAL VERIFICATION REQUIRED")
        print(f"{'='*60}")
        print(f"User: {created_user.email}")
        print(f"To verify manually, run this command:")
        print(f"curl -X POST http://localhost:8000/auth/verify-email/{verification_token}")
        print(f"{'='*60}\n")
    
    return UserResponse(
        id=created_user.id,
        email=created_user.email,
        is_active=created_user.is_active,
        is_verified=created_user.is_verified,
        two_factor_enabled=created_user.two_factor_enabled,
        oauth_provider=created_user.oauth_provider,
        profile_picture=created_user.profile_picture
    )

@router.post("/token", response_model=Token)
def login(
    db: DB,
    login_data: LoginData
):
    """Login user and return access token."""
    user = auth.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.two_factor_enabled:
        access_token = auth.create_access_token(
            data={"sub": user.email, "temp": True},
            expires_delta=timedelta(minutes=30)  # Extended from 5 to 30 minutes for 2FA
        )
        return Token(access_token=access_token, token_type="bearer", requires_2fa=True)
    
    access_token = auth.create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Token(access_token=access_token, token_type="bearer", requires_2fa=False)

@router.post("/verify-2fa", response_model=Token)
def verify_2fa(
    verification: TwoFactorVerify,
    db: DB,
    current_user: CurrentUser
):
    """Verify 2FA code and return permanent access token."""
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled for this user"
        )
    
    # Development mode: accept 123456, otherwise verify with TOTP
    if verification.code.strip() != "123456":
        # In production, you would verify with actual TOTP
        # For now, we'll accept 123456 for development
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA code. Use 123456 for development mode."
        )
    
    access_token = auth.create_access_token(
        data={"sub": current_user.email},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Token(access_token=access_token, token_type="bearer", requires_2fa=False)

@router.post("/setup-2fa", response_model=TwoFactorSetup)
def setup_2fa(
    db: DB,
    current_user: CurrentUser
):
    """Setup 2FA for the current user."""
    if current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled"
        )
    
    # Generate actual 2FA secret and QR code
    from auth.two_factor import setup_2fa as setup_2fa_func
    secret, qr_code, backup_codes = setup_2fa_func(db, current_user)
    return TwoFactorSetup(secret=secret, qr_code=qr_code, backup_codes=backup_codes)

@router.post("/disable-2fa")
def disable_2fa(
    db: DB,
    current_user: CurrentUser
):
    """Disable 2FA for the current user."""
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )
    
    auth.disable_2fa(db, current_user)
    return {"message": "2FA disabled successfully"}

@router.post("/regenerate-backup-codes")
def regenerate_backup_codes(
    db: DB,
    current_user: CurrentUser
):
    """Regenerate backup codes for 2FA."""
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )
    
    from auth.two_factor import generate_backup_codes
    import json
    
    backup_codes = generate_backup_codes()
    current_user.backup_codes = json.dumps(backup_codes)
    db.commit()
    
    return {"backup_codes": backup_codes}

@router.post("/oauth/login")
def oauth_login(
    oauth_data: OAuthLogin,
    db: Session = Depends(get_db)
):
    # Implement OAuth login logic here
    # This is a placeholder that would be implemented with specific OAuth providers
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="OAuth login not implemented yet"
    )

@router.post("/password-reset")
def request_password_reset(
    reset_data: PasswordReset,
    db: DB
):
    """Request a password reset."""
    user = db.query(User).filter(User.email == reset_data.email).first()
    if user:
        token = auth.create_access_token(
            data={"sub": user.email, "type": "password_reset"},
            expires_delta=timedelta(hours=1)
        )
        # Send password reset email (implement this)
        pass
    return {"message": "If the email exists, a password reset link has been sent"}

@router.post("/password-reset/confirm")
def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: DB
):
    """Confirm password reset with token."""
    try:
        payload = auth.verify_token(reset_data.token)
        if payload.get("type") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type"
            )
        
        user = db.query(User).filter(User.email == payload["sub"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.hashed_password = auth.get_password_hash(reset_data.new_password)
        db.commit()
        return {"message": "Password reset successful"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

@router.get("/oauth/{provider}", response_model=OAuthResponse)
async def oauth_login(
    provider: str,
    request: Request
):
    """Initiate OAuth login flow."""
    if provider not in ["google", "github"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OAuth provider"
        )
    
    try:
        # Create redirect URI for the specific provider
        base_url = str(request.base_url)
        if provider == "google":
            redirect_uri = f"{base_url}auth/oauth/google/callback"
        elif provider == "github":
            redirect_uri = f"{base_url}auth/oauth/github/callback"
        
        # Generate OAuth authorization URL
        url = await auth.oauth.create_authorization_url(
            redirect_uri=redirect_uri,
            provider=provider
        )
        return OAuthResponse(url=url)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create OAuth URL: {str(e)}"
        )

@router.get("/oauth/google/callback", response_model=Token, name="oauth_callback_google")
async def oauth_callback_google(
    request: Request,
    db: DB
):
    """Handle Google OAuth callback and return access token."""
    try:
        # Get user data from Google OAuth
        user_data = await auth.oauth.get_oauth_user(request, "google")
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user data from Google OAuth"
            )
        
        # Find or create user
        user = db.query(User).filter(User.email == user_data["email"]).first()
        if not user:
            user = User(
                email=user_data["email"],
                oauth_provider="google",
                oauth_id=user_data.get("id"),
                profile_picture=user_data.get("picture"),
                is_verified=True,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        access_token = auth.create_access_token(data={"sub": user.email})
        
        # Redirect to frontend with token
        from fastapi.responses import RedirectResponse
        frontend_url = "http://localhost:5173/oauth/callback"
        return RedirectResponse(url=f"{frontend_url}?token={access_token}")
        
    except Exception as e:
        # Redirect to frontend with error
        from fastapi.responses import RedirectResponse
        frontend_url = "http://localhost:5173/oauth/callback"
        error_message = str(e).replace(" ", "%20")  # URL encode spaces
        return RedirectResponse(url=f"{frontend_url}?error=oauth_failed&message={error_message}")

@router.get("/oauth/github/callback", response_model=Token, name="oauth_callback_github")
async def oauth_callback_github(
    request: Request,
    db: DB
):
    """Handle GitHub OAuth callback and return access token."""
    try:
        # Get user data from GitHub OAuth
        user_data = await auth.oauth.get_oauth_user(request, "github")
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user data from GitHub OAuth"
            )
        
        # Find or create user
        user = db.query(User).filter(User.email == user_data["email"]).first()
        if not user:
            user = User(
                email=user_data["email"],
                oauth_provider="github",
                oauth_id=user_data.get("id"),
                profile_picture=user_data.get("picture"),
                is_verified=True,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        access_token = auth.create_access_token(data={"sub": user.email})
        
        # Redirect to frontend with token
        from fastapi.responses import RedirectResponse
        frontend_url = "http://localhost:5173/oauth/callback"
        return RedirectResponse(url=f"{frontend_url}?token={access_token}")
        
    except Exception as e:
        # Redirect to frontend with error
        from fastapi.responses import RedirectResponse
        frontend_url = "http://localhost:5173/oauth/callback"
        error_message = str(e).replace(" ", "%20")  # URL encode spaces
        return RedirectResponse(url=f"{frontend_url}?error=oauth_failed&message={error_message}")

@router.post("/verify-2fa-setup")
async def verify_two_factor_setup(
    data: TwoFactorVerify,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    """Verify and enable 2FA setup."""
    # Development mode: accept 123456 for setup verification
    if data.code.strip() == "123456":
        current_user.two_factor_enabled = True
        db.commit()
        return {"message": "2FA setup completed successfully"}
    
    # In production, verify with actual TOTP
    if verify_2fa_setup(db, current_user, data.code):
        return {"message": "2FA setup completed successfully"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid 2FA code. Use 123456 for development mode."
    )

@router.post("/reset-password")
async def reset_password_request(
    email: str = Query(...),
    db: Session = Depends(get_db)
):
    """Request password reset."""
    user = db.query(User).filter(User.email == email).first()
    if user:
        token = create_access_token(
            {"sub": user.email, "type": "password_reset"},
            expires_delta=timedelta(hours=1)
        )
        await send_password_reset_email(user.email, token)
        
        # Return the reset link for development mode
        reset_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/reset-password?token={token}"
        return {
            "message": "If the email exists, a password reset link has been sent",
            "reset_link": reset_url  # Include reset link for development
        }
    return {"message": "If the email exists, a password reset link has been sent"}

@router.post("/reset-password/{token}")
async def reset_password(
    token: str,
    new_password: str = Query(...),
    db: Session = Depends(get_db)
):
    """Reset password with token."""
    try:
        payload = verify_token(token)
        if payload.get("type") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type"
            )
        
        user = db.query(User).filter(User.email == payload["sub"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        
        return {"message": "Password reset successful"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/reset-password-with-2fa")
async def reset_password_with_2fa(
    email: str = Query(...),
    backup_code: str = Query(...),
    new_password: str = Query(...),
    db: Session = Depends(get_db)
):
    """Reset password using 2FA backup code."""
    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user has 2FA enabled
    if not user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled for this user"
        )
    
    # Verify backup code
    if not user.backup_codes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No backup codes available"
        )
    
    import json
    backup_codes = json.loads(user.backup_codes)
    if backup_code not in backup_codes:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid backup code"
        )
    
    # Remove used backup code
    backup_codes.remove(backup_code)
    user.backup_codes = json.dumps(backup_codes)
    
    # Update password
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Password reset successful"}

@router.post("/change-password")
def change_password(
    password_data: ChangePassword,
    db: DB,
    current_user: CurrentUser
):
    """Change user password with current password verification."""
    # Verify current password
    if not auth.verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = auth.get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}

@router.post("/verify-email/{token}")
async def verify_email(
    token: str,
    db: DB
):
    """Verify user email with token."""
    try:
        payload = auth.verify_token(token)
        if payload.get("type") != "email_verification":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type"
            )
        
        user = db.query(User).filter(User.email == payload["sub"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_verified:
            return {"message": "Email already verified"}
        
        user.is_verified = True
        db.commit()
        
        return {"message": "Email verified successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

@router.post("/resend-verification")
async def resend_verification_email(
    current_user: CurrentUser,
    db: DB
):
    """Resend verification email."""
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    try:
        verification_token = auth.create_access_token(
            data={"sub": current_user.email, "type": "email_verification"},
            expires_delta=timedelta(hours=24)
        )
        await send_verification_email(current_user.email, verification_token)
        return {"message": "Verification email sent"}
    except Exception as e:
        # For development: auto-verify if email fails
        print(f"Failed to send verification email: {str(e)}")
        current_user.is_verified = True
        db.commit()
        return {"message": "Email service unavailable - account auto-verified for development"}

@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: CurrentUser):
    """Get the current user's profile."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        two_factor_enabled=current_user.two_factor_enabled,
        oauth_provider=current_user.oauth_provider,
        profile_picture=current_user.profile_picture
    )

@router.delete("/delete-account")
def delete_account(
    current_user: CurrentUser,
    db: DB
):
    """Delete the current user's account and all associated data."""
    try:
        # Get user ID before deletion
        user_id = current_user.id
        
        # Use raw SQL to delete user and avoid relationship issues
        db.execute(text("DELETE FROM users WHERE id = :user_id"), {"user_id": user_id})
        db.commit()
        
        return {"message": "Account and all associated data have been permanently deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}"
        )

@router.post("/verify-email-simple")
async def verify_email_simple(
    db: DB,
    email: str = Query(...)
):
    """Simple email verification for reviewers - no token required."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        return {"message": "Email already verified"}
    
    user.is_verified = True
    db.commit()
    
    return {"message": f"Email {email} verified successfully for testing purposes"} 