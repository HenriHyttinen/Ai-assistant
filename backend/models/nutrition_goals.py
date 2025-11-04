from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base, TimestampMixin
import enum

class GoalType(str, enum.Enum):
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

class GoalStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class GoalFrequency(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class NutritionGoal(Base, TimestampMixin):
    __tablename__ = "nutrition_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    goal_type = Column(Enum(GoalType, native_enum=False), nullable=False)
    goal_name = Column(String, nullable=False)  # Custom name for the goal
    description = Column(Text, nullable=True)  # Optional description
    
    # Goal targets
    target_value = Column(Float, nullable=False)  # Target value to achieve
    current_value = Column(Float, default=0.0)  # Current progress value
    unit = Column(String, nullable=False)  # Unit of measurement (g, mg, cal, etc.)
    
    # Goal settings
    frequency = Column(Enum(GoalFrequency, native_enum=False), default=GoalFrequency.DAILY)
    start_date = Column(DateTime, nullable=False)
    target_date = Column(DateTime, nullable=True)  # Optional end date
    is_flexible = Column(Boolean, default=True)  # Can be adjusted over time
    
    # Goal status
    status = Column(Enum(GoalStatus, native_enum=False), default=GoalStatus.ACTIVE)
    priority = Column(Integer, default=1)  # 1-5 priority level
    is_public = Column(Boolean, default=False)  # Share with community
    
    # Progress tracking
    progress_percentage = Column(Float, default=0.0)
    days_achieved = Column(Integer, default=0)  # Days where goal was met
    total_days = Column(Integer, default=0)  # Total days tracked
    streak_days = Column(Integer, default=0)  # Current streak
    best_streak = Column(Integer, default=0)  # Best streak achieved
    
    # Relationships
    user = relationship("User")
    progress_logs = relationship("GoalProgressLog", cascade="all, delete-orphan")
    milestones = relationship("GoalMilestone", cascade="all, delete-orphan")

class GoalProgressLog(Base, TimestampMixin):
    __tablename__ = "goal_progress_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("nutrition_goals.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Progress data
    date = Column(DateTime, nullable=False, index=True)
    achieved_value = Column(Float, nullable=False)  # Value achieved on this date
    target_value = Column(Float, nullable=False)  # Target for this date
    is_achieved = Column(Boolean, default=False)  # Whether goal was met
    progress_percentage = Column(Float, default=0.0)  # Percentage achieved
    
    # Context
    notes = Column(Text, nullable=True)  # Optional notes about this day
    difficulty_rating = Column(Integer, nullable=True)  # 1-5 how hard it was
    mood_rating = Column(Integer, nullable=True)  # 1-5 mood while pursuing goal
    
    # Relationships
    goal = relationship("NutritionGoal", overlaps="progress_logs")
    user = relationship("User")

class GoalMilestone(Base, TimestampMixin):
    __tablename__ = "goal_milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("nutrition_goals.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Milestone details
    milestone_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    target_value = Column(Float, nullable=False)  # Value needed to achieve milestone
    achieved_value = Column(Float, default=0.0)  # Current progress toward milestone
    is_achieved = Column(Boolean, default=False)
    achieved_date = Column(DateTime, nullable=True)
    
    # Milestone settings
    is_automatic = Column(Boolean, default=True)  # Auto-created or user-created
    reward_description = Column(Text, nullable=True)  # Optional reward for achieving
    
    # Relationships
    goal = relationship("NutritionGoal", overlaps="milestones")
    user = relationship("User")

class GoalTemplate(Base, TimestampMixin):
    __tablename__ = "goal_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    goal_type = Column(Enum(GoalType, native_enum=False), nullable=False)
    
    # Template settings
    default_target_value = Column(Float, nullable=False)
    default_unit = Column(String, nullable=False)
    default_frequency = Column(Enum(GoalFrequency), default=GoalFrequency.DAILY)
    default_duration_days = Column(Integer, nullable=True)  # Suggested duration
    
    # Template metadata
    category = Column(String, nullable=True)  # e.g., "weight_loss", "muscle_gain", "health"
    difficulty_level = Column(Integer, default=1)  # 1-5 difficulty
    is_public = Column(Boolean, default=True)  # Available to all users
    usage_count = Column(Integer, default=0)  # How many times used
    
    # Template content
    instructions = Column(Text, nullable=True)  # How to achieve this goal
    tips = Column(Text, nullable=True)  # Tips for success
    common_challenges = Column(Text, nullable=True)  # Common obstacles
    success_metrics = Column(Text, nullable=True)  # How to measure success
