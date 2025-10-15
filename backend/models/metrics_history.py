from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class MetricsHistory(Base):
    __tablename__ = "metrics_history"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    health_profile_id = Column(Integer, ForeignKey("health_profiles.id"), nullable=False)
    weight = Column(Float, nullable=True)  # in kg
    bmi = Column(Float, nullable=True)
    wellness_score = Column(Float, nullable=True)
    recorded_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    health_profile = relationship("HealthProfile", back_populates="metrics_history") 