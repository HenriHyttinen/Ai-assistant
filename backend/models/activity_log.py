from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)  # in minutes
    intensity = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    performed_at = Column(DateTime(timezone=True), nullable=True)  # When the activity was performed
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)  # When the log was created

    # Relationships
    user = relationship("User", back_populates="activity_logs") 