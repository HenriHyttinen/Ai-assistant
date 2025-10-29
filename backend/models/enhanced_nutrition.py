from sqlalchemy import Column, Integer, String, Float, Text, JSON, Boolean, DateTime, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base, TimestampMixin
import enum

class NutrientDensityLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class GlycemicIndexLevel(str, enum.Enum):
    LOW = "low"  # 0-55
    MEDIUM = "medium"  # 56-69
    HIGH = "high"  # 70+

class FoodProcessingLevel(str, enum.Enum):
    UNPROCESSED = "unprocessed"
    MINIMALLY_PROCESSED = "minimally_processed"
    PROCESSED = "processed"
    ULTRA_PROCESSED = "ultra_processed"

class NutritionalProfile(Base, TimestampMixin):
    """Enhanced nutritional profile for comprehensive analysis"""
    __tablename__ = "nutritional_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    profile_name = Column(String, nullable=False)
    is_default = Column(Boolean, default=False)
    
    # Basic nutritional targets
    daily_calories = Column(Float, nullable=False)
    protein_grams = Column(Float, nullable=False)
    carbs_grams = Column(Float, nullable=False)
    fat_grams = Column(Float, nullable=False)
    fiber_grams = Column(Float, nullable=False)
    sugar_grams = Column(Float, nullable=False)
    sodium_mg = Column(Float, nullable=False)
    
    # Advanced macronutrient targets
    saturated_fat_grams = Column(Float, nullable=True)
    monounsaturated_fat_grams = Column(Float, nullable=True)
    polyunsaturated_fat_grams = Column(Float, nullable=True)
    trans_fat_grams = Column(Float, nullable=True)
    cholesterol_mg = Column(Float, nullable=True)
    
    # Carbohydrate breakdown
    total_carbs_grams = Column(Float, nullable=True)
    net_carbs_grams = Column(Float, nullable=True)  # Total carbs - fiber
    simple_carbs_grams = Column(Float, nullable=True)
    complex_carbs_grams = Column(Float, nullable=True)
    starch_grams = Column(Float, nullable=True)
    
    # Micronutrient targets (comprehensive)
    vitamin_a_mcg = Column(Float, nullable=True)  # RAE (Retinol Activity Equivalents)
    vitamin_c_mg = Column(Float, nullable=True)
    vitamin_d_mcg = Column(Float, nullable=True)
    vitamin_e_mg = Column(Float, nullable=True)
    vitamin_k_mcg = Column(Float, nullable=True)
    thiamine_mg = Column(Float, nullable=True)  # B1
    riboflavin_mg = Column(Float, nullable=True)  # B2
    niacin_mg = Column(Float, nullable=True)  # B3
    pantothenic_acid_mg = Column(Float, nullable=True)  # B5
    pyridoxine_mg = Column(Float, nullable=True)  # B6
    biotin_mcg = Column(Float, nullable=True)  # B7
    folate_mcg = Column(Float, nullable=True)  # B9
    cobalamin_mcg = Column(Float, nullable=True)  # B12
    
    # Minerals
    calcium_mg = Column(Float, nullable=True)
    iron_mg = Column(Float, nullable=True)
    magnesium_mg = Column(Float, nullable=True)
    phosphorus_mg = Column(Float, nullable=True)
    potassium_mg = Column(Float, nullable=True)
    sodium_mg = Column(Float, nullable=True)
    zinc_mg = Column(Float, nullable=True)
    copper_mg = Column(Float, nullable=True)
    manganese_mg = Column(Float, nullable=True)
    selenium_mcg = Column(Float, nullable=True)
    iodine_mcg = Column(Float, nullable=True)
    fluoride_mg = Column(Float, nullable=True)
    
    # Trace minerals
    chromium_mcg = Column(Float, nullable=True)
    molybdenum_mcg = Column(Float, nullable=True)
    boron_mg = Column(Float, nullable=True)
    silicon_mg = Column(Float, nullable=True)
    vanadium_mcg = Column(Float, nullable=True)
    
    # Fatty acids
    omega_3_grams = Column(Float, nullable=True)
    omega_6_grams = Column(Float, nullable=True)
    omega_9_grams = Column(Float, nullable=True)
    dha_grams = Column(Float, nullable=True)  # Docosahexaenoic acid
    epa_grams = Column(Float, nullable=True)  # Eicosapentaenoic acid
    ala_grams = Column(Float, nullable=True)  # Alpha-linolenic acid
    la_grams = Column(Float, nullable=True)  # Linoleic acid
    
    # Amino acids (essential)
    histidine_grams = Column(Float, nullable=True)
    isoleucine_grams = Column(Float, nullable=True)
    leucine_grams = Column(Float, nullable=True)
    lysine_grams = Column(Float, nullable=True)
    methionine_grams = Column(Float, nullable=True)
    phenylalanine_grams = Column(Float, nullable=True)
    threonine_grams = Column(Float, nullable=True)
    tryptophan_grams = Column(Float, nullable=True)
    valine_grams = Column(Float, nullable=True)
    
    # Non-essential amino acids
    alanine_grams = Column(Float, nullable=True)
    arginine_grams = Column(Float, nullable=True)
    asparagine_grams = Column(Float, nullable=True)
    aspartic_acid_grams = Column(Float, nullable=True)
    cysteine_grams = Column(Float, nullable=True)
    glutamic_acid_grams = Column(Float, nullable=True)
    glutamine_grams = Column(Float, nullable=True)
    glycine_grams = Column(Float, nullable=True)
    proline_grams = Column(Float, nullable=True)
    serine_grams = Column(Float, nullable=True)
    tyrosine_grams = Column(Float, nullable=True)
    
    # Phytochemicals and antioxidants
    beta_carotene_mcg = Column(Float, nullable=True)
    lycopene_mcg = Column(Float, nullable=True)
    lutein_mcg = Column(Float, nullable=True)
    zeaxanthin_mcg = Column(Float, nullable=True)
    anthocyanins_mg = Column(Float, nullable=True)
    flavonoids_mg = Column(Float, nullable=True)
    polyphenols_mg = Column(Float, nullable=True)
    resveratrol_mg = Column(Float, nullable=True)
    quercetin_mg = Column(Float, nullable=True)
    catechins_mg = Column(Float, nullable=True)
    
    # Other bioactive compounds
    caffeine_mg = Column(Float, nullable=True)
    theobromine_mg = Column(Float, nullable=True)
    theophylline_mg = Column(Float, nullable=True)
    capsaicin_mg = Column(Float, nullable=True)
    curcumin_mg = Column(Float, nullable=True)
    gingerol_mg = Column(Float, nullable=True)
    allicin_mg = Column(Float, nullable=True)
    
    # Water and hydration
    water_ml = Column(Float, nullable=True)
    alcohol_grams = Column(Float, nullable=True)
    
    # Relationships
    user = relationship("User")
    daily_intakes = relationship("DailyNutritionalIntake", back_populates="profile")

