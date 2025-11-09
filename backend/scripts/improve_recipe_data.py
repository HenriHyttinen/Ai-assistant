#!/usr/bin/env python3
"""
Script to improve recipe names and instructions using AI
Replaces generic names like "Recipe 101" with descriptive names
and generic instructions like "Instruction for step 1" with actual cooking instructions
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Recipe, RecipeIngredient, RecipeInstruction, Ingredient
from ai.nutrition_ai import NutritionAI
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_recipe_ingredients(db, recipe: Recipe) -> List[Dict[str, Any]]:
    """Get ingredients for a recipe"""
    ingredients = []
    recipe_ingredients = db.query(RecipeIngredient).filter(
        RecipeIngredient.recipe_id == recipe.id
    ).all()
    
    for ri in recipe_ingredients:
        ingredient = db.query(Ingredient).filter(Ingredient.id == ri.ingredient_id).first()
        if ingredient:
            ingredients.append({
                'name': ingredient.name,
                'quantity': ri.quantity,
                'unit': ri.unit
            })
    
    return ingredients

def generate_recipe_name(recipe: Recipe, ingredients: List[Dict[str, Any]], nutrition_ai: NutritionAI) -> str:
    """Generate a descriptive recipe name based on ingredients, cuisine, and meal type"""
    try:
        # Create a prompt for generating recipe name
        ingredient_names = [ing['name'] for ing in ingredients[:5]]  # Use first 5 ingredients
        prompt = f"""Generate a creative, descriptive recipe name for a {recipe.meal_type} recipe.

Cuisine: {recipe.cuisine or 'International'}
Meal Type: {recipe.meal_type}
Main Ingredients: {', '.join(ingredient_names)}
Dietary Tags: {', '.join(recipe.dietary_tags or [])}

Requirements:
- The name should be descriptive and appetizing
- It should reflect the cuisine and main ingredients
- It should be suitable for a {recipe.meal_type} meal
- Keep it concise (2-6 words)
- Do NOT include generic words like "Recipe" or numbers

Return ONLY the recipe name, nothing else."""

        name = nutrition_ai._call_openai_fast(prompt, temperature=0.8)
        name = name.strip().strip('"').strip("'")
        
        # Clean up the name
        if name.lower().startswith('recipe name:'):
            name = name.split(':', 1)[1].strip()
        if name.lower().startswith('name:'):
            name = name.split(':', 1)[1].strip()
        
        return name[:100]  # Limit length
    except Exception as e:
        logger.warning(f"Failed to generate name for recipe {recipe.id}: {e}")
        # Fallback: create name from ingredients and cuisine
        ingredient_names = [ing['name'] for ing in ingredients[:2]]
        if recipe.cuisine:
            return f"{recipe.cuisine} {ingredient_names[0] if ingredient_names else 'Dish'}"
        return f"{ingredient_names[0] if ingredient_names else 'Delicious'} {recipe.meal_type.title()}"

def generate_recipe_instructions(
    recipe: Recipe, 
    ingredients: List[Dict[str, Any]], 
    nutrition_ai: NutritionAI,
    num_steps: int
) -> List[str]:
    """Generate actual cooking instructions based on recipe details"""
    try:
        ingredient_list = []
        for ing in ingredients:
            ingredient_list.append(f"{ing['quantity']:.1f}{ing['unit']} {ing['name']}")
        
        prompt = f"""Generate detailed, step-by-step cooking instructions for a {recipe.meal_type} recipe.

Recipe Name: {recipe.title}
Cuisine: {recipe.cuisine or 'International'}
Meal Type: {recipe.meal_type}
Servings: {recipe.servings}
Prep Time: {recipe.prep_time} minutes
Cook Time: {recipe.cook_time} minutes
Difficulty: {recipe.difficulty_level}
Dietary Tags: {', '.join(recipe.dietary_tags or [])}

Ingredients:
{chr(10).join(ingredient_list)}

Requirements:
- Generate exactly {num_steps} clear, sequential steps
- Each step should be specific and actionable
- Include cooking techniques, temperatures, and times where appropriate
- Steps should build on each other logically
- Make it sound like a real recipe from a cookbook
- Each step should be 1-2 sentences

