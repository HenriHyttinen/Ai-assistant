from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

class NutrientDensityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class GlycemicIndexLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class FoodProcessingLevel(str, Enum):
    UNPROCESSED = "unprocessed"
    MINIMALLY_PROCESSED = "minimally_processed"
    PROCESSED = "processed"
    ULTRA_PROCESSED = "ultra_processed"

# Nutritional Profile Schemas
class NutritionalProfileBase(BaseModel):
    profile_name: str
    is_default: bool = False
    
    # Basic nutritional targets
    daily_calories: float = Field(..., gt=0)
    protein_grams: float = Field(..., ge=0)
    carbs_grams: float = Field(..., ge=0)
    fat_grams: float = Field(..., ge=0)
    fiber_grams: float = Field(..., ge=0)
    sugar_grams: float = Field(..., ge=0)
    sodium_mg: float = Field(..., ge=0)
    
    # Advanced macronutrient targets
    saturated_fat_grams: Optional[float] = Field(None, ge=0)
    monounsaturated_fat_grams: Optional[float] = Field(None, ge=0)
    polyunsaturated_fat_grams: Optional[float] = Field(None, ge=0)
    trans_fat_grams: Optional[float] = Field(None, ge=0)
    cholesterol_mg: Optional[float] = Field(None, ge=0)
    
    # Carbohydrate breakdown
    total_carbs_grams: Optional[float] = Field(None, ge=0)
    net_carbs_grams: Optional[float] = Field(None, ge=0)
    simple_carbs_grams: Optional[float] = Field(None, ge=0)
    complex_carbs_grams: Optional[float] = Field(None, ge=0)
    starch_grams: Optional[float] = Field(None, ge=0)
    
    # Micronutrient targets
    vitamin_a_mcg: Optional[float] = Field(None, ge=0)
    vitamin_c_mg: Optional[float] = Field(None, ge=0)
    vitamin_d_mcg: Optional[float] = Field(None, ge=0)
    vitamin_e_mg: Optional[float] = Field(None, ge=0)
    vitamin_k_mcg: Optional[float] = Field(None, ge=0)
    thiamine_mg: Optional[float] = Field(None, ge=0)
    riboflavin_mg: Optional[float] = Field(None, ge=0)
    niacin_mg: Optional[float] = Field(None, ge=0)
    pantothenic_acid_mg: Optional[float] = Field(None, ge=0)
    pyridoxine_mg: Optional[float] = Field(None, ge=0)
    biotin_mcg: Optional[float] = Field(None, ge=0)
    folate_mcg: Optional[float] = Field(None, ge=0)
    cobalamin_mcg: Optional[float] = Field(None, ge=0)
    
    # Minerals
    calcium_mg: Optional[float] = Field(None, ge=0)
    iron_mg: Optional[float] = Field(None, ge=0)
    magnesium_mg: Optional[float] = Field(None, ge=0)
    phosphorus_mg: Optional[float] = Field(None, ge=0)
    potassium_mg: Optional[float] = Field(None, ge=0)
    zinc_mg: Optional[float] = Field(None, ge=0)
    copper_mg: Optional[float] = Field(None, ge=0)
    manganese_mg: Optional[float] = Field(None, ge=0)
    selenium_mcg: Optional[float] = Field(None, ge=0)
    iodine_mcg: Optional[float] = Field(None, ge=0)
    fluoride_mg: Optional[float] = Field(None, ge=0)
    
    # Trace minerals
    chromium_mcg: Optional[float] = Field(None, ge=0)
    molybdenum_mcg: Optional[float] = Field(None, ge=0)
    boron_mg: Optional[float] = Field(None, ge=0)
    silicon_mg: Optional[float] = Field(None, ge=0)
    vanadium_mcg: Optional[float] = Field(None, ge=0)
    
    # Fatty acids
    omega_3_grams: Optional[float] = Field(None, ge=0)
    omega_6_grams: Optional[float] = Field(None, ge=0)
    omega_9_grams: Optional[float] = Field(None, ge=0)
    dha_grams: Optional[float] = Field(None, ge=0)
    epa_grams: Optional[float] = Field(None, ge=0)
    ala_grams: Optional[float] = Field(None, ge=0)
    la_grams: Optional[float] = Field(None, ge=0)
    
    # Amino acids (essential)
    histidine_grams: Optional[float] = Field(None, ge=0)
    isoleucine_grams: Optional[float] = Field(None, ge=0)
    leucine_grams: Optional[float] = Field(None, ge=0)
    lysine_grams: Optional[float] = Field(None, ge=0)
    methionine_grams: Optional[float] = Field(None, ge=0)
    phenylalanine_grams: Optional[float] = Field(None, ge=0)
    threonine_grams: Optional[float] = Field(None, ge=0)
    tryptophan_grams: Optional[float] = Field(None, ge=0)
    valine_grams: Optional[float] = Field(None, ge=0)
    
    # Phytochemicals and antioxidants
    beta_carotene_mcg: Optional[float] = Field(None, ge=0)
    lycopene_mcg: Optional[float] = Field(None, ge=0)
    lutein_mcg: Optional[float] = Field(None, ge=0)
    zeaxanthin_mcg: Optional[float] = Field(None, ge=0)
    anthocyanins_mg: Optional[float] = Field(None, ge=0)
    flavonoids_mg: Optional[float] = Field(None, ge=0)
    polyphenols_mg: Optional[float] = Field(None, ge=0)
    resveratrol_mg: Optional[float] = Field(None, ge=0)
    quercetin_mg: Optional[float] = Field(None, ge=0)
    catechins_mg: Optional[float] = Field(None, ge=0)
    
    # Other bioactive compounds
    caffeine_mg: Optional[float] = Field(None, ge=0)
    theobromine_mg: Optional[float] = Field(None, ge=0)
    theophylline_mg: Optional[float] = Field(None, ge=0)
    capsaicin_mg: Optional[float] = Field(None, ge=0)
    curcumin_mg: Optional[float] = Field(None, ge=0)
    gingerol_mg: Optional[float] = Field(None, ge=0)
    allicin_mg: Optional[float] = Field(None, ge=0)
    
    # Water and hydration
    water_ml: Optional[float] = Field(None, ge=0)
    alcohol_grams: Optional[float] = Field(None, ge=0)