class DailyNutritionalIntake(Base, TimestampMixin):
    """Daily nutritional intake tracking with comprehensive data"""
    __tablename__ = "daily_nutritional_intakes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    profile_id = Column(Integer, ForeignKey("nutritional_profiles.id"), nullable=True)
    intake_date = Column(Date, nullable=False, index=True)
    
    # Basic macronutrients
    calories_consumed = Column(Float, nullable=False, default=0.0)
    protein_grams = Column(Float, nullable=False, default=0.0)
    carbs_grams = Column(Float, nullable=False, default=0.0)
    fat_grams = Column(Float, nullable=False, default=0.0)
    fiber_grams = Column(Float, nullable=False, default=0.0)
    sugar_grams = Column(Float, nullable=False, default=0.0)
    sodium_mg = Column(Float, nullable=False, default=0.0)
    
    # Advanced macronutrients
    saturated_fat_grams = Column(Float, nullable=True, default=0.0)
    monounsaturated_fat_grams = Column(Float, nullable=True, default=0.0)
    polyunsaturated_fat_grams = Column(Float, nullable=True, default=0.0)
    trans_fat_grams = Column(Float, nullable=True, default=0.0)
    cholesterol_mg = Column(Float, nullable=True, default=0.0)
    
    # Carbohydrate breakdown
    total_carbs_grams = Column(Float, nullable=True, default=0.0)
    net_carbs_grams = Column(Float, nullable=True, default=0.0)
    simple_carbs_grams = Column(Float, nullable=True, default=0.0)
    complex_carbs_grams = Column(Float, nullable=True, default=0.0)
    starch_grams = Column(Float, nullable=True, default=0.0)
    
    # Micronutrients (comprehensive)
    vitamin_a_mcg = Column(Float, nullable=True, default=0.0)
    vitamin_c_mg = Column(Float, nullable=True, default=0.0)
    vitamin_d_mcg = Column(Float, nullable=True, default=0.0)
    vitamin_e_mg = Column(Float, nullable=True, default=0.0)
    vitamin_k_mcg = Column(Float, nullable=True, default=0.0)
    thiamine_mg = Column(Float, nullable=True, default=0.0)
    riboflavin_mg = Column(Float, nullable=True, default=0.0)
    niacin_mg = Column(Float, nullable=True, default=0.0)
    pantothenic_acid_mg = Column(Float, nullable=True, default=0.0)
    pyridoxine_mg = Column(Float, nullable=True, default=0.0)
    biotin_mcg = Column(Float, nullable=True, default=0.0)
    folate_mcg = Column(Float, nullable=True, default=0.0)
    cobalamin_mcg = Column(Float, nullable=True, default=0.0)
    
    # Minerals
    calcium_mg = Column(Float, nullable=True, default=0.0)
    iron_mg = Column(Float, nullable=True, default=0.0)
    magnesium_mg = Column(Float, nullable=True, default=0.0)
    phosphorus_mg = Column(Float, nullable=True, default=0.0)
    potassium_mg = Column(Float, nullable=True, default=0.0)
    zinc_mg = Column(Float, nullable=True, default=0.0)
    copper_mg = Column(Float, nullable=True, default=0.0)
    manganese_mg = Column(Float, nullable=True, default=0.0)
    selenium_mcg = Column(Float, nullable=True, default=0.0)
    iodine_mcg = Column(Float, nullable=True, default=0.0)
    fluoride_mg = Column(Float, nullable=True, default=0.0)
    
    # Trace minerals
    chromium_mcg = Column(Float, nullable=True, default=0.0)
    molybdenum_mcg = Column(Float, nullable=True, default=0.0)
    boron_mg = Column(Float, nullable=True, default=0.0)
    silicon_mg = Column(Float, nullable=True, default=0.0)
    vanadium_mcg = Column(Float, nullable=True, default=0.0)
    
    # Fatty acids
    omega_3_grams = Column(Float, nullable=True, default=0.0)
    omega_6_grams = Column(Float, nullable=True, default=0.0)
    omega_9_grams = Column(Float, nullable=True, default=0.0)
    dha_grams = Column(Float, nullable=True, default=0.0)
    epa_grams = Column(Float, nullable=True, default=0.0)
    ala_grams = Column(Float, nullable=True, default=0.0)
    la_grams = Column(Float, nullable=True, default=0.0)
    
    # Amino acids (essential)
    histidine_grams = Column(Float, nullable=True, default=0.0)
    isoleucine_grams = Column(Float, nullable=True, default=0.0)
    leucine_grams = Column(Float, nullable=True, default=0.0)
    lysine_grams = Column(Float, nullable=True, default=0.0)
    methionine_grams = Column(Float, nullable=True, default=0.0)
    phenylalanine_grams = Column(Float, nullable=True, default=0.0)
    threonine_grams = Column(Float, nullable=True, default=0.0)
    tryptophan_grams = Column(Float, nullable=True, default=0.0)
    valine_grams = Column(Float, nullable=True, default=0.0)
    
    # Phytochemicals and antioxidants
    beta_carotene_mcg = Column(Float, nullable=True, default=0.0)
    lycopene_mcg = Column(Float, nullable=True, default=0.0)
    lutein_mcg = Column(Float, nullable=True, default=0.0)
    zeaxanthin_mcg = Column(Float, nullable=True, default=0.0)
    anthocyanins_mg = Column(Float, nullable=True, default=0.0)
    flavonoids_mg = Column(Float, nullable=True, default=0.0)
    polyphenols_mg = Column(Float, nullable=True, default=0.0)
    resveratrol_mg = Column(Float, nullable=True, default=0.0)
    quercetin_mg = Column(Float, nullable=True, default=0.0)
    catechins_mg = Column(Float, nullable=True, default=0.0)
    
    # Other bioactive compounds
    caffeine_mg = Column(Float, nullable=True, default=0.0)
    theobromine_mg = Column(Float, nullable=True, default=0.0)
    theophylline_mg = Column(Float, nullable=True, default=0.0)
    capsaicin_mg = Column(Float, nullable=True, default=0.0)
    curcumin_mg = Column(Float, nullable=True, default=0.0)
    gingerol_mg = Column(Float, nullable=True, default=0.0)
    allicin_mg = Column(Float, nullable=True, default=0.0)
    
    # Water and hydration
    water_ml = Column(Float, nullable=True, default=0.0)
    alcohol_grams = Column(Float, nullable=True, default=0.0)
    
    # Calculated metrics
    protein_percentage = Column(Float, nullable=True)  # % of calories from protein
    carbs_percentage = Column(Float, nullable=True)  # % of calories from carbs
    fat_percentage = Column(Float, nullable=True)  # % of calories from fat
    fiber_density = Column(Float, nullable=True)  # grams per 1000 calories
    nutrient_density_score = Column(Float, nullable=True)  # Overall nutrient density
    
    # Relationships
    user = relationship("User")
    profile = relationship("NutritionalProfile", back_populates="daily_intakes")

