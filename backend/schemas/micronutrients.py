from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class MicronutrientData(BaseModel):
    """Base micronutrient data structure"""
    vitamin_d: Optional[float] = Field(None, description="Vitamin D in mcg")
    vitamin_b12: Optional[float] = Field(None, description="Vitamin B12 in mcg")
    iron: Optional[float] = Field(None, description="Iron in mg")
    calcium: Optional[float] = Field(None, description="Calcium in mg")
    magnesium: Optional[float] = Field(None, description="Magnesium in mg")
    vitamin_c: Optional[float] = Field(None, description="Vitamin C in mg")
    folate: Optional[float] = Field(None, description="Folate in mcg")
    zinc: Optional[float] = Field(None, description="Zinc in mg")
    potassium: Optional[float] = Field(None, description="Potassium in mg")
    fiber: Optional[float] = Field(None, description="Fiber in g")
    
    # Additional micronutrients
    vitamin_a: Optional[float] = Field(None, description="Vitamin A in IU")
    vitamin_e: Optional[float] = Field(None, description="Vitamin E in mg")
    vitamin_k: Optional[float] = Field(None, description="Vitamin K in mcg")
    thiamine: Optional[float] = Field(None, description="Thiamine (B1) in mg")
    riboflavin: Optional[float] = Field(None, description="Riboflavin (B2) in mg")
    niacin: Optional[float] = Field(None, description="Niacin (B3) in mg")
    selenium: Optional[float] = Field(None, description="Selenium in mcg")
    phosphorus: Optional[float] = Field(None, description="Phosphorus in mg")
    omega_3: Optional[float] = Field(None, description="Omega-3 in g")
    omega_6: Optional[float] = Field(None, description="Omega-6 in g")

class MicronutrientGoalCreate(BaseModel):
    """Create micronutrient goals"""
    vitamin_d_target: Optional[float] = None
    vitamin_b12_target: Optional[float] = None
    iron_target: Optional[float] = None
    calcium_target: Optional[float] = None
    magnesium_target: Optional[float] = None
    vitamin_c_target: Optional[float] = None
    folate_target: Optional[float] = None
    zinc_target: Optional[float] = None
    potassium_target: Optional[float] = None
    fiber_target: Optional[float] = None
    
    # Additional micronutrients
    vitamin_a_target: Optional[float] = None
    vitamin_e_target: Optional[float] = None
    vitamin_k_target: Optional[float] = None
    thiamine_target: Optional[float] = None
    riboflavin_target: Optional[float] = None
    niacin_target: Optional[float] = None
    selenium_target: Optional[float] = None
    phosphorus_target: Optional[float] = None
    omega_3_target: Optional[float] = None
    omega_6_target: Optional[float] = None

class MicronutrientGoalResponse(BaseModel):
    """Micronutrient goal response"""
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # All the micronutrient target fields
    vitamin_d_target: Optional[float] = None
    vitamin_b12_target: Optional[float] = None
    iron_target: Optional[float] = None
    calcium_target: Optional[float] = None
    magnesium_target: Optional[float] = None
    vitamin_c_target: Optional[float] = None
    folate_target: Optional[float] = None
    zinc_target: Optional[float] = None
    potassium_target: Optional[float] = None
    fiber_target: Optional[float] = None
    vitamin_a_target: Optional[float] = None
    vitamin_e_target: Optional[float] = None
    vitamin_k_target: Optional[float] = None
    thiamine_target: Optional[float] = None
    riboflavin_target: Optional[float] = None
    niacin_target: Optional[float] = None
    selenium_target: Optional[float] = None
    phosphorus_target: Optional[float] = None
    omega_3_target: Optional[float] = None
    omega_6_target: Optional[float] = None