class NutritionalProfileCreate(NutritionalProfileBase):
    pass

class NutritionalProfileUpdate(BaseModel):
    profile_name: Optional[str] = None
    is_default: Optional[bool] = None
    
    # Basic nutritional targets
    daily_calories: Optional[float] = Field(None, gt=0)
    protein_grams: Optional[float] = Field(None, ge=0)
    carbs_grams: Optional[float] = Field(None, ge=0)
    fat_grams: Optional[float] = Field(None, ge=0)
    fiber_grams: Optional[float] = Field(None, ge=0)
    sugar_grams: Optional[float] = Field(None, ge=0)
    sodium_mg: Optional[float] = Field(None, ge=0)
    
    # Advanced macronutrient targets
    saturated_fat_grams: Optional[float] = Field(None, ge=0)
    monounsaturated_fat_grams: Optional[float] = Field(None, ge=0)
    polyunsaturated_fat_grams: Optional[float] = Field(None, ge=0)
    trans_fat_grams: Optional[float] = Field(None, ge=0)
    cholesterol_mg: Optional[float] = Field(None, ge=0)
    
    # Carbohydrate breakdown
    total_carbs_grams: Optional[float] = Field(None, ge=0)
    net_carbs_grams: Optional[float] = Field(None, ge=0)
    simple_carbs_grams: Optional[float] = Field(None, ge=0)
    complex_carbs_grams: Optional[float] = Field(None, ge=0)
    starch_grams: Optional[float] = Field(None, ge=0)
    
    # Micronutrient targets
    vitamin_a_mcg: Optional[float] = Field(None, ge=0)
    vitamin_c_mg: Optional[float] = Field(None, ge=0)
    vitamin_d_mcg: Optional[float] = Field(None, ge=0)
    vitamin_e_mg: Optional[float] = Field(None, ge=0)
    vitamin_k_mcg: Optional[float] = Field(None, ge=0)
    thiamine_mg: Optional[float] = Field(None, ge=0)
    riboflavin_mg: Optional[float] = Field(None, ge=0)
    niacin_mg: Optional[float] = Field(None, ge=0)
    pantothenic_acid_mg: Optional[float] = Field(None, ge=0)
    pyridoxine_mg: Optional[float] = Field(None, ge=0)
    biotin_mcg: Optional[float] = Field(None, ge=0)
    folate_mcg: Optional[float] = Field(None, ge=0)
    cobalamin_mcg: Optional[float] = Field(None, ge=0)
    
    # Minerals
    calcium_mg: Optional[float] = Field(None, ge=0)
    iron_mg: Optional[float] = Field(None, ge=0)
    magnesium_mg: Optional[float] = Field(None, ge=0)
    phosphorus_mg: Optional[float] = Field(None, ge=0)
    potassium_mg: Optional[float] = Field(None, ge=0)
    zinc_mg: Optional[float] = Field(None, ge=0)
    copper_mg: Optional[float] = Field(None, ge=0)
    manganese_mg: Optional[float] = Field(None, ge=0)
    selenium_mcg: Optional[float] = Field(None, ge=0)
    iodine_mcg: Optional[float] = Field(None, ge=0)
    fluoride_mg: Optional[float] = Field(None, ge=0)
    
    # Trace minerals
    chromium_mcg: Optional[float] = Field(None, ge=0)
    molybdenum_mcg: Optional[float] = Field(None, ge=0)
    boron_mg: Optional[float] = Field(None, ge=0)
    silicon_mg: Optional[float] = Field(None, ge=0)
    vanadium_mcg: Optional[float] = Field(None, ge=0)
    
    # Fatty acids
    omega_3_grams: Optional[float] = Field(None, ge=0)
    omega_6_grams: Optional[float] = Field(None, ge=0)
    omega_9_grams: Optional[float] = Field(None, ge=0)
    dha_grams: Optional[float] = Field(None, ge=0)
    epa_grams: Optional[float] = Field(None, ge=0)
    ala_grams: Optional[float] = Field(None, ge=0)
    la_grams: Optional[float] = Field(None, ge=0)
    
    # Amino acids (essential)
    histidine_grams: Optional[float] = Field(None, ge=0)
    isoleucine_grams: Optional[float] = Field(None, ge=0)
    leucine_grams: Optional[float] = Field(None, ge=0)
    lysine_grams: Optional[float] = Field(None, ge=0)
    methionine_grams: Optional[float] = Field(None, ge=0)
    phenylalanine_grams: Optional[float] = Field(None, ge=0)
    threonine_grams: Optional[float] = Field(None, ge=0)
    tryptophan_grams: Optional[float] = Field(None, ge=0)
    valine_grams: Optional[float] = Field(None, ge=0)
    
    # Phytochemicals and antioxidants
    beta_carotene_mcg: Optional[float] = Field(None, ge=0)
    lycopene_mcg: Optional[float] = Field(None, ge=0)
    lutein_mcg: Optional[float] = Field(None, ge=0)
    zeaxanthin_mcg: Optional[float] = Field(None, ge=0)
    anthocyanins_mg: Optional[float] = Field(None, ge=0)
    flavonoids_mg: Optional[float] = Field(None, ge=0)
    polyphenols_mg: Optional[float] = Field(None, ge=0)
    resveratrol_mg: Optional[float] = Field(None, ge=0)
    quercetin_mg: Optional[float] = Field(None, ge=0)
    catechins_mg: Optional[float] = Field(None, ge=0)
    
    # Other bioactive compounds
    caffeine_mg: Optional[float] = Field(None, ge=0)
    theobromine_mg: Optional[float] = Field(None, ge=0)
    theophylline_mg: Optional[float] = Field(None, ge=0)
    capsaicin_mg: Optional[float] = Field(None, ge=0)
    curcumin_mg: Optional[float] = Field(None, ge=0)
    gingerol_mg: Optional[float] = Field(None, ge=0)
    allicin_mg: Optional[float] = Field(None, ge=0)
    
    # Water and hydration
    water_ml: Optional[float] = Field(None, ge=0)
    alcohol_grams: Optional[float] = Field(None, ge=0)