class FoodComposition(Base, TimestampMixin):
    """Comprehensive food composition database"""
    __tablename__ = "food_compositions"
    
    id = Column(Integer, primary_key=True, index=True)
    food_name = Column(String, nullable=False, index=True)
    scientific_name = Column(String, nullable=True)
    food_group = Column(String, nullable=False, index=True)
    sub_group = Column(String, nullable=True)
    
    # Basic nutritional information per 100g
    calories = Column(Float, nullable=False, default=0.0)
    protein_grams = Column(Float, nullable=False, default=0.0)
    carbs_grams = Column(Float, nullable=False, default=0.0)
    fat_grams = Column(Float, nullable=False, default=0.0)
    fiber_grams = Column(Float, nullable=False, default=0.0)
    sugar_grams = Column(Float, nullable=False, default=0.0)
    sodium_mg = Column(Float, nullable=False, default=0.0)
    
    # Advanced macronutrients
    saturated_fat_grams = Column(Float, nullable=True)
    monounsaturated_fat_grams = Column(Float, nullable=True)
    polyunsaturated_fat_grams = Column(Float, nullable=True)
    trans_fat_grams = Column(Float, nullable=True)
    cholesterol_mg = Column(Float, nullable=True)
    
    # Carbohydrate breakdown
    total_carbs_grams = Column(Float, nullable=True)
    net_carbs_grams = Column(Float, nullable=True)
    simple_carbs_grams = Column(Float, nullable=True)
    complex_carbs_grams = Column(Float, nullable=True)
    starch_grams = Column(Float, nullable=True)
    
    # Micronutrients (comprehensive)
    vitamin_a_mcg = Column(Float, nullable=True)
    vitamin_c_mg = Column(Float, nullable=True)
    vitamin_d_mcg = Column(Float, nullable=True)
    vitamin_e_mg = Column(Float, nullable=True)
    vitamin_k_mcg = Column(Float, nullable=True)
    thiamine_mg = Column(Float, nullable=True)
    riboflavin_mg = Column(Float, nullable=True)
    niacin_mg = Column(Float, nullable=True)
    pantothenic_acid_mg = Column(Float, nullable=True)
    pyridoxine_mg = Column(Float, nullable=True)
    biotin_mcg = Column(Float, nullable=True)
    folate_mcg = Column(Float, nullable=True)
    cobalamin_mcg = Column(Float, nullable=True)
    
    # Minerals
    calcium_mg = Column(Float, nullable=True)
    iron_mg = Column(Float, nullable=True)
    magnesium_mg = Column(Float, nullable=True)
    phosphorus_mg = Column(Float, nullable=True)
    potassium_mg = Column(Float, nullable=True)
    zinc_mg = Column(Float, nullable=True)
    copper_mg = Column(Float, nullable=True)
    manganese_mg = Column(Float, nullable=True)
    selenium_mcg = Column(Float, nullable=True)
    iodine_mcg = Column(Float, nullable=True)
    fluoride_mg = Column(Float, nullable=True)
    
    # Trace minerals
    chromium_mcg = Column(Float, nullable=True)
    molybdenum_mcg = Column(Float, nullable=True)
    boron_mg = Column(Float, nullable=True)
    silicon_mg = Column(Float, nullable=True)
    vanadium_mcg = Column(Float, nullable=True)
    
    # Fatty acids
    omega_3_grams = Column(Float, nullable=True)
    omega_6_grams = Column(Float, nullable=True)
    omega_9_grams = Column(Float, nullable=True)
    dha_grams = Column(Float, nullable=True)
    epa_grams = Column(Float, nullable=True)
    ala_grams = Column(Float, nullable=True)
    la_grams = Column(Float, nullable=True)
    
    # Amino acids (essential)
    histidine_grams = Column(Float, nullable=True)
    isoleucine_grams = Column(Float, nullable=True)
    leucine_grams = Column(Float, nullable=True)
    lysine_grams = Column(Float, nullable=True)
    methionine_grams = Column(Float, nullable=True)
    phenylalanine_grams = Column(Float, nullable=True)
    threonine_grams = Column(Float, nullable=True)
    tryptophan_grams = Column(Float, nullable=True)
    valine_grams = Column(Float, nullable=True)
    
    # Non-essential amino acids
    alanine_grams = Column(Float, nullable=True)
    arginine_grams = Column(Float, nullable=True)
    asparagine_grams = Column(Float, nullable=True)
    aspartic_acid_grams = Column(Float, nullable=True)
    cysteine_grams = Column(Float, nullable=True)
    glutamic_acid_grams = Column(Float, nullable=True)
    glutamine_grams = Column(Float, nullable=True)
    glycine_grams = Column(Float, nullable=True)
    proline_grams = Column(Float, nullable=True)
    serine_grams = Column(Float, nullable=True)
    tyrosine_grams = Column(Float, nullable=True)
    
    # Phytochemicals and antioxidants
    beta_carotene_mcg = Column(Float, nullable=True)
    lycopene_mcg = Column(Float, nullable=True)
    lutein_mcg = Column(Float, nullable=True)
    zeaxanthin_mcg = Column(Float, nullable=True)
    anthocyanins_mg = Column(Float, nullable=True)
    flavonoids_mg = Column(Float, nullable=True)
    polyphenols_mg = Column(Float, nullable=True)
    resveratrol_mg = Column(Float, nullable=True)
    quercetin_mg = Column(Float, nullable=True)
    catechins_mg = Column(Float, nullable=True)
    
    # Other bioactive compounds
    caffeine_mg = Column(Float, nullable=True)
    theobromine_mg = Column(Float, nullable=True)
    theophylline_mg = Column(Float, nullable=True)
    capsaicin_mg = Column(Float, nullable=True)
    curcumin_mg = Column(Float, nullable=True)
    gingerol_mg = Column(Float, nullable=True)
    allicin_mg = Column(Float, nullable=True)
    
    # Water and hydration
    water_ml = Column(Float, nullable=True)
    alcohol_grams = Column(Float, nullable=True)
    
    # Food characteristics
    glycemic_index = Column(Float, nullable=True)
    glycemic_load = Column(Float, nullable=True)
    glycemic_index_level = Column(Enum(GlycemicIndexLevel), nullable=True)
    nutrient_density_score = Column(Float, nullable=True)
    nutrient_density_level = Column(Enum(NutrientDensityLevel), nullable=True)
    processing_level = Column(Enum(FoodProcessingLevel), nullable=True)
    
    # Food safety and quality
    is_organic = Column(Boolean, default=False)
    is_gmo_free = Column(Boolean, default=True)
    is_gluten_free = Column(Boolean, default=False)
    is_dairy_free = Column(Boolean, default=False)
    is_nut_free = Column(Boolean, default=False)
    is_soy_free = Column(Boolean, default=False)
    
    # Allergen information
    allergens = Column(JSON, nullable=True)  # List of allergens
    cross_contamination_risks = Column(JSON, nullable=True)  # List of cross-contamination risks
    
    # Storage and preparation
    shelf_life_days = Column(Integer, nullable=True)
    storage_conditions = Column(JSON, nullable=True)  # Temperature, humidity, etc.
    preparation_methods = Column(JSON, nullable=True)  # Raw, cooked, etc.
    
    # Source and verification
    data_source = Column(String, nullable=True)  # USDA, FDC, etc.
    last_updated = Column(DateTime, nullable=True)
    verification_status = Column(String, nullable=True)  # verified, pending, unverified
    
    # Relationships - removed incorrect relationship