Format: Return each step on a new line, numbered as "Step 1:", "Step 2:", etc."""

        response = nutrition_ai._call_openai_fast(prompt, temperature=0.7)
        
        # Parse the response into steps
        instructions = []
        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Remove step numbers if present
            if line.lower().startswith('step'):
                line = line.split(':', 1)[1].strip() if ':' in line else line[4:].strip()
            # Remove leading numbers
            if line and line[0].isdigit():
                line = line.split('.', 1)[1].strip() if '.' in line else line[1:].strip()
            if line:
                instructions.append(line)
        
        # Ensure we have the right number of steps
        if len(instructions) < num_steps:
            # Pad with generic instructions if needed
            for i in range(len(instructions), num_steps):
                instructions.append(f"Continue cooking until done, adjusting heat as needed.")
        elif len(instructions) > num_steps:
            instructions = instructions[:num_steps]
        
        return instructions
    except Exception as e:
        logger.warning(f"Failed to generate instructions for recipe {recipe.id}: {e}")
        # Fallback: generic but slightly better instructions
        return [
            f"Prepare all ingredients as listed.",
            f"Follow standard {recipe.meal_type} preparation techniques.",
            f"Cook according to {recipe.cuisine or 'standard'} cooking methods.",
            f"Season to taste and serve hot."
        ][:num_steps]

def improve_recipes(limit: int = None, dry_run: bool = False):
    """Improve recipe names and instructions for generic recipes"""
    db = SessionLocal()
    nutrition_ai = NutritionAI()
    
    try:
        # Find recipes with generic names
        all_recipes = db.query(Recipe).filter(
            Recipe.title.like('Recipe %')
        ).all()
        
        if limit:
            all_recipes = all_recipes[:limit]
        
        logger.info(f"Found {len(all_recipes)} recipes with generic names to improve")
        
        improved = 0
        for i, recipe in enumerate(all_recipes, 1):
            try:
                logger.info(f"Processing recipe {i}/{len(all_recipes)}: {recipe.id} ({recipe.title})")
                
                # Get ingredients
                ingredients = get_recipe_ingredients(db, recipe)
                if not ingredients:
                    logger.warning(f"Recipe {recipe.id} has no ingredients, skipping")
                    continue
                
                # Generate new name
                new_name = generate_recipe_name(recipe, ingredients, nutrition_ai)
                logger.info(f"  New name: {new_name}")
                
                # Get existing instructions
                existing_instructions = db.query(RecipeInstruction).filter(
                    RecipeInstruction.recipe_id == recipe.id
                ).order_by(RecipeInstruction.step_number).all()
                
                num_steps = len(existing_instructions) if existing_instructions else 4
                
                # Generate new instructions
                new_instructions = generate_recipe_instructions(
                    recipe, ingredients, nutrition_ai, num_steps
                )
                logger.info(f"  Generated {len(new_instructions)} instructions")
                
                if not dry_run:
                    # Update recipe name
                    recipe.title = new_name
                    recipe.summary = f"A delicious {new_name.lower()} perfect for {recipe.meal_type}"
                    
                    # Update instructions
                    for idx, instruction_text in enumerate(new_instructions, 1):
                        if idx <= len(existing_instructions):
                            # Update existing instruction
                            existing_instructions[idx - 1].description = instruction_text
                        else:
                            # Create new instruction
                            new_instruction = RecipeInstruction(
                                recipe_id=recipe.id,
                                step_number=idx,
                                step_title=f"Step {idx}",
                                description=instruction_text,
                                time_required=recipe.cook_time // num_steps if recipe.cook_time else 5
                            )
                            db.add(new_instruction)
                    
                    db.commit()
                    improved += 1
                    logger.info(f"  ✅ Updated recipe {recipe.id}")
                else:
                    logger.info(f"  [DRY RUN] Would update recipe {recipe.id}")
                
            except Exception as e:
                logger.error(f"Error processing recipe {recipe.id}: {e}", exc_info=True)
                db.rollback()
                continue
        
        logger.info(f"✅ Improved {improved} recipes")
        
    except Exception as e:
        logger.error(f"Error improving recipes: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Improve recipe names and instructions")
    parser.add_argument("--limit", type=int, help="Limit number of recipes to process")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually update the database")
    args = parser.parse_args()
    
    improve_recipes(limit=args.limit, dry_run=args.dry_run)

