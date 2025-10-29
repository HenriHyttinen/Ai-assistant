from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base, TimestampMixin

class MicronutrientGoal(Base, TimestampMixin):
    __tablename__ = "micronutrient_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Micronutrient targets (daily recommended values)
    vitamin_d_target = Column(Float, nullable=True)  # mcg
    vitamin_b12_target = Column(Float, nullable=True)  # mcg
    iron_target = Column(Float, nullable=True)  # mg
    calcium_target = Column(Float, nullable=True)  # mg
    magnesium_target = Column(Float, nullable=True)  # mg
    vitamin_c_target = Column(Float, nullable=True)  # mg
    folate_target = Column(Float, nullable=True)  # mcg
    zinc_target = Column(Float, nullable=True)  # mg
    potassium_target = Column(Float, nullable=True)  # mg
    fiber_target = Column(Float, nullable=True)  # g
    
    # Additional micronutrients
    vitamin_a_target = Column(Float, nullable=True)  # IU
    vitamin_e_target = Column(Float, nullable=True)  # mg
    vitamin_k_target = Column(Float, nullable=True)  # mcg
    thiamine_target = Column(Float, nullable=True)  # mg (B1)
    riboflavin_target = Column(Float, nullable=True)  # mg (B2)
    niacin_target = Column(Float, nullable=True)  # mg (B3)
    selenium_target = Column(Float, nullable=True)  # mcg
    phosphorus_target = Column(Float, nullable=True)  # mg
    omega_3_target = Column(Float, nullable=True)  # g
    omega_6_target = Column(Float, nullable=True)  # g
    
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User")

class DailyMicronutrientIntake(Base, TimestampMixin):
    __tablename__ = "daily_micronutrient_intakes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    
    # Daily micronutrient intake
    vitamin_d_intake = Column(Float, default=0.0)  # mcg
    vitamin_b12_intake = Column(Float, default=0.0)  # mcg
    iron_intake = Column(Float, default=0.0)  # mg
    calcium_intake = Column(Float, default=0.0)  # mg
    magnesium_intake = Column(Float, default=0.0)  # mg
    vitamin_c_intake = Column(Float, default=0.0)  # mg
    folate_intake = Column(Float, default=0.0)  # mcg
    zinc_intake = Column(Float, default=0.0)  # mg
    potassium_intake = Column(Float, default=0.0)  # mg
    fiber_intake = Column(Float, default=0.0)  # g
    
    # Additional micronutrients
    vitamin_a_intake = Column(Float, default=0.0)  # IU
    vitamin_e_intake = Column(Float, default=0.0)  # mg
    vitamin_k_intake = Column(Float, default=0.0)  # mcg
    thiamine_intake = Column(Float, default=0.0)  # mg (B1)
    riboflavin_intake = Column(Float, default=0.0)  # mg (B2)
    niacin_intake = Column(Float, default=0.0)  # mg (B3)
    selenium_intake = Column(Float, default=0.0)  # mcg
    phosphorus_intake = Column(Float, default=0.0)  # mg
    omega_3_intake = Column(Float, default=0.0)  # g
    omega_6_intake = Column(Float, default=0.0)  # g
    
    # Relationships
    user = relationship("User")

class MicronutrientDeficiency(Base, TimestampMixin):
    __tablename__ = "micronutrient_deficiencies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Deficiency tracking
    micronutrient_name = Column(String, nullable=False)  # e.g., "vitamin_d", "iron"
    deficiency_level = Column(String, nullable=False)  # "mild", "moderate", "severe"
    current_intake = Column(Float, nullable=False)  # current daily intake
    recommended_intake = Column(Float, nullable=False)  # recommended daily intake
    deficiency_percentage = Column(Float, nullable=False)  # percentage below recommended
    
    # Recommendations
    food_suggestions = Column(String, nullable=True)  # JSON string of food recommendations
    supplement_suggestions = Column(String, nullable=True)  # supplement recommendations
    
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User")
