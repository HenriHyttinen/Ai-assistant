from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class GoalType(str, Enum):
    CALORIES = "calories"
    PROTEIN = "protein"
    CARBS = "carbs"
    FAT = "fat"
    FIBER = "fiber"
    SODIUM = "sodium"
    WATER = "water"
    VITAMIN_C = "vitamin_c"
    VITAMIN_A = "vitamin_a"
    CALCIUM = "calcium"
    IRON = "iron"
    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    WEIGHT_MAINTENANCE = "weight_maintenance"

class GoalStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class GoalFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

# Base schemas
class NutritionGoalBase(BaseModel):
    goal_type: GoalType
    goal_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    target_value: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=20)
    frequency: GoalFrequency = GoalFrequency.DAILY
    start_date: datetime
    target_date: Optional[datetime] = None
    is_flexible: bool = True
    priority: int = Field(1, ge=1, le=5)
    is_public: bool = False

class GoalProgressLogBase(BaseModel):
    date: datetime
    achieved_value: float = Field(..., ge=0)
    notes: Optional[str] = Field(None, max_length=1000)
    difficulty_rating: Optional[int] = Field(None, ge=1, le=5)
    mood_rating: Optional[int] = Field(None, ge=1, le=5)

class GoalMilestoneBase(BaseModel):
    milestone_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    target_value: float = Field(..., gt=0)
    is_automatic: bool = True
    reward_description: Optional[str] = Field(None, max_length=200)

# Create schemas
class NutritionGoalCreate(NutritionGoalBase):
    pass

class GoalProgressLogCreate(GoalProgressLogBase):
    goal_id: int

class GoalMilestoneCreate(GoalMilestoneBase):
    goal_id: int

class GoalTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    goal_type: GoalType
    default_target_value: float = Field(..., gt=0)
    default_unit: str = Field(..., min_length=1, max_length=20)
    default_frequency: GoalFrequency = GoalFrequency.DAILY
    default_duration_days: Optional[int] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=50)
    difficulty_level: int = Field(1, ge=1, le=5)
    instructions: Optional[str] = Field(None, max_length=2000)
    tips: Optional[str] = Field(None, max_length=2000)
    common_challenges: Optional[str] = Field(None, max_length=2000)
    success_metrics: Optional[str] = Field(None, max_length=2000)

# Update schemas
class NutritionGoalUpdate(BaseModel):
    goal_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    target_value: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=20)
    frequency: Optional[GoalFrequency] = None
    target_date: Optional[datetime] = None
    is_flexible: Optional[bool] = None
    status: Optional[GoalStatus] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    is_public: Optional[bool] = None

class GoalProgressLogUpdate(BaseModel):
    achieved_value: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=1000)
    difficulty_rating: Optional[int] = Field(None, ge=1, le=5)
    mood_rating: Optional[int] = Field(None, ge=1, le=5)

class GoalMilestoneUpdate(BaseModel):
    milestone_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    target_value: Optional[float] = Field(None, gt=0)
    reward_description: Optional[str] = Field(None, max_length=200)

# Response schemas
class GoalProgressLogResponse(GoalProgressLogBase):
    id: int
    goal_id: int
    user_id: str
    target_value: float
    is_achieved: bool
    progress_percentage: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class GoalMilestoneResponse(GoalMilestoneBase):
    id: int
    goal_id: int
    user_id: str
    achieved_value: float
    is_achieved: bool
    achieved_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class NutritionGoalResponse(NutritionGoalBase):
    id: int
    user_id: str
    current_value: float
    status: GoalStatus
    progress_percentage: float
    days_achieved: int
    total_days: int
    streak_days: int
    best_streak: int
    created_at: datetime
    updated_at: datetime
    progress_logs: List[GoalProgressLogResponse] = []
    milestones: List[GoalMilestoneResponse] = []
    
    class Config:
        from_attributes = True

class GoalTemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    goal_type: GoalType
    default_target_value: float
    default_unit: str
    default_frequency: GoalFrequency
    default_duration_days: Optional[int]
    category: Optional[str]
    difficulty_level: int
    is_public: bool
    usage_count: int
    instructions: Optional[str]
    tips: Optional[str]
    common_challenges: Optional[str]
    success_metrics: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Dashboard and summary schemas
class GoalSummary(BaseModel):
    total_goals: int
    active_goals: int
    completed_goals: int
    paused_goals: int
    total_streak_days: int
    best_streak: int
    goals_achieved_today: int
    goals_on_track: int
    goals_behind: int

class GoalProgressSummary(BaseModel):
    goal_id: int
    goal_name: str
    goal_type: GoalType
    target_value: float
    current_value: float
    progress_percentage: float
    status: GoalStatus
    streak_days: int
    days_remaining: Optional[int]
    is_on_track: bool
    last_achieved: Optional[datetime]
    next_milestone: Optional[GoalMilestoneResponse]

class GoalDashboard(BaseModel):
    summary: GoalSummary
    active_goals: List[GoalProgressSummary]
    recent_achievements: List[GoalProgressLogResponse]
    upcoming_milestones: List[GoalMilestoneResponse]
    streak_leaderboard: List[dict]  # Top goals by streak

# Search and filter schemas
class GoalFilter(BaseModel):
    status: Optional[GoalStatus] = None
    goal_type: Optional[GoalType] = None
    frequency: Optional[GoalFrequency] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    is_public: Optional[bool] = None
    start_date_from: Optional[datetime] = None
    start_date_to: Optional[datetime] = None
    target_date_from: Optional[datetime] = None
    target_date_to: Optional[datetime] = None

class GoalSearch(BaseModel):
    query: Optional[str] = None
    filters: Optional[GoalFilter] = None
    sort_by: str = Field("created_at", pattern="^(created_at|updated_at|progress_percentage|streak_days|priority)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

# Analytics schemas
class GoalAnalytics(BaseModel):
    goal_id: int
    goal_name: str
    goal_type: GoalType
    total_days: int
    days_achieved: int
    achievement_rate: float
    current_streak: int
    best_streak: int
    average_progress: float
    trend_direction: str  # "improving", "declining", "stable"
    weekly_progress: List[dict]
    monthly_progress: List[dict]
    milestone_achievements: int
    total_milestones: int

class GoalInsights(BaseModel):
    insights: List[str]
    recommendations: List[str]
    challenges: List[str]
    successes: List[str]
    next_actions: List[str]
