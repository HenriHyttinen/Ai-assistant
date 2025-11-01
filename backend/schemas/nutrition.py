from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from constants.dietary import DIETARY_PREFERENCES, ALLERGIES_INTOLERANCES
from enum import Enum

# Enums for better type safety
class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class PlanType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"

# Base schemas
class NutritionalInfo(BaseModel):
    calories: float = Field(..., description="Calories in kcal")
    protein: float = Field(..., description="Protein in grams")
    carbs: float = Field(..., description="Carbohydrates in grams")
    fats: float = Field(..., description="Fats in grams")
    fiber: Optional[float] = Field(None, description="Fiber in grams")
    sugar: Optional[float] = Field(None, description="Sugar in grams")
    sodium: Optional[float] = Field(None, description="Sodium in mg")
    
    # Micronutrients (bonus feature)
    vitamin_d: Optional[float] = Field(None, description="Vitamin D in IU")
    vitamin_b12: Optional[float] = Field(None, description="Vitamin B12 in mcg")
    iron: Optional[float] = Field(None, description="Iron in mg")
    calcium: Optional[float] = Field(None, description="Calcium in mg")

class IngredientBase(BaseModel):
    id: str
    name: str
    category: str
    unit: str
    quantity: float = Field(..., description="Quantity in grams or ml")
    nutrition: NutritionalInfo

class RecipeIngredientCreate(BaseModel):
    ingredient_id: str
    quantity: float = Field(..., gt=0, description="Quantity in grams or ml")
    unit: str
    notes: Optional[str] = None

class RecipeInstructionCreate(BaseModel):
    step_number: int = Field(..., gt=0)
    step_title: str
    description: str
    ingredients_used: Optional[List[str]] = None
    time_required: Optional[int] = Field(None, ge=0, description="Time in minutes")

class RecipeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    cuisine: str = Field(..., min_length=1, max_length=50)
    meal_type: MealType
    servings: int = Field(..., gt=0)
    summary: Optional[str] = None
    prep_time: int = Field(..., ge=0, description="Prep time in minutes")
    cook_time: int = Field(..., ge=0, description="Cook time in minutes")
    difficulty_level: DifficultyLevel
    dietary_tags: Optional[List[str]] = []
    image_url: Optional[str] = None
    ingredients: List[RecipeIngredientCreate]
    instructions: List[RecipeInstructionCreate]

class RecipeResponse(BaseModel):
    id: str
    title: str
    cuisine: str
    meal_type: str
    servings: int
    summary: Optional[str]
    prep_time: int
    cook_time: int
    difficulty_level: str
    dietary_tags: List[str]
    source: str
    image_url: Optional[str]
    # Calculated nutritional data
    calculated_calories: Optional[float] = 0
    calculated_protein: Optional[float] = 0
    calculated_carbs: Optional[float] = 0
    calculated_fats: Optional[float] = 0
    calculated_fiber: Optional[float] = 0
    calculated_sugar: Optional[float] = 0
    calculated_sodium: Optional[float] = 0
    # Recipe content
    ingredients_list: Optional[List[str]] = []
    instructions_list: Optional[List[str]] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# User Preferences Schemas
class UserNutritionPreferencesCreate(BaseModel):
    dietary_preferences: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    disliked_ingredients: Optional[List[str]] = []
    cuisine_preferences: Optional[List[str]] = []
    daily_calorie_target: Optional[float] = Field(None, gt=0)
    protein_target: Optional[float] = Field(None, ge=0)
    carbs_target: Optional[float] = Field(None, ge=0)
    fats_target: Optional[float] = Field(None, ge=0)
    meals_per_day: int = Field(3, ge=1, le=6)
    snacks_per_day: int = Field(2, ge=0, le=5)  # Number of snacks per day
    preferred_meal_times: Optional[Dict[str, str]] = None
    timezone: str = Field("UTC", description="Timezone in ISO format")

    @field_validator('dietary_preferences')
    @classmethod
    def validate_diets(cls, v: Optional[List[str]]):
        if not v:
            return []
        invalid = [d for d in v if d not in DIETARY_PREFERENCES]
        if invalid:
            raise ValueError(f"Unsupported dietary preferences: {invalid}. Allowed: {DIETARY_PREFERENCES}")
        return v

    @field_validator('allergies')
    @classmethod
    def validate_allergies(cls, v: Optional[List[str]]):
        if not v:
            return []
        invalid = [a for a in v if a not in ALLERGIES_INTOLERANCES]
        if invalid:
            raise ValueError(f"Unsupported allergies: {invalid}. Allowed: {ALLERGIES_INTOLERANCES}")
        return v

    @field_validator('preferred_meal_times')
    @classmethod
    def validate_meal_times(cls, v: Optional[Dict[str, str]]):
        if not v:
            return v
        for k, iso in v.items():
            if not isinstance(iso, str):
                raise ValueError("preferred_meal_times values must be ISO 8601 strings")
            try:
                # Accept Z as UTC
                datetime.fromisoformat(iso.replace('Z', '+00:00'))
            except Exception:
                raise ValueError(f"Invalid ISO 8601 time for '{k}': {iso}")
        return v

