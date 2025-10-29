from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .base import TimestampMixin

class HealthProfile(Base, TimestampMixin):
    __tablename__ = "health_profiles"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Demographics
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    
    # Physical metrics
    height = Column(Float, nullable=True)  # in cm
    weight = Column(Float, nullable=True)  # in kg
    
    # Lifestyle indicators
    occupation_type = Column(String, nullable=True)
    activity_level = Column(String, nullable=True)
    
    # Dietary preferences and restrictions
    dietary_preferences = Column(String, nullable=True)  # JSON string of preferences
    dietary_restrictions = Column(String, nullable=True)  # JSON string of restrictions
    meal_preferences = Column(String, nullable=True)  # breakfast, lunch, dinner preferences
    
    # Fitness goals
    fitness_goal = Column(String, nullable=True)
    target_weight = Column(Float, nullable=True)
    target_activity_level = Column(String, nullable=True)
    
    # Exercise preferences
    preferred_exercise_time = Column(String, nullable=True)
    preferred_exercise_environment = Column(String, nullable=True)
    weekly_activity_frequency = Column(Integer, nullable=True)
    exercise_types = Column(String, nullable=True)  # JSON string of exercise types
    average_session_duration = Column(String, nullable=True)
    
    # Fitness assessment
    fitness_level = Column(String, nullable=True)
    endurance_level = Column(Integer, nullable=True)  # 1-10 scale
    strength_indicators = Column(String, nullable=True)  # JSON string of strength metrics
    current_endurance_minutes = Column(Integer, nullable=True)  # How long can run/walk
    pushup_count = Column(Integer, nullable=True)  # Number of pushups can do
    squat_count = Column(Integer, nullable=True)  # Number of squats can do

    # Relationships
    # user = relationship("User", back_populates="health_profile")
    metrics_history = relationship("MetricsHistory", back_populates="health_profile") 