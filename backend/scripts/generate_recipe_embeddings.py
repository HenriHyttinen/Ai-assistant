#!/usr/bin/env python3
"""
Generate vector embeddings for all recipes to enable RAG (Retrieval-Augmented Generation) search.
This script will:
1. Load all 500 recipes from the database
2. Generate embeddings for each recipe using sentence transformers
3. Store embeddings in the database for fast similarity search
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Recipe
from sqlalchemy.orm import Session
import logging
import numpy as np
from typing import List, Dict, Any

# Try to import sentence transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("❌ sentence-transformers not available. Install with: pip install sentence-transformers")

# Fallback: Use a simple TF-IDF based embedding
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("❌ scikit-learn not available for fallback embeddings")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RecipeEmbeddingGenerator:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_model = None
        self.vectorizer = None
        self.embedding_dimension = 384  # all-MiniLM-L6-v2 dimension
        self.use_tfidf = False
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("✅ Loaded sentence transformer model: all-MiniLM-L6-v2")
            except Exception as e:
                logger.error(f"❌ Failed to load sentence transformer model: {e}")
                self.embedding_model = None
        elif SKLEARN_AVAILABLE:
            try:
                self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
                self.use_tfidf = True
                self.embedding_dimension = 1000  # TF-IDF dimension
                logger.info("✅ Using TF-IDF vectorizer as fallback")
            except Exception as e:
                logger.error(f"❌ Failed to initialize TF-IDF vectorizer: {e}")
                self.vectorizer = None
        else:
            logger.error("❌ No embedding method available")
    
    def create_recipe_text(self, recipe: Recipe) -> str:
        """Create a comprehensive text representation of the recipe for embedding"""
        text_parts = []
        
        # Basic recipe info
        text_parts.append(f"Title: {recipe.title}")
        text_parts.append(f"Cuisine: {recipe.cuisine}")
        text_parts.append(f"Meal type: {recipe.meal_type}")
        text_parts.append(f"Difficulty: {recipe.difficulty_level}")
        
        # Summary
        if recipe.summary:
            text_parts.append(f"Summary: {recipe.summary}")
        
        # Dietary tags
        if recipe.dietary_tags:
            dietary_tags = [tag for tag in recipe.dietary_tags if not tag.startswith('contains-')]
            if dietary_tags:
                text_parts.append(f"Dietary: {', '.join(dietary_tags)}")
        
        # Allergens
        if recipe.dietary_tags:
            allergens = [tag.replace('contains-', '') for tag in recipe.dietary_tags if tag.startswith('contains-')]
            if allergens:
                text_parts.append(f"Contains: {', '.join(allergens)}")
        
        # Ingredients
        if recipe.ingredients:
            ingredient_names = []
            for ingredient in recipe.ingredients:
                if hasattr(ingredient, 'ingredient') and ingredient.ingredient:
                    ingredient_names.append(ingredient.ingredient.name)
                elif hasattr(ingredient, 'name'):
                    ingredient_names.append(ingredient.name)
            
            if ingredient_names:
                text_parts.append(f"Ingredients: {', '.join(ingredient_names)}")
        
        # Instructions (first few steps)
        if recipe.instructions:
            instruction_texts = []
            for instruction in recipe.instructions[:3]:  # First 3 steps
                if hasattr(instruction, 'description'):
                    instruction_texts.append(instruction.description)
                elif hasattr(instruction, 'step_description'):
                    instruction_texts.append(instruction.step_description)
            
            if instruction_texts:
                text_parts.append(f"Instructions: {' '.join(instruction_texts)}")
        
        # Nutrition info
        if hasattr(recipe, 'per_serving_calories') and recipe.per_serving_calories:
            text_parts.append(f"Calories per serving: {recipe.per_serving_calories}")
        
        if hasattr(recipe, 'per_serving_protein') and recipe.per_serving_protein:
            text_parts.append(f"Protein per serving: {recipe.per_serving_protein}g")
        
        # Cooking info
        text_parts.append(f"Prep time: {recipe.prep_time} minutes")
        text_parts.append(f"Cook time: {recipe.cook_time} minutes")
        text_parts.append(f"Servings: {recipe.servings}")
        
        return " | ".join(text_parts)
    
    def generate_embeddings_for_all_recipes(self) -> int:
        """Generate embeddings for all recipes in the database"""
        if not self.embedding_model and not self.vectorizer:
            logger.error("❌ Cannot generate embeddings: no model available")
            return 0
        
        # Get all active recipes
        recipes = self.db.query(Recipe).filter(Recipe.is_active == True).all()
        total_recipes = len(recipes)
        
        logger.info(f"🔄 Generating embeddings for {total_recipes} recipes...")
        
        updated_count = 0
        batch_size = 50
        
        for i in range(0, total_recipes, batch_size):
            batch = recipes[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(total_recipes + batch_size - 1)//batch_size}")
            
            # Prepare texts for this batch
            recipe_texts = []
            recipe_ids = []
            
            for recipe in batch:
                recipe_text = self.create_recipe_text(recipe)
                recipe_texts.append(recipe_text)
                recipe_ids.append(recipe.id)
            
            try:
                if self.embedding_model:
                    # Use sentence transformers
                    embeddings = self.embedding_model.encode(recipe_texts, convert_to_numpy=True)
                elif self.vectorizer:
                    # Use TF-IDF
                    if i == 0:  # Fit vectorizer on first batch
                        embeddings = self.vectorizer.fit_transform(recipe_texts).toarray()
                    else:
                        embeddings = self.vectorizer.transform(recipe_texts).toarray()
                else:
                    logger.error("❌ No embedding method available")
                    continue
                
                # Update recipes with embeddings
                for j, recipe in enumerate(batch):
                    # Convert numpy array to list for JSON storage
                    embedding_list = embeddings[j].tolist()
                    recipe.embedding = embedding_list
                    updated_count += 1
                
                # Commit batch
                self.db.commit()
                logger.info(f"✅ Updated {len(batch)} recipes with embeddings")
                
            except Exception as e:
                logger.error(f"❌ Error processing batch {i//batch_size + 1}: {e}")
                self.db.rollback()
                continue
        
        logger.info(f"🎉 Successfully generated embeddings for {updated_count} recipes!")
        return updated_count
    
    def verify_embeddings(self) -> Dict[str, Any]:
        """Verify that embeddings were generated correctly"""
        logger.info("🔍 Verifying embeddings...")
        
        # Count recipes with embeddings
        recipes_with_embeddings = self.db.query(Recipe).filter(
            Recipe.is_active == True,
            Recipe.embedding.isnot(None)
        ).count()
        
        total_recipes = self.db.query(Recipe).filter(Recipe.is_active == True).count()
        
        # Check embedding dimensions
        sample_recipe = self.db.query(Recipe).filter(
            Recipe.is_active == True,
            Recipe.embedding.isnot(None)
        ).first()
        
        embedding_dim = None
        if sample_recipe and sample_recipe.embedding:
            embedding_dim = len(sample_recipe.embedding)
        
        # Test similarity search
        similarity_test = self.test_similarity_search()
        
        return {
            "total_recipes": total_recipes,
            "recipes_with_embeddings": recipes_with_embeddings,
            "embedding_dimension": embedding_dim,
            "coverage_percentage": (recipes_with_embeddings / total_recipes * 100) if total_recipes > 0 else 0,
            "similarity_test": similarity_test
        }
    
    def test_similarity_search(self) -> Dict[str, Any]:
        """Test similarity search functionality"""
        try:
            # Get a sample recipe with embedding
            sample_recipe = self.db.query(Recipe).filter(
                Recipe.is_active == True,
                Recipe.embedding.isnot(None)
            ).first()
            
            if not sample_recipe:
                return {"error": "No recipes with embeddings found"}
            
            # Test query
            test_query = "chicken pasta italian"
            if self.embedding_model:
                query_embedding = self.embedding_model.encode([test_query])[0]
            elif self.vectorizer:
                query_embedding = self.vectorizer.transform([test_query]).toarray()[0]
            else:
                return {"error": "No embedding method available", "status": "failed"}
            
            # Find similar recipes
            recipes = self.db.query(Recipe).filter(
                Recipe.is_active == True,
                Recipe.embedding.isnot(None)
            ).limit(10).all()
            
            similarities = []
            for recipe in recipes:
                recipe_embedding = np.array(recipe.embedding)
                similarity = np.dot(query_embedding, recipe_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(recipe_embedding)
                )
                similarities.append({
                    "title": recipe.title,
                    "similarity": float(similarity),
                    "cuisine": recipe.cuisine
                })
            
            # Sort by similarity
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            return {
                "test_query": test_query,
                "top_matches": similarities[:3],
                "status": "success"
            }
            
        except Exception as e:
            return {"error": str(e), "status": "failed"}

def main():
    """Main function to generate embeddings for all recipes"""
    db = SessionLocal()
    
    try:
        if not SENTENCE_TRANSFORMERS_AVAILABLE and not SKLEARN_AVAILABLE:
            logger.error("❌ Cannot proceed: no embedding method available")
            logger.error("Install with: pip install sentence-transformers OR pip install scikit-learn")
            return
        
        generator = RecipeEmbeddingGenerator(db)
        
        # Generate embeddings
        updated_count = generator.generate_embeddings_for_all_recipes()
        
        if updated_count > 0:
            # Verify embeddings
            verification = generator.verify_embeddings()
            
            logger.info("📊 Embedding Generation Summary:")
            logger.info(f"  Total recipes: {verification['total_recipes']}")
            logger.info(f"  Recipes with embeddings: {verification['recipes_with_embeddings']}")
            logger.info(f"  Coverage: {verification['coverage_percentage']:.1f}%")
            logger.info(f"  Embedding dimension: {verification['embedding_dimension']}")
            
            if verification['similarity_test']['status'] == 'success':
                logger.info("✅ Similarity search test passed!")
                logger.info(f"  Test query: '{verification['similarity_test']['test_query']}'")
                logger.info("  Top matches:")
                for match in verification['similarity_test']['top_matches']:
                    logger.info(f"    - {match['title']} ({match['cuisine']}) - {match['similarity']:.3f}")
            else:
                logger.warning(f"⚠️ Similarity search test failed: {verification['similarity_test'].get('error', 'Unknown error')}")
        
        logger.info("🎉 Recipe embedding generation completed!")
        
    except Exception as e:
        logger.error(f"❌ Error generating embeddings: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
