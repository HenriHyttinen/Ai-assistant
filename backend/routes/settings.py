from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any

from database import get_db
from services import settings as settings_service
from auth.supabase_auth import get_current_user_supabase as get_current_user
from schemas.settings import (
    UserSettingsCreate,
    UserSettingsUpdate,
    UserSettingsResponse
)
from models.user import User

router = APIRouter()

@router.get("/me", response_model=UserSettingsResponse)
def get_my_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get current user's settings."""
    user_settings = settings_service.get_or_create_user_settings(db, current_user.id)
    return UserSettingsResponse.model_validate(user_settings)

@router.put("/me", response_model=UserSettingsResponse)
def update_my_settings(
    settings_update: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update current user's settings."""
    # Get or create settings if they don't exist
    user_settings = settings_service.get_or_create_user_settings(db, current_user.id)
    
    # Update the settings
    updated_settings = settings_service.update_user_settings(
        db, current_user.id, settings_update
    )
    if not updated_settings:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update settings"
        )
    return UserSettingsResponse.model_validate(updated_settings)

@router.post("/me", response_model=UserSettingsResponse)
def create_my_settings(
    settings_data: UserSettingsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create settings for current user (if they don't exist)."""
    # Check if settings already exist
    existing_settings = settings_service.get_user_settings(db, current_user.id)
    if existing_settings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Settings already exist for this user"
        )
    
    new_settings = settings_service.create_user_settings(db, current_user.id, settings_data)
    return UserSettingsResponse.model_validate(new_settings)
