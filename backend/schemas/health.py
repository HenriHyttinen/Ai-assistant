from pydantic import BaseModel, conint, confloat, Field, field_validator, ValidationError
from typing import List, Optional, Dict
from datetime import datetime

class HealthProfileBase(BaseModel):
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = None
    height: Optional[float] = Field(None, gt=50, le=300)  # in cm (20 inches to 10 feet)
    weight: Optional[float] = Field(None, gt=20, le=500)  # in kg (44 lbs to 1100 lbs)
    occupation_type: Optional[str] = None
    activity_level: Optional[str] = None
    
    # Dietary preferences and restrictions
    dietary_preferences: Optional[str] = None  # JSON string of preferences
    dietary_restrictions: Optional[str] = None  # JSON string of restrictions
    meal_preferences: Optional[str] = None  # breakfast, lunch, dinner preferences
    
    fitness_goal: Optional[str] = None
    target_weight: Optional[float] = Field(None, gt=20, le=500)  # in kg (44 lbs to 1100 lbs)
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
    
    @field_validator('height')
    @classmethod
    def validate_height(cls, v):
        if v is not None:
            if v < 50:
                raise ValueError('Height must be at least 50 cm (about 20 inches)')
            if v > 300:
                raise ValueError('Height must be no more than 300 cm (about 10 feet)')
        return v
    
    @field_validator('weight')
    @classmethod
    def validate_weight(cls, v):
        if v is not None:
            if v < 20:
                raise ValueError('Weight must be at least 20 kg (about 44 lbs)')
            if v > 500:
                raise ValueError('Weight must be no more than 500 kg (about 1100 lbs)')
        return v
    
    @field_validator('target_weight')
    @classmethod
    def validate_target_weight(cls, v):
        if v is not None:
            if v < 20:
                raise ValueError('Target weight must be at least 20 kg (about 44 lbs)')
            if v > 500:
                raise ValueError('Target weight must be no more than 500 kg (about 1100 lbs)')
        return v

class HealthProfileCreate(HealthProfileBase):
    pass

class HealthProfileUpdate(HealthProfileBase):
    pass

class HealthProfileResponse(BaseModel):
    """Response schema for reading health profile data - no strict validation for existing data."""
    id: int
    user_id: int
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None  # No validation for reading existing data
    weight: Optional[float] = None  # No validation for reading existing data
    occupation_type: Optional[str] = None
    activity_level: Optional[str] = None
    
    # Dietary preferences and restrictions
    dietary_preferences: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    meal_preferences: Optional[str] = None
    
    fitness_goal: Optional[str] = None
    target_weight: Optional[float] = None  # No validation for reading existing data
    target_activity_level: Optional[str] = None
    preferred_exercise_time: Optional[str] = None
    preferred_exercise_environment: Optional[str] = None
    weekly_activity_frequency: Optional[int] = None
    exercise_types: Optional[str] = None
    average_session_duration: Optional[str] = None
    fitness_level: Optional[str] = None
    endurance_level: Optional[int] = None
    strength_indicators: Optional[str] = None
    current_endurance_minutes: Optional[int] = None
    pushup_count: Optional[int] = None
    squat_count: Optional[int] = None
    
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
    
    @field_validator('performed_at', mode='before')
    @classmethod
    def parse_performed_at(cls, v):
        if isinstance(v, str):
            # Handle datetime-local format (YYYY-MM-DDTHH:MM:SS)
            if 'T' in v and len(v) == 19:  # YYYY-MM-DDTHH:MM:SS
                return datetime.fromisoformat(v)
            # Handle ISO format
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except:
                return datetime.fromisoformat(v)
        return v

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