class NutritionalAnalysis(Base, TimestampMixin):
    """Advanced nutritional analysis and insights"""
    __tablename__ = "nutritional_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    analysis_date = Column(Date, nullable=False, index=True)
    analysis_type = Column(String, nullable=False)  # daily, weekly, monthly, custom
    
    # Basic nutritional analysis
    total_calories = Column(Float, nullable=False)
    calories_from_protein = Column(Float, nullable=True)
    calories_from_carbs = Column(Float, nullable=True)
    calories_from_fat = Column(Float, nullable=True)
    calories_from_alcohol = Column(Float, nullable=True)
    
    # Macronutrient ratios
    protein_percentage = Column(Float, nullable=True)
    carbs_percentage = Column(Float, nullable=True)
    fat_percentage = Column(Float, nullable=True)
    alcohol_percentage = Column(Float, nullable=True)
    
    # Nutritional quality scores
    nutrient_density_score = Column(Float, nullable=True)  # 0-100
    fiber_density_score = Column(Float, nullable=True)  # 0-100
    protein_quality_score = Column(Float, nullable=True)  # 0-100
    micronutrient_adequacy_score = Column(Float, nullable=True)  # 0-100
    overall_nutrition_score = Column(Float, nullable=True)  # 0-100
    
    # Deficiency analysis
    nutrient_deficiencies = Column(JSON, nullable=True)  # List of deficient nutrients
    excess_nutrients = Column(JSON, nullable=True)  # List of excessive nutrients
    recommended_adjustments = Column(JSON, nullable=True)  # AI recommendations
    
    # Health impact analysis
    cardiovascular_health_score = Column(Float, nullable=True)  # 0-100
    metabolic_health_score = Column(Float, nullable=True)  # 0-100
    immune_support_score = Column(Float, nullable=True)  # 0-100
    cognitive_health_score = Column(Float, nullable=True)  # 0-100
    bone_health_score = Column(Float, nullable=True)  # 0-100
    
    # Trend analysis
    calorie_trend = Column(String, nullable=True)  # increasing, decreasing, stable
    protein_trend = Column(String, nullable=True)
    micronutrient_trend = Column(String, nullable=True)
    overall_trend = Column(String, nullable=True)
    
    # AI insights and recommendations
    ai_insights = Column(JSON, nullable=True)  # AI-generated insights
    personalized_recommendations = Column(JSON, nullable=True)  # Personalized recommendations
    risk_factors = Column(JSON, nullable=True)  # Identified risk factors
    improvement_areas = Column(JSON, nullable=True)  # Areas for improvement
    
    # Relationships
    user = relationship("User")

class HealthMetrics(Base, TimestampMixin):
    """Health metrics that can be correlated with nutrition"""
    __tablename__ = "health_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    measurement_date = Column(Date, nullable=False, index=True)
    metric_type = Column(String, nullable=False)  # weight, blood_pressure, blood_sugar, etc.
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String, nullable=False)
    measurement_method = Column(String, nullable=True)  # scale, blood_test, etc.
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User")

class NutritionalCorrelation(Base, TimestampMixin):
    """Correlations between nutrition and health metrics"""
    __tablename__ = "nutritional_correlations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    correlation_date = Column(Date, nullable=False, index=True)
    
    # Correlation data
    nutrient_name = Column(String, nullable=False)
    health_metric_type = Column(String, nullable=False)
    correlation_coefficient = Column(Float, nullable=False)  # -1 to 1
    correlation_strength = Column(String, nullable=False)  # weak, moderate, strong
    p_value = Column(Float, nullable=True)  # Statistical significance
    sample_size = Column(Integer, nullable=True)
    
    # Time period analyzed
    analysis_period_days = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Relationships
    user = relationship("User")
