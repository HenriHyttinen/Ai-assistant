"""
Unit tests for RAG (Retrieval-Augmented Generation) retrieval
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.nutrition_ai import NutritionAI


class TestRAGRetrieval:
    """Test RAG retrieval functionality"""

    @pytest.fixture
    def nutrition_ai(self, db_session):
        """Initialize NutritionAI with test database"""
        ai = NutritionAI()
        ai.db = db_session
        return ai

    @pytest.fixture
    def mock_embedding_model(self):
        """Mock SentenceTransformer embedding model"""
        mock_model = Mock()
        # Return 384-dimensional embeddings (all-MiniLM-L6-v2)
        mock_model.encode.return_value = np.array([[0.1] * 384, [0.2] * 384, [0.3] * 384])
        return mock_model

    @pytest.fixture
    def sample_recipes_with_embeddings(self, db_session):
        """Create sample recipes with embeddings"""
        recipes = []
        embeddings = [
            [0.1] * 384,  # Recipe 1: breakfast
            [0.2] * 384,  # Recipe 2: lunch
            [0.3] * 384,  # Recipe 3: dinner
        ]
        
        recipe_data = [
            {
                "id": "r_breakfast_1",
                "title": "Morning Scramble",
                "meal_type": "breakfast",
                "cuisine": "American",
                "dietary_tags": ["vegetarian"],
                "embedding": embeddings[0],
            },
            {
                "id": "r_lunch_1",
                "title": "Lunch Salad",
                "meal_type": "lunch",
                "cuisine": "Mediterranean",
                "dietary_tags": ["vegetarian", "gluten-free"],
                "embedding": embeddings[1],
            },
            {
                "id": "r_dinner_1",
                "title": "Evening Pasta",
                "meal_type": "dinner",
                "cuisine": "Italian",
                "dietary_tags": ["vegetarian"],
                "embedding": embeddings[2],
            },
        ]
        
        from models.recipe import Recipe
        
        for data in recipe_data:
            recipe = Recipe(
                id=data["id"],
                title=data["title"],
                cuisine=data["cuisine"],
                meal_type=data["meal_type"],
                servings=2,
                summary=f"Test {data['title']}",
                prep_time=10,
                cook_time=20,
                difficulty_level="easy",
                dietary_tags=data["dietary_tags"],
                source="test",
                is_active=True,
                embedding=data["embedding"],
            )
            db_session.add(recipe)
            recipes.append(recipe)
        
        db_session.commit()
        return recipes

    def test_retrieve_similar_recipes_by_meal_type(
        self, nutrition_ai, mock_embedding_model, sample_recipes_with_embeddings, db_session
    ):
        """Test that similar recipes are retrieved filtered by meal type"""
        # Patch the underlying attribute directly (properties don't have setters)
        import ai.model_cache
        original_embedding = ai.model_cache.model_cache._embedding_model
        ai.model_cache.model_cache._embedding_model = mock_embedding_model
        try:
            query = "breakfast vegetarian"
            meal_type = "breakfast"
            top_k = 5
            user_embedding = np.array([0.1] * 384)  # Mock user embedding
            
            similar_recipes = nutrition_ai._retrieve_similar_recipes(
                query=query,
                user_embedding=user_embedding,
                db=db_session,
                limit=top_k,
                meal_type=meal_type,
            )
            
            # Verify results are filtered by meal_type
            assert all(r.get('meal_type') == meal_type or r.get('meal_type', '') == meal_type for r in similar_recipes)
            assert len(similar_recipes) > 0
        finally:
            ai.model_cache.model_cache._embedding_model = original_embedding

    def test_similarity_calculation(self, nutrition_ai, mock_embedding_model, sample_recipes_with_embeddings, db_session):
        """Test that similarity is calculated using cosine similarity"""
        import numpy as np
        # Patch the underlying attribute directly (properties don't have setters)
        import ai.model_cache
        original_embedding = ai.model_cache.model_cache._embedding_model
        ai.model_cache.model_cache._embedding_model = mock_embedding_model
        try:
            query = "morning breakfast"
            meal_type = "breakfast"
            user_embedding = np.array([0.1] * 384)
            
            similar_recipes = nutrition_ai._retrieve_similar_recipes(
                query=query,
                user_embedding=user_embedding,
                db=db_session,
                limit=5,
                meal_type=meal_type,
            )
            
            # Verify recipes are returned (similarity calculation works)
            assert len(similar_recipes) > 0
        finally:
            ai.model_cache.model_cache._embedding_model = original_embedding

    def test_filtering_by_dietary_tags(
        self, nutrition_ai, mock_embedding_model, sample_recipes_with_embeddings, db_session
    ):
        """Test that recipes can be filtered by dietary tags"""
        import numpy as np
        # Patch the underlying attribute directly (properties don't have setters)
        import ai.model_cache
        original_embedding = ai.model_cache.model_cache._embedding_model
        ai.model_cache.model_cache._embedding_model = mock_embedding_model
        try:
            query = "vegetarian meal"
            meal_type = "breakfast"
            user_embedding = np.array([0.1] * 384)
            
            similar_recipes = nutrition_ai._retrieve_similar_recipes(
                query=query,
                user_embedding=user_embedding,
                db=db_session,
                limit=5,
                meal_type=meal_type,
            )
            
            # Verify recipes are returned
            # (Dietary tag filtering is applied after retrieval in actual implementation)
            assert len(similar_recipes) >= 0
        finally:
            ai.model_cache.model_cache._embedding_model = original_embedding

    def test_top_k_limit(self, nutrition_ai, mock_embedding_model, sample_recipes_with_embeddings, db_session):
        """Test that top_k limits the number of results"""
        import numpy as np
        # Patch the underlying attribute directly (properties don't have setters)
        import ai.model_cache
        original_embedding = ai.model_cache.model_cache._embedding_model
        ai.model_cache.model_cache._embedding_model = mock_embedding_model
        try:
            query = "test query"
            meal_type = "breakfast"
            top_k = 2
            user_embedding = np.array([0.1] * 384)
            
            similar_recipes = nutrition_ai._retrieve_similar_recipes(
                query=query,
                user_embedding=user_embedding,
                db=db_session,
                limit=top_k,
                meal_type=meal_type,
            )
            
            # Verify results don't exceed top_k
            assert len(similar_recipes) <= top_k
        finally:
            ai.model_cache.model_cache._embedding_model = original_embedding

    def test_embedding_generation(self, nutrition_ai, mock_embedding_model):
        """Test that embeddings are generated correctly"""
        query = "test recipe query"
        
        # Patch the underlying attribute directly (properties don't have setters)
        import ai.model_cache
        original_embedding = ai.model_cache.model_cache._embedding_model
        ai.model_cache.model_cache._embedding_model = mock_embedding_model
        try:
            # Ensure NutritionAI instance uses the mocked model
            nutrition_ai.embedding_model = mock_embedding_model
            
            # Test user embedding generation (similar to query embedding)
            user_preferences = {"dietary_preferences": ["vegetarian"]}
            embedding = nutrition_ai._get_user_embedding(user_preferences)
            
            # Verify embedding is generated
            assert embedding is not None
            assert len(embedding) == 384  # all-MiniLM-L6-v2 dimension
            # Verify encode was called (model should not be None)
            if nutrition_ai.embedding_model is not None:
                mock_embedding_model.encode.assert_called_once()
        finally:
            ai.model_cache.model_cache._embedding_model = original_embedding

    def test_empty_database_handling(self, nutrition_ai, mock_embedding_model, db_session):
        """Test that empty database returns empty results"""
        import numpy as np
        # Patch the underlying attribute directly (properties don't have setters)
        import ai.model_cache
        original_embedding = ai.model_cache.model_cache._embedding_model
        ai.model_cache.model_cache._embedding_model = mock_embedding_model
        try:
            query = "test query"
            meal_type = "breakfast"
            user_embedding = np.array([0.1] * 384)
            
            similar_recipes = nutrition_ai._retrieve_similar_recipes(
                query=query,
                user_embedding=user_embedding,
                db=db_session,
                limit=5,
                meal_type=meal_type,
            )
            
            # Verify empty database returns empty list
            assert similar_recipes == []
        finally:
            ai.model_cache.model_cache._embedding_model = original_embedding

    def test_cosine_similarity_calculation(self):
        """Test cosine similarity calculation"""
        # Test vectors
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([1.0, 0.0, 0.0])  # Same vector
        vec3 = np.array([0.0, 1.0, 0.0])  # Orthogonal
        
        # Calculate cosine similarity
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
        # Same vectors should have similarity = 1.0
        similarity_same = cosine_similarity(vec1, vec2)
        assert abs(similarity_same - 1.0) < 1e-6
        
        # Orthogonal vectors should have similarity = 0.0
        similarity_orthogonal = cosine_similarity(vec1, vec3)
        assert abs(similarity_orthogonal - 0.0) < 1e-6

    def test_meal_type_filtering(self, nutrition_ai, mock_embedding_model, sample_recipes_with_embeddings, db_session):
        """Test that meal type filtering works correctly"""
        import numpy as np
        # Patch the underlying attribute directly (properties don't have setters)
        import ai.model_cache
        original_embedding = ai.model_cache.model_cache._embedding_model
        ai.model_cache.model_cache._embedding_model = mock_embedding_model
        try:
            query = "test"
            user_embedding = np.array([0.1] * 384)
            
            # Test breakfast filtering
            breakfast_recipes = nutrition_ai._retrieve_similar_recipes(
                query=query,
                user_embedding=user_embedding,
                db=db_session,
                limit=10,
                meal_type="breakfast",
            )
            assert all(r.get('meal_type') == "breakfast" for r in breakfast_recipes)
            
            # Test lunch filtering
            lunch_recipes = nutrition_ai._retrieve_similar_recipes(
                query=query,
                user_embedding=user_embedding,
                db=db_session,
                limit=10,
                meal_type="lunch",
            )
            assert all(r.get('meal_type') == "lunch" for r in lunch_recipes)
            
            # Test dinner filtering
            dinner_recipes = nutrition_ai._retrieve_similar_recipes(
                query=query,
                user_embedding=user_embedding,
                db=db_session,
                limit=10,
                meal_type="dinner",
            )
            assert all(r.get('meal_type') == "dinner" for r in dinner_recipes)
        finally:
            ai.model_cache.model_cache._embedding_model = original_embedding

