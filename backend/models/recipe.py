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
    
    # Relationships
    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    instructions = relationship("RecipeInstruction", back_populates="recipe", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlanRecipe", back_populates="recipe")

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
    
    # Micronutrients (bonus feature)
    vitamin_d = Column(Float, nullable=True)
    vitamin_b12 = Column(Float, nullable=True)
    iron = Column(Float, nullable=True)
    calcium = Column(Float, nullable=True)
    
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
