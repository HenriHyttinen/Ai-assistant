from pydantic import BaseModel
from typing import List, Optional

class DataConsent(BaseModel):
    """Data consent schema for user privacy preferences."""
    data_collection: bool = False
    data_processing: bool = False
    data_sharing: bool = False
    ai_insights: bool = False
    email_notifications: bool = False
    analytics_tracking: bool = False
    
    # Specific data types
    health_metrics: bool = False
    activity_data: bool = False
    personal_info: bool = False
    usage_patterns: bool = False

class ConsentResponse(BaseModel):
    """Response schema for consent status."""
    user_id: int
    consent_given: bool
    consent_date: str
    data_usage_consent: DataConsent
    privacy_policy_version: str = "1.0"

class ConsentUpdate(BaseModel):
    """Schema for updating consent preferences."""
    data_usage_consent: DataConsent
    consent_given: bool

