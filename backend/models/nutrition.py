from sqlalchemy import Column, Integer, String, Float, JSON, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base, TimestampMixin

class UserNutritionPreferences(Base, TimestampMixin):
    __tablename__ = "user_nutrition_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Dietary preferences and restrictions
    dietary_preferences = Column(JSON, nullable=True)  # ["vegetarian", "keto", "paleo", etc.]
    allergies = Column(JSON, nullable=True)  # ["nuts", "dairy", "gluten", etc.]
    disliked_ingredients = Column(JSON, nullable=True)  # ["mushrooms", "tofu", etc.]
    cuisine_preferences = Column(JSON, nullable=True)  # ["Italian", "Mexican", "Asian", etc.]
    
    # Nutritional targets
    daily_calorie_target = Column(Float, nullable=True)
    protein_target = Column(Float, nullable=True)  # in grams
    carbs_target = Column(Float, nullable=True)  # in grams
    fats_target = Column(Float, nullable=True)  # in grams
    
    # Meal preferences
    meals_per_day = Column(Integer, nullable=False, default=3)
    preferred_meal_times = Column(JSON, nullable=True)  # {"breakfast": "08:00", "lunch": "12:30", "dinner": "19:00"}
    timezone = Column(String, nullable=False, default="UTC")
    
    # Relationships
    user = relationship("User", back_populates="nutrition_preferences")

class MealPlan(Base, TimestampMixin):
    __tablename__ = "meal_plans"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_type = Column(String, nullable=False)  # "daily" or "weekly"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)  # For weekly plans
    version = Column(String, nullable=False, default="1.0")
    is_active = Column(Boolean, default=True)
    
    # AI generation metadata
    generation_strategy = Column(JSON, nullable=True)  # Strategy used for generation
    ai_model_used = Column(String, nullable=True)
    generation_parameters = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="meal_plans")
    meals = relationship("MealPlanMeal", back_populates="meal_plan", cascade="all, delete-orphan")
    recipes = relationship("MealPlanRecipe", back_populates="meal_plan", cascade="all, delete-orphan")

class MealPlanMeal(Base):
    __tablename__ = "meal_plan_meals"

    id = Column(Integer, primary_key=True, index=True)
    meal_plan_id = Column(String, ForeignKey("meal_plans.id"), nullable=False)
    meal_date = Column(Date, nullable=False)
    meal_type = Column(String, nullable=False)  # breakfast, lunch, dinner, snack
    meal_time = Column(DateTime, nullable=True)  # ISO 8601 format
    meal_name = Column(String, nullable=False)
    
    # Nutritional information for the meal
    calories = Column(Float, nullable=False, default=0.0)
    protein = Column(Float, nullable=False, default=0.0)
    carbs = Column(Float, nullable=False, default=0.0)
    fats = Column(Float, nullable=False, default=0.0)
    
    # Relationships
    meal_plan = relationship("MealPlan", back_populates="meals")
    recipes = relationship("MealPlanRecipe", back_populates="meal", cascade="all, delete-orphan")

class MealPlanRecipe(Base):
    __tablename__ = "meal_plan_recipes"

    id = Column(Integer, primary_key=True, index=True)
    meal_plan_id = Column(String, ForeignKey("meal_plans.id"), nullable=False)
    meal_id = Column(Integer, ForeignKey("meal_plan_meals.id"), nullable=False)
    recipe_id = Column(String, ForeignKey("recipes.id"), nullable=False)
    servings = Column(Float, nullable=False, default=1.0)
    is_alternative = Column(Boolean, default=False)  # For alternative meal options
    
    # Relationships
    meal_plan = relationship("MealPlan", back_populates="recipes")
    meal = relationship("MealPlanMeal", back_populates="recipes")
    recipe = relationship("Recipe", back_populates="meal_plans")

class NutritionalLog(Base, TimestampMixin):
    __tablename__ = "nutritional_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    log_date = Column(Date, nullable=False, index=True)
    meal_type = Column(String, nullable=False)  # breakfast, lunch, dinner, snack
    
    # Nutritional values consumed
    calories = Column(Float, nullable=False, default=0.0)
    protein = Column(Float, nullable=False, default=0.0)
    carbs = Column(Float, nullable=False, default=0.0)
    fats = Column(Float, nullable=False, default=0.0)
    fiber = Column(Float, nullable=False, default=0.0)
    sugar = Column(Float, nullable=False, default=0.0)
    sodium = Column(Float, nullable=False, default=0.0)
    
    # Micronutrients (bonus feature)
    vitamin_d = Column(Float, nullable=True)
    vitamin_b12 = Column(Float, nullable=True)
    iron = Column(Float, nullable=True)
    calcium = Column(Float, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="nutritional_logs")

class ShoppingList(Base, TimestampMixin):
    __tablename__ = "shopping_lists"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    meal_plan_id = Column(String, ForeignKey("meal_plans.id"), nullable=True)
    list_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="shopping_lists")
    meal_plan = relationship("MealPlan")
    items = relationship("ShoppingListItem", back_populates="shopping_list", cascade="all, delete-orphan")

class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"

    id = Column(Integer, primary_key=True, index=True)
    shopping_list_id = Column(String, ForeignKey("shopping_lists.id"), nullable=False)
    ingredient_id = Column(String, ForeignKey("ingredients.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    category = Column(String, nullable=False)  # dairy, protein, vegetables, etc.
    is_purchased = Column(Boolean, default=False)
    notes = Column(String, nullable=True)
    
    # Relationships
    shopping_list = relationship("ShoppingList", back_populates="items")
    ingredient = relationship("Ingredient")
