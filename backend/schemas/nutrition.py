from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
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
    meal_type: MealType
    servings: int
    summary: Optional[str]
    prep_time: int
    cook_time: int
    total_time: int
    difficulty_level: str
    dietary_tags: List[str]
    source: str
    image_url: Optional[str]
    ingredients: List[Dict[str, Any]]
    instructions: List[Dict[str, Any]]
    nutrition: NutritionalInfo
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
    preferred_meal_times: Optional[Dict[str, str]] = None
    timezone: str = Field("UTC", description="Timezone in ISO format")

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
    preferred_meal_times: Optional[Dict[str, str]] = None
    timezone: Optional[str] = None

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

class MealPlanMealCreate(BaseModel):
    meal_date: date
    meal_type: MealType
    meal_time: Optional[datetime] = None
    meal_name: str
    recipes: List[Dict[str, Any]]  # Recipe IDs and servings

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
    total_items: int
    purchased_items: int
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

class RecipeSearchRequest(BaseModel):
    query: Optional[str] = None
    cuisine: Optional[str] = None
    meal_type: Optional[MealType] = None
    dietary_tags: Optional[List[str]] = []
    max_calories: Optional[float] = None
    min_protein: Optional[float] = None
    max_prep_time: Optional[int] = None
    difficulty_level: Optional[DifficultyLevel] = None
    limit: int = Field(20, ge=1, le=100)

class NutritionalAnalysisRequest(BaseModel):
    start_date: date
    end_date: date
    include_micronutrients: bool = False
    analysis_type: str = Field("daily", description="daily, weekly, or monthly")
