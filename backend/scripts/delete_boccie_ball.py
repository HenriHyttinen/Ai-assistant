#!/usr/bin/env python3
"""
Quick script to delete the "Boccie Ball" drink recipe from the database
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from database import SessionLocal
from models.recipe import Recipe, RecipeIngredient, RecipeInstruction
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def delete_boccie_ball():
    """Delete the Boccie Ball recipe"""
    db: Session = SessionLocal()
    try:
        # Find the recipe by title
        recipe = db.query(Recipe).filter(
            Recipe.title.ilike('%boccie ball%')
        ).first()
        
        if not recipe:
            logger.warning("❌ Recipe 'Boccie Ball' not found in database")
            return
        
        logger.info(f"✅ Found recipe: {recipe.title} (ID: {recipe.id})")
        
        # Delete related instructions
        instructions_deleted = db.query(RecipeInstruction).filter(
            RecipeInstruction.recipe_id == recipe.id
        ).delete()
        
        # Delete related ingredients
        ingredients_deleted = db.query(RecipeIngredient).filter(
            RecipeIngredient.recipe_id == recipe.id
        ).delete()
        
        # Delete the recipe itself
        db.delete(recipe)
        db.commit()
        
        logger.info(f"✅ Deleted recipe '{recipe.title}'")
        logger.info(f"   - Deleted {instructions_deleted} instructions")
        logger.info(f"   - Deleted {ingredients_deleted} ingredients")
        
    except Exception as e:
        logger.error(f"❌ Error deleting recipe: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    delete_boccie_ball()