class DailyMicronutrientIntakeCreate(BaseModel):
    """Create daily micronutrient intake"""
    date: datetime
    vitamin_d_intake: Optional[float] = 0.0
    vitamin_b12_intake: Optional[float] = 0.0
    iron_intake: Optional[float] = 0.0
    calcium_intake: Optional[float] = 0.0
    magnesium_intake: Optional[float] = 0.0
    vitamin_c_intake: Optional[float] = 0.0
    folate_intake: Optional[float] = 0.0
    zinc_intake: Optional[float] = 0.0
    potassium_intake: Optional[float] = 0.0
    fiber_intake: Optional[float] = 0.0
    
    # Additional micronutrients
    vitamin_a_intake: Optional[float] = 0.0
    vitamin_e_intake: Optional[float] = 0.0
    vitamin_k_intake: Optional[float] = 0.0
    thiamine_intake: Optional[float] = 0.0
    riboflavin_intake: Optional[float] = 0.0
    niacin_intake: Optional[float] = 0.0
    selenium_intake: Optional[float] = 0.0
    phosphorus_intake: Optional[float] = 0.0
    omega_3_intake: Optional[float] = 0.0
    omega_6_intake: Optional[float] = 0.0

class DailyMicronutrientIntakeResponse(BaseModel):
    """Daily micronutrient intake response"""
    id: int
    user_id: int
    date: datetime
    created_at: datetime
    updated_at: datetime
    
    # All the micronutrient fields
    vitamin_d: Optional[float] = 0.0
    vitamin_b12: Optional[float] = 0.0
    iron: Optional[float] = 0.0
    calcium: Optional[float] = 0.0
    magnesium: Optional[float] = 0.0
    vitamin_c: Optional[float] = 0.0
    folate: Optional[float] = 0.0
    zinc: Optional[float] = 0.0
    potassium: Optional[float] = 0.0
    fiber: Optional[float] = 0.0
    vitamin_a: Optional[float] = 0.0
    vitamin_e: Optional[float] = 0.0
    vitamin_k: Optional[float] = 0.0
    thiamine: Optional[float] = 0.0
    riboflavin: Optional[float] = 0.0
    niacin: Optional[float] = 0.0
    selenium: Optional[float] = 0.0
    phosphorus: Optional[float] = 0.0
    omega_3: Optional[float] = 0.0
    omega_6: Optional[float] = 0.0

class MicronutrientDeficiencyResponse(BaseModel):
    """Micronutrient deficiency response"""
    id: int
    user_id: int
    micronutrient_name: str
    deficiency_level: str
    current_intake: float
    recommended_intake: float
    deficiency_percentage: float
    food_suggestions: Optional[str] = None
    supplement_suggestions: Optional[str] = None
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class MicronutrientAnalysis(BaseModel):
    """Micronutrient analysis for a period"""
    period_start: datetime
    period_end: datetime
    average_intake: MicronutrientData
    goal_targets: MicronutrientData
    deficiencies: List[MicronutrientDeficiencyResponse]
    recommendations: List[str]
    overall_score: float  # 0-100 score for micronutrient adequacy

class MicronutrientDashboard(BaseModel):
    """Micronutrient dashboard summary"""
    current_goals: MicronutrientGoalResponse
    today_intake: Optional[DailyMicronutrientIntakeResponse]
    weekly_average: MicronutrientData
    deficiencies: List[MicronutrientDeficiencyResponse]
    recommendations: List[str]
    overall_score: float
    trend_data: List[Dict[str, Any]]  # For charts

class MicronutrientSearchFilter(BaseModel):
    """Filter for micronutrient-based recipe search"""
    min_vitamin_d: Optional[float] = None
    min_vitamin_b12: Optional[float] = None
    min_iron: Optional[float] = None
    min_calcium: Optional[float] = None
    min_magnesium: Optional[float] = None
    min_vitamin_c: Optional[float] = None
    min_folate: Optional[float] = None
    min_zinc: Optional[float] = None
    min_potassium: Optional[float] = None
    min_fiber: Optional[float] = None
    
    # Additional filters
    min_vitamin_a: Optional[float] = None
    min_vitamin_e: Optional[float] = None
    min_omega_3: Optional[float] = None
    min_selenium: Optional[float] = None
