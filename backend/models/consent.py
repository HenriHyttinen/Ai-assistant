from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base
from .base import TimestampMixin

class DataConsent(Base, TimestampMixin):
    __tablename__ = "data_consent"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Overall consent
    consent_given = Column(Boolean, default=False)
    consent_date = Column(DateTime, nullable=True)
    privacy_policy_version = Column(String, default="1.0")
    
    # Data collection permissions
    data_collection = Column(Boolean, default=False)
    data_processing = Column(Boolean, default=False)
    data_sharing = Column(Boolean, default=False)
    
    # Feature-specific permissions
    ai_insights = Column(Boolean, default=False)
    email_notifications = Column(Boolean, default=False)
    analytics_tracking = Column(Boolean, default=False)
    
    # Specific data types
    health_metrics = Column(Boolean, default=False)
    activity_data = Column(Boolean, default=False)
    personal_info = Column(Boolean, default=False)
    usage_patterns = Column(Boolean, default=False)
    
    # Relationship
    user = relationship("User", back_populates="consent")
