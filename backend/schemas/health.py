from pydantic import BaseModel, conint, confloat, Field
from typing import List, Optional, Dict
from datetime import datetime

class HealthProfileBase(BaseModel):
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = None
    height: Optional[float] = Field(None, gt=0)  # in cm
    weight: Optional[float] = Field(None, gt=0)  # in kg
    occupation_type: Optional[str] = None
    activity_level: Optional[str] = None
    
    # Dietary preferences and restrictions
    dietary_preferences: Optional[str] = None  # JSON string of preferences
    dietary_restrictions: Optional[str] = None  # JSON string of restrictions
    meal_preferences: Optional[str] = None  # breakfast, lunch, dinner preferences
    
    fitness_goal: Optional[str] = None
    target_weight: Optional[float] = Field(None, gt=0)
    target_activity_level: Optional[str] = None
    preferred_exercise_time: Optional[str] = None
    preferred_exercise_environment: Optional[str] = None
    weekly_activity_frequency: Optional[int] = Field(None, ge=0, le=7)
    exercise_types: Optional[str] = None
    average_session_duration: Optional[str] = None
    fitness_level: Optional[str] = None
    endurance_level: Optional[int] = Field(None, ge=1, le=10)
    strength_indicators: Optional[str] = None
    current_endurance_minutes: Optional[int] = Field(None, ge=0)  # How long can run/walk
    pushup_count: Optional[int] = Field(None, ge=0)  # Number of pushups can do
    squat_count: Optional[int] = Field(None, ge=0)  # Number of squats can do

class HealthProfileCreate(HealthProfileBase):
    pass

class HealthProfileUpdate(HealthProfileBase):
    pass

class HealthProfileResponse(HealthProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ActivityLogBase(BaseModel):
    activity_type: str
    duration: int = Field(gt=0)  # in minutes
    intensity: Optional[str] = None
    notes: Optional[str] = None
    # Optional timestamp when the activity actually happened
    performed_at: Optional[datetime] = None

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

class WellnessScoreResponse(BaseModel):
    wellness_score: float
    bmi: float
    bmi_category: str
    components: Dict[str, float]

class HealthAnalytics(BaseModel):
    current_bmi: Optional[float] = None
    current_wellness_score: Optional[float] = None
    weight_trend: List[float] = []
    bmi_trend: List[float] = []
    wellness_score_trend: List[float] = []
    weight_trend_timestamps: List[str] = []  # ISO format timestamps
    activity_summary: dict = {}
    progress_towards_goal: Optional[float] = None  # percentage 