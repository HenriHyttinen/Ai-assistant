from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
from .base import TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String, nullable=True)
    backup_codes = Column(String, nullable=True)  # JSON string of backup codes
    oauth_provider = Column(String, nullable=True)
    oauth_id = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)

    # Relationships - using string references to avoid circular imports
    health_profile = relationship("HealthProfile", back_populates="user", uselist=False)
    activity_logs = relationship("ActivityLog", back_populates="user")
    goals = relationship("Goal", back_populates="user")
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    consent = relationship("DataConsent", back_populates="user", uselist=False)
    achievements = relationship("UserAchievement", back_populates="user")
    
    # Nutrition-related relationships
    nutrition_preferences = relationship("UserNutritionPreferences", back_populates="user", uselist=False)
    meal_plans = relationship("MealPlan", back_populates="user")
    nutritional_logs = relationship("NutritionalLog", back_populates="user")
    shopping_lists = relationship("ShoppingList", back_populates="user") 