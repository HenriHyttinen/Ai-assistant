from pydantic import BaseModel, Field, AliasChoices
from typing import Optional

class UserSettingsBase(BaseModel):
    email_notifications: bool = Field(default=True, alias="emailNotifications")
    weekly_reports: bool = Field(default=True, alias="weeklyReports")
    ai_insights: bool = Field(default=True, alias="aiInsights")
    data_sharing: bool = Field(default=False, alias="dataSharing")
    measurement_system: str = Field(default="metric", pattern="^(metric|imperial)$", alias="measurementSystem")
    language: str = Field(default="en", min_length=2, max_length=5)
    timezone: str = Field(default="UTC", description="Timezone in ISO format (e.g., UTC, America/New_York, Europe/London)")

    class Config:
        populate_by_name = True  # Allow both field names and aliases

class UserSettingsCreate(UserSettingsBase):
    pass

class UserSettingsUpdate(BaseModel):
    email_notifications: Optional[bool] = Field(None, alias="emailNotifications")
    weekly_reports: Optional[bool] = Field(None, alias="weeklyReports")
    ai_insights: Optional[bool] = Field(None, alias="aiInsights")
    data_sharing: Optional[bool] = Field(None, alias="dataSharing")
    measurement_system: Optional[str] = Field(None, pattern="^(metric|imperial)$", alias="measurementSystem")
    language: Optional[str] = Field(None, min_length=2, max_length=5)
    timezone: Optional[str] = Field(None, description="Timezone in ISO format (e.g., UTC, America/New_York, Europe/London)")

    class Config:
        populate_by_name = True  # Allow both field names and aliases

class UserSettingsResponse(UserSettingsBase):
    id: int
    user_id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow both field names and aliases
        
    @classmethod
    def model_validate(cls, obj, **kwargs):
        # Convert datetime objects to strings
        if hasattr(obj, 'created_at') and obj.created_at:
            obj.created_at = obj.created_at.isoformat()
        if hasattr(obj, 'updated_at') and obj.updated_at:
            obj.updated_at = obj.updated_at.isoformat()
        return super().model_validate(obj, **kwargs)
