from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

class HealthProfileBase(BaseModel):
    age: int = Field(..., gt=0, lt=120)
    gender: str
    height: float = Field(..., gt=0)  # in cm
    weight: float = Field(..., gt=0)  # in kg
    occupation_type: str
    activity_level: str
    fitness_goal: str
    target_weight: Optional[float] = None
    target_activity_level: Optional[str] = None
    preferred_exercise_time: Optional[str] = None
    preferred_exercise_environment: Optional[str] = None
    weekly_activity_frequency: int = Field(..., ge=0, le=7)
    exercise_types: List[str]
    average_session_duration: str
    fitness_level: str
    endurance_level: Optional[int] = None
    strength_indicators: Optional[dict] = None

class HealthProfileCreate(HealthProfileBase):
    pass

class HealthProfileResponse(HealthProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ActivityLogBase(BaseModel):
    activity_type: str
    duration: int = Field(..., gt=0)  # in minutes
    intensity: str
    notes: Optional[str] = None

class ActivityLogCreate(ActivityLogBase):
    pass

class ActivityLogResponse(ActivityLogBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class MetricsHistoryBase(BaseModel):
    weight: float
    bmi: float
    wellness_score: float

class MetricsHistoryCreate(MetricsHistoryBase):
    pass

class MetricsHistoryResponse(MetricsHistoryBase):
    id: int
    health_profile_id: int
    recorded_at: datetime

    class Config:
        from_attributes = True 