#!/usr/bin/env python3
"""
Generate vector embeddings for all ingredients to enable RAG (Retrieval-Augmented Generation) search.
This script will:
1. Load all ingredients from the database
2. Generate embeddings for each ingredient using sentence transformers
3. Store embeddings in the database for fast similarity search
"""

import sys
import os
# Add backend directory to path (need 3 levels up from _legacy subdirectory)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import SessionLocal
from models.recipe import Ingredient
from sqlalchemy.orm import Session
import logging
import numpy as np
from typing import List, Dict, Any

# Use model_cache which handles embedding model initialization
try:
    from ai.model_cache import model_cache
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("❌ model_cache not available")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IngredientEmbeddingGenerator:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_model = None
        self.embedding_dimension = 384  # all-MiniLM-L6-v2 dimension
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # Use model_cache which already handles embedding model initialization
                self.embedding_model = model_cache.embedding_model
                if self.embedding_model:
                    logger.info("✅ Loaded sentence transformer model from model_cache: all-MiniLM-L6-v2")
                else:
                    logger.error("❌ model_cache embedding_model is None - embedding generation will not work")
                    logger.error("   This is likely due to scipy/numpy version compatibility issues")
                    self.embedding_model = None
            except Exception as e:
                logger.error(f"❌ Failed to load embedding model from model_cache: {e}")
                self.embedding_model = None
        else:
            logger.error("❌ No embedding method available")
    
    def create_ingredient_text(self, ingredient: Ingredient) -> str:
        """Create a comprehensive text representation of the ingredient for embedding"""
        text_parts = []
        
        # Basic ingredient info
        text_parts.append(f"Name: {ingredient.name}")
        text_parts.append(f"Category: {ingredient.category}")
        text_parts.append(f"Unit: {ingredient.unit}")
        
        # Nutrition info (key nutritional properties)
        if ingredient.calories and ingredient.calories > 0:
            text_parts.append(f"Calories: {ingredient.calories} per 100g/ml")
        
        if ingredient.protein and ingredient.protein > 0:
            text_parts.append(f"Protein: {ingredient.protein}g per 100g/ml")
        
        if ingredient.carbs and ingredient.carbs > 0:
            text_parts.append(f"Carbs: {ingredient.carbs}g per 100g/ml")
        
        if ingredient.fats and ingredient.fats > 0:
            text_parts.append(f"Fats: {ingredient.fats}g per 100g/ml")
        
        # Micronutrients (key ones)
        micronutrient_info = []
        if ingredient.vitamin_c and ingredient.vitamin_c > 0:
            micronutrient_info.append(f"vitamin C: {ingredient.vitamin_c}mg")
        if ingredient.calcium and ingredient.calcium > 0:
            micronutrient_info.append(f"calcium: {ingredient.calcium}mg")
        if ingredient.iron and ingredient.iron > 0:
            micronutrient_info.append(f"iron: {ingredient.iron}mg")
        if ingredient.potassium and ingredient.potassium > 0:
            micronutrient_info.append(f"potassium: {ingredient.potassium}mg")
        
        if micronutrient_info:
            text_parts.append(f"Micronutrients: {', '.join(micronutrient_info)}")
        
        return " | ".join(text_parts)
    
    def generate_embeddings_for_all_ingredients(self) -> int:
        """Generate embeddings for all ingredients in the database"""
        if not self.embedding_model:
            logger.error("❌ Cannot generate embeddings: embedding model not available")
            logger.error("   This may be due to scipy/numpy version compatibility issues")
            logger.error("   Try: pip install --upgrade numpy scipy")
            return 0
        
        # Get all ingredients
        ingredients = self.db.query(Ingredient).all()
        total_ingredients = len(ingredients)
        
        logger.info(f"🔄 Generating embeddings for {total_ingredients} ingredients...")
        
        updated_count = 0
        batch_size = 100  # Larger batch size for ingredients (simpler text)
        
        for i in range(0, total_ingredients, batch_size):
            batch = ingredients[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(total_ingredients + batch_size - 1)//batch_size}")
            
            # Prepare texts for this batch
            ingredient_texts = []
            ingredient_ids = []
            
            for ingredient in batch:
                ingredient_text = self.create_ingredient_text(ingredient)
                ingredient_texts.append(ingredient_text)
                ingredient_ids.append(ingredient.id)
            
            try:
                if self.embedding_model:
                    # Use sentence transformers
                    embeddings = self.embedding_model.encode(ingredient_texts, convert_to_numpy=True)
                else:
                    logger.error("❌ No embedding method available")
                    continue
                
                # Update ingredients with embeddings
                for j, ingredient in enumerate(batch):
                    # Convert numpy array to list for JSON storage
                    embedding_list = embeddings[j].tolist()
                    ingredient.embedding = embedding_list
                    updated_count += 1
                
                # Commit batch
                self.db.commit()
                logger.info(f"✅ Updated {len(batch)} ingredients with embeddings")
                
            except Exception as e:
                logger.error(f"❌ Error processing batch {i//batch_size + 1}: {e}")
                self.db.rollback()
                continue
        
        logger.info(f"🎉 Successfully generated embeddings for {updated_count} ingredients!")
        return updated_count
    
    def verify_embeddings(self) -> Dict[str, Any]:
        """Verify that embeddings were generated correctly"""
        logger.info("🔍 Verifying embeddings...")
        
        # Count ingredients with embeddings
        ingredients_with_embeddings = self.db.query(Ingredient).filter(
            Ingredient.embedding.isnot(None)
        ).count()
        
        total_ingredients = self.db.query(Ingredient).count()
        
        # Check embedding dimensions
        sample_ingredient = self.db.query(Ingredient).filter(
            Ingredient.embedding.isnot(None)
        ).first()
        
        embedding_dim = None
        if sample_ingredient and sample_ingredient.embedding:
            embedding_dim = len(sample_ingredient.embedding)
        
        # Test similarity search
        similarity_test = self.test_similarity_search()
        
        return {
            "total_ingredients": total_ingredients,
            "ingredients_with_embeddings": ingredients_with_embeddings,
            "embedding_dimension": embedding_dim,
            "coverage_percentage": (ingredients_with_embeddings / total_ingredients * 100) if total_ingredients > 0 else 0,
            "similarity_test": similarity_test
        }
    
    def test_similarity_search(self) -> Dict[str, Any]:
        """Test similarity search functionality"""
        try:
            # Get a sample ingredient with embedding
            sample_ingredient = self.db.query(Ingredient).filter(
                Ingredient.embedding.isnot(None)
            ).first()
            
            if not sample_ingredient:
                return {"error": "No ingredients with embeddings found"}
            
            # Test query
            test_query = "chicken breast protein"
            if self.embedding_model:
                query_embedding = self.embedding_model.encode([test_query])[0]
            else:
                return {"error": "No embedding method available", "status": "failed"}
            
            # Find similar ingredients
            ingredients = self.db.query(Ingredient).filter(
                Ingredient.embedding.isnot(None)
            ).limit(10).all()
            
            similarities = []
            for ingredient in ingredients:
                ingredient_embedding = np.array(ingredient.embedding)
                similarity = np.dot(query_embedding, ingredient_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(ingredient_embedding)
                )
                similarities.append({
                    "name": ingredient.name,
                    "similarity": float(similarity),
                    "category": ingredient.category
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
    """Main function to generate embeddings for all ingredients"""
    db = SessionLocal()
    
    try:
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.error("❌ Cannot proceed: model_cache not available")
            logger.error("Install with: pip install sentence-transformers")
            return
        
        if not model_cache.embedding_model:
            logger.error("❌ Cannot proceed: embedding model failed to initialize")
            logger.error("   This may be due to scipy/numpy version compatibility issues")
            logger.error("   Try: pip install --upgrade numpy scipy sentence-transformers")
            return
        
        generator = IngredientEmbeddingGenerator(db)
        
        # Generate embeddings
        updated_count = generator.generate_embeddings_for_all_ingredients()
        
        if updated_count > 0:
            # Verify embeddings
            verification = generator.verify_embeddings()
            
            logger.info("📊 Embedding Generation Summary:")
            logger.info(f"  Total ingredients: {verification['total_ingredients']}")
            logger.info(f"  Ingredients with embeddings: {verification['ingredients_with_embeddings']}")
            logger.info(f"  Coverage: {verification['coverage_percentage']:.1f}%")
            logger.info(f"  Embedding dimension: {verification['embedding_dimension']}")
            
            if verification['similarity_test']['status'] == 'success':
                logger.info("✅ Similarity search test passed!")
                logger.info(f"  Test query: '{verification['similarity_test']['test_query']}'")
                logger.info("  Top matches:")
                for match in verification['similarity_test']['top_matches']:
                    logger.info(f"    - {match['name']} ({match['category']}) - {match['similarity']:.3f}")
            else:
                logger.warning(f"⚠️ Similarity search test failed: {verification['similarity_test'].get('error', 'Unknown error')}")
        
        logger.info("🎉 Ingredient embedding generation completed!")
        
    except Exception as e:
        logger.error(f"❌ Error generating embeddings: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()

