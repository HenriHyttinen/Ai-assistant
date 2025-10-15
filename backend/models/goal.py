from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from .base import TimestampMixin

class Goal(Base, TimestampMixin):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    target = Column(String, nullable=False)
    type = Column(String, nullable=False)  # "weight", "activity", "habit"
    deadline = Column(DateTime, nullable=True)
    status = Column(String, default="not_started")  # "not_started", "in_progress", "completed", "failed"
    progress = Column(Float, default=0.0)
    
    # Relationships
    user = relationship("User", back_populates="goals")
