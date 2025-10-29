from sqlalchemy import Column, Integer, String, Float, Text, JSON, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base, TimestampMixin

class Recipe(Base, TimestampMixin):
    __tablename__ = "recipes"

    id = Column(String, primary_key=True, index=True)  # Custom ID for better control
    title = Column(String, nullable=False, index=True)
    cuisine = Column(String, nullable=False, index=True)
    meal_type = Column(String, nullable=False, index=True)  # breakfast, lunch, dinner, snack
    servings = Column(Integer, nullable=False, default=1)
    summary = Column(Text, nullable=True)
    prep_time = Column(Integer, nullable=False)  # in minutes
    cook_time = Column(Integer, nullable=False)  # in minutes
    difficulty_level = Column(String, nullable=False)  # easy, medium, hard
    dietary_tags = Column(JSON, nullable=True)  # ["vegetarian", "gluten-free", etc.]
    source = Column(String, nullable=False, default="user-generated")
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Vector embedding for RAG (stored as JSON array)
    embedding = Column(JSON, nullable=True)
    
    # Per-serving nutrition (for daily logging)
    per_serving_calories = Column(Float, nullable=True)
    per_serving_protein = Column(Float, nullable=True)
    per_serving_carbs = Column(Float, nullable=True)
    per_serving_fat = Column(Float, nullable=True)
    per_serving_sodium = Column(Float, nullable=True)
    
    # Total recipe nutrition (for full recipe display)
    total_calories = Column(Float, nullable=True)
    total_protein = Column(Float, nullable=True)
    total_carbs = Column(Float, nullable=True)
    total_fat = Column(Float, nullable=True)
    total_sodium = Column(Float, nullable=True)
    
    # Micronutrients (per serving)
    per_serving_vitamin_d = Column(Float, nullable=True)  # mcg
    per_serving_vitamin_b12 = Column(Float, nullable=True)  # mcg
    per_serving_iron = Column(Float, nullable=True)  # mg
    per_serving_calcium = Column(Float, nullable=True)  # mg
    per_serving_magnesium = Column(Float, nullable=True)  # mg
    per_serving_vitamin_c = Column(Float, nullable=True)  # mg
    per_serving_folate = Column(Float, nullable=True)  # mcg
    per_serving_zinc = Column(Float, nullable=True)  # mg
    per_serving_potassium = Column(Float, nullable=True)  # mg
    per_serving_fiber = Column(Float, nullable=True)  # g
    
    # Total micronutrients (for full recipe display)
    total_vitamin_d = Column(Float, nullable=True)
    total_vitamin_b12 = Column(Float, nullable=True)
    total_iron = Column(Float, nullable=True)
    total_calcium = Column(Float, nullable=True)
    total_magnesium = Column(Float, nullable=True)
    total_vitamin_c = Column(Float, nullable=True)
    total_folate = Column(Float, nullable=True)
    total_zinc = Column(Float, nullable=True)
    total_potassium = Column(Float, nullable=True)
    total_fiber = Column(Float, nullable=True)
    
    # Relationships
    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    instructions = relationship("RecipeInstruction", back_populates="recipe", cascade="all, delete-orphan")
    # meal_plans = relationship("MealPlanRecipe", back_populates="recipe")

class Ingredient(Base, TimestampMixin):
    __tablename__ = "ingredients"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)  # dairy, protein, vegetables, etc.
    unit = Column(String, nullable=False)  # gram, ml, piece, etc.
    default_quantity = Column(Float, nullable=False, default=100.0)
    
    # Nutritional information per 100g/ml
    calories = Column(Float, nullable=False, default=0.0)
    protein = Column(Float, nullable=False, default=0.0)
    carbs = Column(Float, nullable=False, default=0.0)
    fats = Column(Float, nullable=False, default=0.0)
    fiber = Column(Float, nullable=False, default=0.0)
    sugar = Column(Float, nullable=False, default=0.0)
    sodium = Column(Float, nullable=False, default=0.0)
    
    # Micronutrients (comprehensive tracking)
    vitamin_d = Column(Float, nullable=True)  # IU
    vitamin_b12 = Column(Float, nullable=True)  # mcg
    iron = Column(Float, nullable=True)  # mg
    calcium = Column(Float, nullable=True)  # mg
    vitamin_c = Column(Float, nullable=True)  # mg
    vitamin_a = Column(Float, nullable=True)  # IU
    vitamin_e = Column(Float, nullable=True)  # mg
    vitamin_k = Column(Float, nullable=True)  # mcg
    thiamine = Column(Float, nullable=True)  # mg (B1)
    riboflavin = Column(Float, nullable=True)  # mg (B2)
    niacin = Column(Float, nullable=True)  # mg (B3)
    folate = Column(Float, nullable=True)  # mcg (B9)
    magnesium = Column(Float, nullable=True)  # mg
    zinc = Column(Float, nullable=True)  # mg
    selenium = Column(Float, nullable=True)  # mcg
    potassium = Column(Float, nullable=True)  # mg
    phosphorus = Column(Float, nullable=True)  # mg
    omega_3 = Column(Float, nullable=True)  # g
    omega_6 = Column(Float, nullable=True)  # g
    
    # Vector embedding for RAG
    embedding = Column(JSON, nullable=True)
    
    # Relationships
    recipe_ingredients = relationship("RecipeIngredient", back_populates="ingredient")

class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(String, ForeignKey("recipes.id"), nullable=False)
    ingredient_id = Column(String, ForeignKey("ingredients.id"), nullable=False)
    quantity = Column(Float, nullable=False)  # in grams or ml
    unit = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    
    # Relationships
    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="recipe_ingredients")

class RecipeInstruction(Base):
    __tablename__ = "recipe_instructions"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(String, ForeignKey("recipes.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    step_title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    ingredients_used = Column(JSON, nullable=True)  # List of ingredient IDs used in this step
    time_required = Column(Integer, nullable=True)  # in minutes
    
    # Relationships
    recipe = relationship("Recipe", back_populates="instructions")
