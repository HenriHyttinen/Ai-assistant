"""
Pytest configuration and fixtures for backend tests
"""
import pytest
import sys
import os
from datetime import date, datetime
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.base import Base
from models.user import User
from models.nutrition import UserNutritionPreferences
from models.recipe import Recipe, Ingredient, RecipeIngredient, RecipeInstruction


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def mock_user():
    """Create a mock user"""
    user = Mock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.username = "testuser"
    return user


@pytest.fixture
def sample_user_preferences():
    """Sample user nutrition preferences"""
    return {
        "dietary_preferences": ["vegetarian"],
        "allergies": ["nuts"],
        "disliked_ingredients": ["mushrooms"],
        "cuisine_preferences": ["Italian", "Mediterranean"],
        "daily_calorie_target": 2000.0,
        "protein_target": 100.0,
        "carbs_target": 250.0,
        "fats_target": 65.0,
        "meals_per_day": 3,
        "snacks_per_day": 2,
    }


@pytest.fixture
def sample_recipe_data():
    """Sample recipe data for testing"""
    return {
        "title": "Test Pasta",
        "cuisine": "Italian",
        "meal_type": "dinner",
        "servings": 2,
        "summary": "A delicious test pasta",
        "prep_time": 10,
        "cook_time": 20,
        "difficulty_level": "easy",
        "dietary_tags": ["vegetarian"],
        "source": "test",
        "ingredients": [
            {"name": "pasta", "quantity": 200, "unit": "g"},
            {"name": "tomato sauce", "quantity": 150, "unit": "ml"},
        ],
        "instructions": [
            {"step_number": 1, "description": "Cook pasta", "time_required": 10},
            {"step_number": 2, "description": "Add sauce", "time_required": 5},
        ],
    }


@pytest.fixture
def sample_ingredient_data():
    """Sample ingredient data for testing"""
    return {
        "name": "chicken breast",
        "category": "protein",
        "unit": "g",
        "default_quantity": 100.0,
        "calories": 165.0,
        "protein": 31.0,
        "carbs": 0.0,
        "fats": 3.6,
        "fiber": 0.0,
        "sugar": 0.0,
        "sodium": 74.0,
    }


@pytest.fixture
def sample_recipe(db_session, sample_recipe_data):
    """Create a sample recipe in the database"""
    recipe = Recipe(
        id="r_test_1",
        title=sample_recipe_data["title"],
        cuisine=sample_recipe_data["cuisine"],
        meal_type=sample_recipe_data["meal_type"],
        servings=sample_recipe_data["servings"],
        summary=sample_recipe_data["summary"],
        prep_time=sample_recipe_data["prep_time"],
        cook_time=sample_recipe_data["cook_time"],
        difficulty_level=sample_recipe_data["difficulty_level"],
        dietary_tags=sample_recipe_data["dietary_tags"],
        source=sample_recipe_data["source"],
        is_active=True,
    )
    db_session.add(recipe)
    db_session.commit()
    return recipe


@pytest.fixture
def sample_ingredient(db_session, sample_ingredient_data):
    """Create a sample ingredient in the database"""
    ingredient = Ingredient(
        id="ing_test_1",
        name=sample_ingredient_data["name"],
        category=sample_ingredient_data["category"],
        unit=sample_ingredient_data["unit"],
        default_quantity=sample_ingredient_data["default_quantity"],
        calories=sample_ingredient_data["calories"],
        protein=sample_ingredient_data["protein"],
        carbs=sample_ingredient_data["carbs"],
        fats=sample_ingredient_data["fats"],
        fiber=sample_ingredient_data["fiber"],
        sugar=sample_ingredient_data["sugar"],
        sodium=sample_ingredient_data["sodium"],
    )
    db_session.add(ingredient)
    db_session.commit()
    return ingredient


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    # Create a Mock object that mimics the OpenAI response structure
    mock_response = Mock()
    mock_message = Mock()
    mock_message.content = '{"title": "Test Recipe", "cuisine": "Italian", "ingredients": [{"name": "pasta", "quantity": 200, "unit": "g"}], "instructions": ["Cook pasta"]}'
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_response.usage = {"total_tokens": 100, "prompt_tokens": 50, "completion_tokens": 50}
    return mock_response


@pytest.fixture
def mock_embedding_model():
    """Mock SentenceTransformer embedding model"""
    mock_model = Mock()
    mock_model.encode.return_value = [[0.1] * 384]  # 384-dimensional embedding
    return mock_model


@pytest.fixture(autouse=True)
def mock_openai_api(mock_openai_response):
    """Auto-mock OpenAI API calls"""
    # Create mock client and embedding model
    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_openai_response
    
    mock_embedding = Mock()
    mock_embedding.encode.return_value = [[0.1] * 384]
    
    # Import model_cache and patch the instance attributes directly
    import ai.model_cache
    original_openai = ai.model_cache.model_cache._openai_client
    original_embedding = ai.model_cache.model_cache._embedding_model
    
    # Replace with mocks
    ai.model_cache.model_cache._openai_client = mock_client
    ai.model_cache.model_cache._embedding_model = mock_embedding
    
    yield mock_client
    
    # Restore originals
    ai.model_cache.model_cache._openai_client = original_openai
    ai.model_cache.model_cache._embedding_model = original_embedding