class UserNutritionPreferencesUpdate(BaseModel):
    dietary_preferences: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    disliked_ingredients: Optional[List[str]] = None
    cuisine_preferences: Optional[List[str]] = None
    daily_calorie_target: Optional[float] = Field(None, gt=0)
    protein_target: Optional[float] = Field(None, ge=0)
    carbs_target: Optional[float] = Field(None, ge=0)
    fats_target: Optional[float] = Field(None, ge=0)
    meals_per_day: Optional[int] = Field(None, ge=1, le=6)
    snacks_per_day: Optional[int] = Field(None, ge=0, le=5)
    preferred_meal_times: Optional[Dict[str, str]] = None
    timezone: Optional[str] = None

    @field_validator('dietary_preferences')
    @classmethod
    def validate_diets_update(cls, v: Optional[List[str]]):
        if v is None:
            return v
        invalid = [d for d in v if d not in DIETARY_PREFERENCES]
        if invalid:
            raise ValueError(f"Unsupported dietary preferences: {invalid}. Allowed: {DIETARY_PREFERENCES}")
        return v

    @field_validator('allergies')
    @classmethod
    def validate_allergies_update(cls, v: Optional[List[str]]):
        if v is None:
            return v
        invalid = [a for a in v if a not in ALLERGIES_INTOLERANCES]
        if invalid:
            raise ValueError(f"Unsupported allergies: {invalid}. Allowed: {ALLERGIES_INTOLERANCES}")
        return v

    @field_validator('preferred_meal_times')
    @classmethod
    def validate_meal_times_update(cls, v: Optional[Dict[str, str]]):
        if v is None:
            return v
        for k, iso in v.items():
            if not isinstance(iso, str):
                raise ValueError("preferred_meal_times values must be ISO 8601 strings")
            try:
                datetime.fromisoformat(iso.replace('Z', '+00:00'))
            except Exception:
                raise ValueError(f"Invalid ISO 8601 time for '{k}': {iso}")
        return v

class UserNutritionPreferencesResponse(BaseModel):
    id: int
    user_id: int
    dietary_preferences: List[str]
    allergies: List[str]
    disliked_ingredients: List[str]
    cuisine_preferences: List[str]
    daily_calorie_target: Optional[float]
    protein_target: Optional[float]
    carbs_target: Optional[float]
    fats_target: Optional[float]
    meals_per_day: int
    snacks_per_day: int
    preferred_meal_times: Dict[str, str]
    timezone: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Meal Plan Schemas
class MealPlanRequest(BaseModel):
    plan_type: PlanType
    start_date: date
    end_date: Optional[date] = None
    preferences: Optional[UserNutritionPreferencesCreate] = None

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, info):
        start = info.data.get('start_date')
        if v is not None and start is not None and v < start:
            raise ValueError('end_date must be on or after start_date')
        return v

