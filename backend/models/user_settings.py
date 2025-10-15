from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from .base import TimestampMixin

class UserSettings(Base, TimestampMixin):
    __tablename__ = "user_settings"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    weekly_reports = Column(Boolean, default=True)
    ai_insights = Column(Boolean, default=True)
    
    # Privacy settings
    data_sharing = Column(Boolean, default=False)
    
    # User preferences
    measurement_system = Column(String, default="metric")  # "metric" or "imperial"
    language = Column(String, default="en")  # Language code (en, es, fr, de, etc.)
    
    # Relationship
    user = relationship("User", back_populates="settings")
