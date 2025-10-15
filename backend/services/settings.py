from sqlalchemy.orm import Session
from models.user_settings import UserSettings
from schemas.settings import UserSettingsCreate, UserSettingsUpdate
from typing import Optional

def get_user_settings(db: Session, user_id: int) -> Optional[UserSettings]:
    """Get user settings by user ID."""
    return db.query(UserSettings).filter(UserSettings.user_id == user_id).first()

def create_user_settings(db: Session, user_id: int, settings_data: UserSettingsCreate) -> UserSettings:
    """Create new user settings."""
    db_settings = UserSettings(
        user_id=user_id,
        **settings_data.model_dump()
    )
    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)
    return db_settings

def update_user_settings(
    db: Session, 
    user_id: int, 
    settings_update: UserSettingsUpdate
) -> Optional[UserSettings]:
    """Update user settings."""
    db_settings = get_user_settings(db, user_id)
    if not db_settings:
        return None
    
    update_data = settings_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_settings, field, value)
    
    db.commit()
    db.refresh(db_settings)
    return db_settings

def get_or_create_user_settings(db: Session, user_id: int) -> UserSettings:
    """Get user settings or create default ones if they don't exist."""
    settings = get_user_settings(db, user_id)
    if not settings:
        default_settings = UserSettingsCreate()
        settings = create_user_settings(db, user_id, default_settings)
    return settings