class NutritionalProfileResponse(NutritionalProfileBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Daily Nutritional Intake Schemas
class DailyNutritionalIntakeBase(BaseModel):
    intake_date: date
    profile_id: Optional[int] = None
    
    # Basic macronutrients
    calories_consumed: float = Field(0.0, ge=0)
    protein_grams: float = Field(0.0, ge=0)
    carbs_grams: float = Field(0.0, ge=0)
    fat_grams: float = Field(0.0, ge=0)
    fiber_grams: float = Field(0.0, ge=0)
    sugar_grams: float = Field(0.0, ge=0)
    sodium_mg: float = Field(0.0, ge=0)
    
    # Advanced macronutrients
    saturated_fat_grams: Optional[float] = Field(0.0, ge=0)
    monounsaturated_fat_grams: Optional[float] = Field(0.0, ge=0)
    polyunsaturated_fat_grams: Optional[float] = Field(0.0, ge=0)
    trans_fat_grams: Optional[float] = Field(0.0, ge=0)
    cholesterol_mg: Optional[float] = Field(0.0, ge=0)
    
    # Carbohydrate breakdown
    total_carbs_grams: Optional[float] = Field(0.0, ge=0)
    net_carbs_grams: Optional[float] = Field(0.0, ge=0)
    simple_carbs_grams: Optional[float] = Field(0.0, ge=0)
    complex_carbs_grams: Optional[float] = Field(0.0, ge=0)
    starch_grams: Optional[float] = Field(0.0, ge=0)
    
    # Micronutrients (comprehensive)
    vitamin_a_mcg: Optional[float] = Field(0.0, ge=0)
    vitamin_c_mg: Optional[float] = Field(0.0, ge=0)
    vitamin_d_mcg: Optional[float] = Field(0.0, ge=0)
    vitamin_e_mg: Optional[float] = Field(0.0, ge=0)
    vitamin_k_mcg: Optional[float] = Field(0.0, ge=0)
    thiamine_mg: Optional[float] = Field(0.0, ge=0)
    riboflavin_mg: Optional[float] = Field(0.0, ge=0)
    niacin_mg: Optional[float] = Field(0.0, ge=0)
    pantothenic_acid_mg: Optional[float] = Field(0.0, ge=0)
    pyridoxine_mg: Optional[float] = Field(0.0, ge=0)
    biotin_mcg: Optional[float] = Field(0.0, ge=0)
    folate_mcg: Optional[float] = Field(0.0, ge=0)
    cobalamin_mcg: Optional[float] = Field(0.0, ge=0)
    
    # Minerals
    calcium_mg: Optional[float] = Field(0.0, ge=0)
    iron_mg: Optional[float] = Field(0.0, ge=0)
    magnesium_mg: Optional[float] = Field(0.0, ge=0)
    phosphorus_mg: Optional[float] = Field(0.0, ge=0)
    potassium_mg: Optional[float] = Field(0.0, ge=0)
    zinc_mg: Optional[float] = Field(0.0, ge=0)
    copper_mg: Optional[float] = Field(0.0, ge=0)
    manganese_mg: Optional[float] = Field(0.0, ge=0)
    selenium_mcg: Optional[float] = Field(0.0, ge=0)
    iodine_mcg: Optional[float] = Field(0.0, ge=0)
    fluoride_mg: Optional[float] = Field(0.0, ge=0)
    
    # Trace minerals
    chromium_mcg: Optional[float] = Field(0.0, ge=0)
    molybdenum_mcg: Optional[float] = Field(0.0, ge=0)
    boron_mg: Optional[float] = Field(0.0, ge=0)
    silicon_mg: Optional[float] = Field(0.0, ge=0)
    vanadium_mcg: Optional[float] = Field(0.0, ge=0)
    
    # Fatty acids
    omega_3_grams: Optional[float] = Field(0.0, ge=0)
    omega_6_grams: Optional[float] = Field(0.0, ge=0)
    omega_9_grams: Optional[float] = Field(0.0, ge=0)
    dha_grams: Optional[float] = Field(0.0, ge=0)
    epa_grams: Optional[float] = Field(0.0, ge=0)
    ala_grams: Optional[float] = Field(0.0, ge=0)
    la_grams: Optional[float] = Field(0.0, ge=0)
    
    # Amino acids (essential)
    histidine_grams: Optional[float] = Field(0.0, ge=0)
    isoleucine_grams: Optional[float] = Field(0.0, ge=0)
    leucine_grams: Optional[float] = Field(0.0, ge=0)
    lysine_grams: Optional[float] = Field(0.0, ge=0)
    methionine_grams: Optional[float] = Field(0.0, ge=0)
    phenylalanine_grams: Optional[float] = Field(0.0, ge=0)
    threonine_grams: Optional[float] = Field(0.0, ge=0)
    tryptophan_grams: Optional[float] = Field(0.0, ge=0)
    valine_grams: Optional[float] = Field(0.0, ge=0)
    
    # Phytochemicals and antioxidants
    beta_carotene_mcg: Optional[float] = Field(0.0, ge=0)
    lycopene_mcg: Optional[float] = Field(0.0, ge=0)
    lutein_mcg: Optional[float] = Field(0.0, ge=0)
    zeaxanthin_mcg: Optional[float] = Field(0.0, ge=0)
    anthocyanins_mg: Optional[float] = Field(0.0, ge=0)
    flavonoids_mg: Optional[float] = Field(0.0, ge=0)
    polyphenols_mg: Optional[float] = Field(0.0, ge=0)
    resveratrol_mg: Optional[float] = Field(0.0, ge=0)
    quercetin_mg: Optional[float] = Field(0.0, ge=0)
    catechins_mg: Optional[float] = Field(0.0, ge=0)
    
    # Other bioactive compounds
    caffeine_mg: Optional[float] = Field(0.0, ge=0)
    theobromine_mg: Optional[float] = Field(0.0, ge=0)
    theophylline_mg: Optional[float] = Field(0.0, ge=0)
    capsaicin_mg: Optional[float] = Field(0.0, ge=0)
    curcumin_mg: Optional[float] = Field(0.0, ge=0)
    gingerol_mg: Optional[float] = Field(0.0, ge=0)
    allicin_mg: Optional[float] = Field(0.0, ge=0)
    
    # Water and hydration
    water_ml: Optional[float] = Field(0.0, ge=0)
    alcohol_grams: Optional[float] = Field(0.0, ge=0)

class DailyNutritionalIntakeCreate(DailyNutritionalIntakeBase):
    pass

class DailyNutritionalIntakeUpdate(BaseModel):
    # Basic macronutrients
    calories_consumed: Optional[float] = Field(None, ge=0)
    protein_grams: Optional[float] = Field(None, ge=0)
    carbs_grams: Optional[float] = Field(None, ge=0)
    fat_grams: Optional[float] = Field(None, ge=0)
    fiber_grams: Optional[float] = Field(None, ge=0)
    sugar_grams: Optional[float] = Field(None, ge=0)
    sodium_mg: Optional[float] = Field(None, ge=0)
    
    # Advanced macronutrients
    saturated_fat_grams: Optional[float] = Field(None, ge=0)
    monounsaturated_fat_grams: Optional[float] = Field(None, ge=0)
    polyunsaturated_fat_grams: Optional[float] = Field(None, ge=0)
    trans_fat_grams: Optional[float] = Field(None, ge=0)
    cholesterol_mg: Optional[float] = Field(None, ge=0)
    
    # Water and hydration
    water_ml: Optional[float] = Field(None, ge=0)
    alcohol_grams: Optional[float] = Field(None, ge=0)

class DailyNutritionalIntakeResponse(DailyNutritionalIntakeBase):
    id: int
    user_id: str
    profile_id: Optional[int] = None
    
    # Calculated metrics
    protein_percentage: Optional[float] = None
    carbs_percentage: Optional[float] = None
    fat_percentage: Optional[float] = None
    fiber_density: Optional[float] = None
    nutrient_density_score: Optional[float] = None
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Food Composition Schemas
class FoodCompositionBase(BaseModel):
    food_name: str
    scientific_name: Optional[str] = None
    food_group: str
    sub_group: Optional[str] = None
    
    # Basic nutritional information per 100g
    calories: float = Field(0.0, ge=0)
    protein_grams: float = Field(0.0, ge=0)
    carbs_grams: float = Field(0.0, ge=0)
    fat_grams: float = Field(0.0, ge=0)
    fiber_grams: float = Field(0.0, ge=0)
    sugar_grams: float = Field(0.0, ge=0)
    sodium_mg: float = Field(0.0, ge=0)
    
    # Advanced macronutrients
    saturated_fat_grams: Optional[float] = Field(None, ge=0)
    monounsaturated_fat_grams: Optional[float] = Field(None, ge=0)
    polyunsaturated_fat_grams: Optional[float] = Field(None, ge=0)
    trans_fat_grams: Optional[float] = Field(None, ge=0)
    cholesterol_mg: Optional[float] = Field(None, ge=0)
    
    # Food characteristics
    glycemic_index: Optional[float] = Field(None, ge=0, le=100)
    glycemic_load: Optional[float] = Field(None, ge=0)
    glycemic_index_level: Optional[GlycemicIndexLevel] = None
    nutrient_density_score: Optional[float] = Field(None, ge=0, le=100)
    nutrient_density_level: Optional[NutrientDensityLevel] = None
    processing_level: Optional[FoodProcessingLevel] = None
    
    # Food safety and quality
    is_organic: bool = False
    is_gmo_free: bool = True
    is_gluten_free: bool = False
    is_dairy_free: bool = False
    is_nut_free: bool = False
    is_soy_free: bool = False
    
    # Allergen information
    allergens: Optional[List[str]] = None
    cross_contamination_risks: Optional[List[str]] = None
    
    # Storage and preparation
    shelf_life_days: Optional[int] = Field(None, ge=0)
    storage_conditions: Optional[Dict[str, Any]] = None
    preparation_methods: Optional[List[str]] = None
    
    # Source and verification
    data_source: Optional[str] = None
    verification_status: Optional[str] = None

class FoodCompositionCreate(FoodCompositionBase):
    pass

class FoodCompositionUpdate(BaseModel):
    food_name: Optional[str] = None
    scientific_name: Optional[str] = None
    food_group: Optional[str] = None
    sub_group: Optional[str] = None
    
    # Basic nutritional information per 100g
    calories: Optional[float] = Field(None, ge=0)
    protein_grams: Optional[float] = Field(None, ge=0)
    carbs_grams: Optional[float] = Field(None, ge=0)
    fat_grams: Optional[float] = Field(None, ge=0)
    fiber_grams: Optional[float] = Field(None, ge=0)
    sugar_grams: Optional[float] = Field(None, ge=0)
    sodium_mg: Optional[float] = Field(None, ge=0)
    
    # Food characteristics
    glycemic_index: Optional[float] = Field(None, ge=0, le=100)
    glycemic_load: Optional[float] = Field(None, ge=0)
    glycemic_index_level: Optional[GlycemicIndexLevel] = None
    nutrient_density_score: Optional[float] = Field(None, ge=0, le=100)
    nutrient_density_level: Optional[NutrientDensityLevel] = None
    processing_level: Optional[FoodProcessingLevel] = None
    
    # Food safety and quality
    is_organic: Optional[bool] = None
    is_gmo_free: Optional[bool] = None
    is_gluten_free: Optional[bool] = None
    is_dairy_free: Optional[bool] = None
    is_nut_free: Optional[bool] = None
    is_soy_free: Optional[bool] = None
    
    # Allergen information
    allergens: Optional[List[str]] = None
    cross_contamination_risks: Optional[List[str]] = None
    
    # Storage and preparation
    shelf_life_days: Optional[int] = Field(None, ge=0)
    storage_conditions: Optional[Dict[str, Any]] = None
    preparation_methods: Optional[List[str]] = None
    
    # Source and verification
    data_source: Optional[str] = None
    verification_status: Optional[str] = None

class FoodCompositionResponse(FoodCompositionBase):
    id: int
    last_updated: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Nutritional Analysis Schemas
class NutritionalAnalysisBase(BaseModel):
    analysis_date: date
    analysis_type: str  # daily, weekly, monthly, custom
    
    # Basic nutritional analysis
    total_calories: float = Field(..., ge=0)
    calories_from_protein: Optional[float] = Field(None, ge=0)
    calories_from_carbs: Optional[float] = Field(None, ge=0)
    calories_from_fat: Optional[float] = Field(None, ge=0)
    calories_from_alcohol: Optional[float] = Field(None, ge=0)
    
    # Macronutrient ratios
    protein_percentage: Optional[float] = Field(None, ge=0, le=100)
    carbs_percentage: Optional[float] = Field(None, ge=0, le=100)
    fat_percentage: Optional[float] = Field(None, ge=0, le=100)
    alcohol_percentage: Optional[float] = Field(None, ge=0, le=100)
    
    # Nutritional quality scores
    nutrient_density_score: Optional[float] = Field(None, ge=0, le=100)
    fiber_density_score: Optional[float] = Field(None, ge=0, le=100)
    protein_quality_score: Optional[float] = Field(None, ge=0, le=100)
    micronutrient_adequacy_score: Optional[float] = Field(None, ge=0, le=100)
    overall_nutrition_score: Optional[float] = Field(None, ge=0, le=100)
    
    # Deficiency analysis
    nutrient_deficiencies: Optional[List[str]] = None
    excess_nutrients: Optional[List[str]] = None
    recommended_adjustments: Optional[List[str]] = None
    
    # Health impact analysis
    cardiovascular_health_score: Optional[float] = Field(None, ge=0, le=100)
    metabolic_health_score: Optional[float] = Field(None, ge=0, le=100)
    immune_support_score: Optional[float] = Field(None, ge=0, le=100)
    cognitive_health_score: Optional[float] = Field(None, ge=0, le=100)
    bone_health_score: Optional[float] = Field(None, ge=0, le=100)
    
    # Trend analysis
    calorie_trend: Optional[str] = None  # increasing, decreasing, stable
    protein_trend: Optional[str] = None
    micronutrient_trend: Optional[str] = None
    overall_trend: Optional[str] = None
    
    # AI insights and recommendations
    ai_insights: Optional[List[str]] = None
    personalized_recommendations: Optional[List[str]] = None
    risk_factors: Optional[List[str]] = None
    improvement_areas: Optional[List[str]] = None

class NutritionalAnalysisCreate(NutritionalAnalysisBase):
    pass

class NutritionalAnalysisUpdate(BaseModel):
    # Basic nutritional analysis
    total_calories: Optional[float] = Field(None, ge=0)
    calories_from_protein: Optional[float] = Field(None, ge=0)
    calories_from_carbs: Optional[float] = Field(None, ge=0)
    calories_from_fat: Optional[float] = Field(None, ge=0)
    calories_from_alcohol: Optional[float] = Field(None, ge=0)
    
    # Macronutrient ratios
    protein_percentage: Optional[float] = Field(None, ge=0, le=100)
    carbs_percentage: Optional[float] = Field(None, ge=0, le=100)
    fat_percentage: Optional[float] = Field(None, ge=0, le=100)
    alcohol_percentage: Optional[float] = Field(None, ge=0, le=100)
    
    # Nutritional quality scores
    nutrient_density_score: Optional[float] = Field(None, ge=0, le=100)
    fiber_density_score: Optional[float] = Field(None, ge=0, le=100)
    protein_quality_score: Optional[float] = Field(None, ge=0, le=100)
    micronutrient_adequacy_score: Optional[float] = Field(None, ge=0, le=100)
    overall_nutrition_score: Optional[float] = Field(None, ge=0, le=100)
    
    # Deficiency analysis
    nutrient_deficiencies: Optional[List[str]] = None
    excess_nutrients: Optional[List[str]] = None
    recommended_adjustments: Optional[List[str]] = None
    
    # Health impact analysis
    cardiovascular_health_score: Optional[float] = Field(None, ge=0, le=100)
    metabolic_health_score: Optional[float] = Field(None, ge=0, le=100)
    immune_support_score: Optional[float] = Field(None, ge=0, le=100)
    cognitive_health_score: Optional[float] = Field(None, ge=0, le=100)
    bone_health_score: Optional[float] = Field(None, ge=0, le=100)
    
    # Trend analysis
    calorie_trend: Optional[str] = None
    protein_trend: Optional[str] = None
    micronutrient_trend: Optional[str] = None
    overall_trend: Optional[str] = None
    
    # AI insights and recommendations
    ai_insights: Optional[List[str]] = None
    personalized_recommendations: Optional[List[str]] = None
    risk_factors: Optional[List[str]] = None
    improvement_areas: Optional[List[str]] = None

class NutritionalAnalysisResponse(NutritionalAnalysisBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Health Metrics Schemas
class HealthMetricsBase(BaseModel):
    measurement_date: date
    metric_type: str  # weight, blood_pressure, blood_sugar, etc.
    metric_value: float = Field(..., ge=0)
    metric_unit: str
    measurement_method: Optional[str] = None
    notes: Optional[str] = None

class HealthMetricsCreate(HealthMetricsBase):
    pass

class HealthMetricsUpdate(BaseModel):
    measurement_date: Optional[date] = None
    metric_type: Optional[str] = None
    metric_value: Optional[float] = Field(None, ge=0)
    metric_unit: Optional[str] = None
    measurement_method: Optional[str] = None
    notes: Optional[str] = None

class HealthMetricsResponse(HealthMetricsBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Nutritional Correlation Schemas
class NutritionalCorrelationBase(BaseModel):
    correlation_date: date
    nutrient_name: str
    health_metric_type: str
    correlation_coefficient: float = Field(..., ge=-1, le=1)
    correlation_strength: str  # weak, moderate, strong
    p_value: Optional[float] = Field(None, ge=0, le=1)
    sample_size: Optional[int] = Field(None, ge=1)
    analysis_period_days: int = Field(..., ge=1)
    start_date: date
    end_date: date

class NutritionalCorrelationCreate(NutritionalCorrelationBase):
    pass

class NutritionalCorrelationResponse(NutritionalCorrelationBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Search and Filter Schemas
class NutritionalProfileSearch(BaseModel):
    profile_name: Optional[str] = None
    is_default: Optional[bool] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

class FoodCompositionSearch(BaseModel):
    food_name: Optional[str] = None
    food_group: Optional[str] = None
    sub_group: Optional[str] = None
    nutrient_density_level: Optional[NutrientDensityLevel] = None
    processing_level: Optional[FoodProcessingLevel] = None
    is_organic: Optional[bool] = None
    is_gluten_free: Optional[bool] = None
    is_dairy_free: Optional[bool] = None
    allergens: Optional[List[str]] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

class NutritionalAnalysisSearch(BaseModel):
    analysis_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_nutrition_score: Optional[float] = Field(None, ge=0, le=100)
    max_nutrition_score: Optional[float] = Field(None, ge=0, le=100)
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

# Dashboard and Analytics Schemas
class NutritionalDashboard(BaseModel):
    user_id: str
    current_profile: Optional[NutritionalProfileResponse] = None
    today_intake: Optional[DailyNutritionalIntakeResponse] = None
    weekly_average: Optional[DailyNutritionalIntakeResponse] = None
    monthly_average: Optional[DailyNutritionalIntakeResponse] = None
    recent_analyses: List[NutritionalAnalysisResponse] = []
    health_metrics: List[HealthMetricsResponse] = []
    correlations: List[NutritionalCorrelationResponse] = []
    recommendations: List[str] = []
    alerts: List[str] = []

class NutritionalInsights(BaseModel):
    user_id: str
    analysis_period: str  # daily, weekly, monthly
    period_start: date
    period_end: date
    
    # Key insights
    key_findings: List[str] = []
    nutrient_gaps: List[str] = []
    excess_nutrients: List[str] = []
    health_impacts: List[str] = []
    recommendations: List[str] = []
    
    # Trends
    calorie_trend: Optional[str] = None
    protein_trend: Optional[str] = None
    micronutrient_trend: Optional[str] = None
    overall_trend: Optional[str] = None
    
    # Scores
    overall_nutrition_score: Optional[float] = None
    nutrient_density_score: Optional[float] = None
    health_impact_score: Optional[float] = None
    
    # Correlations
    significant_correlations: List[NutritionalCorrelationResponse] = []