class MealPlanMealCreate(BaseModel):
    meal_date: date
    meal_type: MealType
    meal_time: Optional[datetime] = None
    meal_name: str
    recipes: List[Dict[str, Any]]  # Recipe IDs and servings

    @field_validator('meal_time', mode='before')
    @classmethod
    def parse_meal_time(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            try:
                dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                return dt
            except Exception:
                raise ValueError('meal_time must be ISO 8601')
        return v

class MealPlanMealResponse(BaseModel):
    id: int
    meal_plan_id: str
    meal_date: date
    meal_type: MealType
    meal_time: Optional[datetime] = None
    meal_name: str
    recipes: List[Dict[str, Any]]  # Recipe details with servings
    total_calories: Optional[float] = None
    total_protein: Optional[float] = None
    total_carbs: Optional[float] = None
    total_fat: Optional[float] = None
    total_fiber: Optional[float] = None
    total_sodium: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MealPlanCreate(BaseModel):
    plan_type: PlanType
    start_date: date
    end_date: Optional[date] = None
    meals: List[MealPlanMealCreate]

class MealPlanResponse(BaseModel):
    id: str
    user_id: int
    plan_type: PlanType
    start_date: date
    end_date: Optional[date]
    version: str
    is_active: bool
    meals: List[Dict[str, Any]]
    total_nutrition: NutritionalInfo
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Nutritional Log Schemas
class NutritionalLogCreate(BaseModel):
    log_date: date
    meal_type: MealType
    calories: float = Field(..., ge=0)
    protein: float = Field(..., ge=0)
    carbs: float = Field(..., ge=0)
    fats: float = Field(..., ge=0)
    fiber: Optional[float] = Field(None, ge=0)
    sugar: Optional[float] = Field(None, ge=0)
    sodium: Optional[float] = Field(None, ge=0)
    vitamin_d: Optional[float] = Field(None, ge=0)
    vitamin_b12: Optional[float] = Field(None, ge=0)
    iron: Optional[float] = Field(None, ge=0)
    calcium: Optional[float] = Field(None, ge=0)

class NutritionalLogResponse(BaseModel):
    id: int
    user_id: int
    log_date: date
    meal_type: MealType
    calories: float
    protein: float
    carbs: float
    fats: float
    fiber: Optional[float]
    sugar: Optional[float]
    sodium: Optional[float]
    vitamin_d: Optional[float]
    vitamin_b12: Optional[float]
    iron: Optional[float]
    calcium: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

# Shopping List Schemas
class ShoppingListItemCreate(BaseModel):
    ingredient_id: str
    quantity: float = Field(..., gt=0)
    unit: str
    notes: Optional[str] = None

class ShoppingListCreate(BaseModel):
    list_name: str = Field(..., min_length=1, max_length=100)
    meal_plan_id: Optional[str] = None
    items: List[ShoppingListItemCreate]

class ShoppingListResponse(BaseModel):
    id: str
    user_id: int
    list_name: str
    meal_plan_id: Optional[str]
    is_active: bool
    items: List[Dict[str, Any]]
    total_items: int = Field(..., description="Total number of items in the list")
    purchased_items: int = Field(..., description="Number of purchased items")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# AI Generation Schemas
class MealPlanGenerationRequest(BaseModel):
    plan_type: PlanType
    start_date: date
    end_date: Optional[date] = None
    preferences_override: Optional[Dict[str, Any]] = None
    generation_strategy: Optional[str] = "balanced"  # balanced, high_protein, low_carb, etc.

class MicronutrientFilter(BaseModel):
    nutrients: List[str] = []
    min_values: Dict[str, float] = {}
    max_values: Dict[str, float] = {}
    categories: List[str] = []

class UserPreferences(BaseModel):
    dietary_preferences: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    disliked_ingredients: Optional[List[str]] = []

class RecipeSearchRequest(BaseModel):
    query: Optional[str] = None
    cuisine: Optional[str] = None
    meal_type: Optional[MealType] = None
    dietary_tags: Optional[List[str]] = []
    max_calories: Optional[float] = None
    min_protein: Optional[float] = None
    max_prep_time: Optional[int] = None
    difficulty_level: Optional[DifficultyLevel] = None
    # Micronutrient filters
    min_vitamin_d: Optional[float] = None
    min_vitamin_c: Optional[float] = None
    min_iron: Optional[float] = None
    min_calcium: Optional[float] = None
    min_magnesium: Optional[float] = None
    min_zinc: Optional[float] = None
    micronutrient_filters: Optional[MicronutrientFilter] = None
    # User preferences for automatic filtering
    user_preferences: Optional[UserPreferences] = None
    # Sorting and pagination
    sort_by: Optional[str] = Field(None, description="Sort by: title, calories, protein, prep_time, difficulty, id")
    sort_order: Optional[str] = Field("asc", description="Sort order: asc or desc")
    limit: int = Field(20, ge=1, le=500)
    page: int = Field(1, ge=1, description="Page number for pagination")

class NutritionalAnalysisRequest(BaseModel):
    start_date: date
    end_date: date
    include_micronutrients: bool = False
    analysis_type: str = Field("daily", description="daily, weekly, or monthly")
