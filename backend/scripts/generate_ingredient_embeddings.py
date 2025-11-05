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
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
                    logger.error("   This may be due to scipy/numpy version compatibility issues")
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
        text_parts.append(ingredient.name)
        text_parts.append(ingredient.category)
        
        # Nutrition info (key nutritional properties)
        if ingredient.calories and ingredient.calories > 0:
            text_parts.append(f"{ingredient.calories} calories")
        
        if ingredient.protein and ingredient.protein > 0:
            text_parts.append(f"{ingredient.protein}g protein")
        
        if ingredient.carbs and ingredient.carbs > 0:
            text_parts.append(f"{ingredient.carbs}g carbs")
        
        if ingredient.fats and ingredient.fats > 0:
            text_parts.append(f"{ingredient.fats}g fats")
        
        return " ".join(text_parts)
    
    def generate_embeddings_for_all_ingredients(self) -> int:
        """Generate embeddings for all ingredients in the database"""
        if not self.embedding_model:
            logger.error("❌ Cannot generate embeddings: embedding model not available")
            logger.error("   This may be due to scipy/numpy version compatibility issues")
            logger.error("   Try: pip install --upgrade numpy scipy sentence-transformers")
            return 0
        
        logger.info("🚀 Starting ingredient embedding generation...")
        
        # Get all ingredients
        ingredients = self.db.query(Ingredient).all()
        total_ingredients = len(ingredients)
        logger.info(f"📊 Found {total_ingredients} ingredients to process")
        
        if total_ingredients == 0:
            logger.warning("⚠️  No ingredients found in database")
            return 0
        
        updated_count = 0
        batch_size = 100
        
        for i in range(0, total_ingredients, batch_size):
            batch = ingredients[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_ingredients + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} ingredients)...")
            
            # Prepare texts for batch encoding
            texts = []
            for ingredient in batch:
                text = self.create_ingredient_text(ingredient)
                texts.append(text)
            
            # Generate embeddings in batch
            try:
                embeddings = self.embedding_model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
                
                # Update ingredients with embeddings
                for ingredient, embedding in zip(batch, embeddings):
                    # Convert numpy array to list for JSON storage
                    ingredient.embedding = embedding.tolist()
                    updated_count += 1
                
                # Commit batch
                self.db.commit()
                logger.info(f"✅ Updated {updated_count}/{total_ingredients} ingredients with embeddings")
                
            except Exception as e:
                logger.error(f"❌ Error processing batch {batch_num}: {e}")
                self.db.rollback()
                continue
        
        logger.info(f"🎉 Successfully generated embeddings for {updated_count} ingredients!")
        return updated_count
    
    def verify_embeddings(self) -> Dict[str, Any]:
        """Verify that embeddings were generated correctly"""
        total_ingredients = self.db.query(Ingredient).count()
        ingredients_with_embeddings = self.db.query(Ingredient).filter(
            Ingredient.embedding.isnot(None)
        ).count()
        
        coverage_percentage = (ingredients_with_embeddings / total_ingredients * 100) if total_ingredients > 0 else 0
        
        return {
            "total_ingredients": total_ingredients,
            "ingredients_with_embeddings": ingredients_with_embeddings,
            "coverage_percentage": coverage_percentage
        }

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
            
            if verification['coverage_percentage'] >= 100:
                logger.info("✅ All ingredients now have embeddings!")
            elif verification['coverage_percentage'] >= 500:
                logger.info(f"✅ Embedding requirement met (≥500 ingredients with embeddings)")
            else:
                logger.warning(f"⚠️  Only {verification['ingredients_with_embeddings']} ingredients have embeddings")
        else:
            logger.error("❌ No embeddings were generated")
            
    except Exception as e:
        logger.error(f"❌ Error generating embeddings: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()

