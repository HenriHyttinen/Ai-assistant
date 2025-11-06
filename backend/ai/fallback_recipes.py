"""
Fallback recipe system for when AI generation fails
Provides high-quality, diverse recipes to avoid duplicates and placeholder content
"""

import random
from typing import Dict, List, Any

class FallbackRecipeGenerator:
    def __init__(self):
        self.recipe_templates = {
            'breakfast': [
                {
                    'base_name': 'Mediterranean Morning Bowl',
                    'cuisines': ['Mediterranean', 'Greek', 'Turkish'],
                    'ingredients': ['Greek yogurt', 'honey', 'nuts', 'berries'],
                    'cooking_method': 'no-cook',
                    'calorie_base': 400
                },
                {
                    'base_name': 'Asian Sunrise Stir-Fry',
                    'cuisines': ['Asian', 'Chinese', 'Thai'],
                    'ingredients': ['eggs', 'vegetables', 'soy sauce', 'sesame oil'],
                    'cooking_method': 'stir-fry',
                    'calorie_base': 350
                },
                {
                    'base_name': 'Mexican Morning Wrap',
                    'cuisines': ['Mexican', 'Tex-Mex'],
                    'ingredients': ['tortilla', 'eggs', 'beans', 'cheese', 'salsa'],
                    'cooking_method': 'wrap',
                    'calorie_base': 450
                },
                {
                    'base_name': 'French Crepe Delight',
                    'cuisines': ['French', 'European'],
                    'ingredients': ['flour', 'eggs', 'milk', 'butter', 'filling'],
                    'cooking_method': 'pan-fry',
                    'calorie_base': 380
                },
                {
                    'base_name': 'Indian Spiced Oats',
                    'cuisines': ['Indian', 'South Asian'],
                    'ingredients': ['oats', 'spices', 'vegetables', 'ghee'],
                    'cooking_method': 'simmer',
                    'calorie_base': 320
                }
            ],
            'lunch': [
                {
                    'base_name': 'Mediterranean Power Bowl',
                    'cuisines': ['Mediterranean', 'Greek'],
                    'ingredients': ['quinoa', 'vegetables', 'olive oil', 'herbs'],
                    'cooking_method': 'bowl',
                    'calorie_base': 500
                },
                {
                    'base_name': 'Asian Fusion Noodle Bowl',
                    'cuisines': ['Asian', 'Japanese', 'Thai'],
                    'ingredients': ['noodles', 'vegetables', 'protein', 'sauce'],
                    'cooking_method': 'stir-fry',
                    'calorie_base': 550
                },
                {
                    'base_name': 'Mexican Fiesta Bowl',
                    'cuisines': ['Mexican', 'Tex-Mex'],
                    'ingredients': ['rice', 'beans', 'vegetables', 'salsa', 'cheese'],
                    'cooking_method': 'bowl',
                    'calorie_base': 480
                },
                {
                    'base_name': 'Italian Pasta Primavera',
                    'cuisines': ['Italian', 'European'],
                    'ingredients': ['pasta', 'vegetables', 'olive oil', 'herbs'],
                    'cooking_method': 'boil',
                    'calorie_base': 520
                },
                {
                    'base_name': 'Middle Eastern Platter',
                    'cuisines': ['Middle Eastern', 'Lebanese'],
                    'ingredients': ['grains', 'vegetables', 'tahini', 'herbs'],
                    'cooking_method': 'platter',
                    'calorie_base': 470
                }
            ],
            'dinner': [
                {
                    'base_name': 'Mediterranean Stuffed Vegetables',
                    'cuisines': ['Mediterranean', 'Greek'],
                    'ingredients': ['bell peppers', 'rice', 'herbs', 'olive oil'],
                    'cooking_method': 'bake',
                    'calorie_base': 450
                },
                {
                    'base_name': 'Asian Curry Delight',
                    'cuisines': ['Asian', 'Thai', 'Indian'],
                    'ingredients': ['protein', 'coconut milk', 'curry paste', 'vegetables'],
                    'cooking_method': 'simmer',
                    'calorie_base': 580
                },
                {
                    'base_name': 'Mexican Enchilada Skillet',
                    'cuisines': ['Mexican', 'Tex-Mex'],
                    'ingredients': ['tortillas', 'beans', 'cheese', 'sauce'],
                    'cooking_method': 'bake',
                    'calorie_base': 520
                },
                {
                    'base_name': 'Italian Risotto Special',
                    'cuisines': ['Italian', 'European'],
                    'ingredients': ['rice', 'broth', 'vegetables', 'cheese'],
                    'cooking_method': 'simmer',
                    'calorie_base': 480
                },
                {
                    'base_name': 'Middle Eastern Tagine',
                    'cuisines': ['Middle Eastern', 'Moroccan'],
                    'ingredients': ['protein', 'vegetables', 'spices', 'dried fruits'],
                    'cooking_method': 'slow-cook',
                    'calorie_base': 500
                }
            ],
            'snack': [
                {
                    'base_name': 'Mediterranean Hummus Plate',
                    'cuisines': ['Mediterranean', 'Middle Eastern'],
                    'ingredients': ['hummus', 'vegetables', 'pita', 'olive oil'],
                    'cooking_method': 'no-cook',
                    'calorie_base': 200
                },
                {
                    'base_name': 'Asian Edamame Mix',
                    'cuisines': ['Asian', 'Japanese'],
                    'ingredients': ['edamame', 'seaweed', 'sesame', 'soy sauce'],
                    'cooking_method': 'steam',
                    'calorie_base': 180
                },
                {
                    'base_name': 'Mexican Guacamole Bowl',
                    'cuisines': ['Mexican', 'Tex-Mex'],
                    'ingredients': ['avocado', 'lime', 'tomatoes', 'chips'],
                    'cooking_method': 'mash',
                    'calorie_base': 220
                },
                {
                    'base_name': 'Italian Bruschetta',
                    'cuisines': ['Italian', 'European'],
                    'ingredients': ['bread', 'tomatoes', 'basil', 'olive oil'],
                    'cooking_method': 'toast',
                    'calorie_base': 190
                },
                {
                    'base_name': 'Middle Eastern Mezze',
                    'cuisines': ['Middle Eastern', 'Lebanese'],
                    'ingredients': ['dips', 'vegetables', 'pita', 'olives'],
                    'cooking_method': 'platter',
                    'calorie_base': 210
                }
            ]
        }
    
    def generate_unique_recipe(self, meal_type: str, target_calories: int, target_cuisine: str, existing_names: List[str], db=None) -> Dict[str, Any]:
        """Generate a unique recipe avoiding duplicates"""
        import time
        
        # Get available templates for this meal type
        templates = self.recipe_templates.get(meal_type, self.recipe_templates['breakfast'])
        
        # Filter by cuisine if possible
        cuisine_templates = [t for t in templates if target_cuisine.lower() in [c.lower() for c in t['cuisines']]]
        if not cuisine_templates:
            cuisine_templates = templates
        
        # Try to find a unique recipe
        max_attempts = 10
        for attempt in range(max_attempts):
            template = random.choice(cuisine_templates)
            
            # CRITICAL FIX: Avoid adding suffixes that create duplicates - use cuisine and ingredients instead
            base_name = template['base_name']
            
            # Check if base_name already exists (with or without suffix)
            base_exists = any(base_name.lower() in name.lower() for name in existing_names)
            
            if base_exists:
                # Try a different template instead of adding a suffix
                continue  # Try next template
            else:
                # Use base name without suffix if it's unique
                unique_name = base_name
            
            # Check if this name is unique
            if unique_name not in existing_names:
                return self._build_recipe(unique_name, template, target_calories, target_cuisine, db=db)
        
        # If we can't find a unique name, try a completely different template
        # CRITICAL FIX: Don't add timestamp suffixes - use a different template instead
        all_templates = self.recipe_templates.get(meal_type, self.recipe_templates['breakfast'])
        used_templates = [t for t in all_templates if any(t['base_name'].lower() in name.lower() for name in existing_names)]
        available_templates = [t for t in all_templates if t not in used_templates]
        
        if available_templates:
            template = random.choice(available_templates)
            unique_name = template['base_name']
        else:
            # Last resort: use timestamp but make it clear it's a fallback
            template = random.choice(cuisine_templates)
            timestamp = int(time.time() * 1000) % 10000
            unique_name = f"{template['base_name']} {timestamp}"
        
        return self._build_recipe(unique_name, template, target_calories, target_cuisine, db=db)
    
    def _build_recipe(self, name: str, template: Dict[str, Any], target_calories: int, target_cuisine: str, db=None) -> Dict[str, Any]:
        """Build a complete recipe from template"""
        
        # CRITICAL FIX: Define high-calorie ingredients that need quantity limits
        high_calorie_ingredients = {
            'ghee', 'butter', 'oil', 'sesame oil', 'olive oil', 'vegetable oil',
            'coconut oil', 'nuts', 'almonds', 'walnuts', 'peanuts', 'cashews',
            'cheese', 'goat cheese', 'feta cheese', 'parmesan', 'cheddar'
        }
        
        # Create detailed ingredients with validation
        ingredients = []
        for i, ingredient in enumerate(template['ingredients']):
            # Base quantity calculation
            base_quantity = 50 + (i * 15)  # Reduced from 25 to 15 to prevent excessive quantities
            unit = 'g' if i % 2 == 0 else 'ml'
            
            # CRITICAL FIX: Validate and limit high-calorie ingredients
            ingredient_lower = ingredient.lower()
            is_high_calorie = any(hc in ingredient_lower for hc in high_calorie_ingredients)
            
            if is_high_calorie:
                # Limit high-calorie ingredients to max 30g/ml per serving
                quantity = min(base_quantity, 30)
                # For oils/fats, prefer ml unit
                if any(oil in ingredient_lower for oil in ['oil', 'ghee', 'butter']):
                    unit = 'ml'
                else:
                    unit = 'g'
            else:
                # Regular ingredients can have higher quantities
                quantity = base_quantity
            
            ingredients.append({
                'name': ingredient,
                'quantity': quantity,
                'unit': unit
            })
        
        # CRITICAL FIX: Calculate nutrition from actual ingredients instead of placeholder values
        # Use ingredient database to get accurate nutrition values
        calculated_nutrition = None
        if db:
            try:
                from ai.nutrition_ai import NutritionAI
                nutrition_ai = NutritionAI()
                calculated_nutrition = nutrition_ai._calculate_recipe_nutrition(ingredients, db)
                if calculated_nutrition and calculated_nutrition.get('calories', 0) > 0:
                    # Use calculated nutrition from ingredients (accurate)
                    calories = int(calculated_nutrition.get('calories', target_calories))
                    protein = round(calculated_nutrition.get('protein', 0), 1)
                    carbs = round(calculated_nutrition.get('carbs', 0), 1)
                    fats = round(calculated_nutrition.get('fats', 0), 1)
                else:
                    # Fallback to formula if calculation fails
                    calculated_nutrition = None
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to calculate nutrition from ingredients for fallback recipe: {e}")
                calculated_nutrition = None
        
        # Fallback to formula-based calculation if database calculation failed
        if not calculated_nutrition:
            protein_cals = int(target_calories * 0.25)
            carbs_cals = int(target_calories * 0.45)
            fats_cals = int(target_calories * 0.30)
            
            calories = target_calories
            protein = protein_cals // 4
            carbs = carbs_cals // 4
            fats = fats_cals // 9
        
        # Create detailed instructions
        instructions = [
            {'step': 1, 'description': f"Prepare all ingredients for {name.lower()}"},
            {'step': 2, 'description': f"Cook using {template['cooking_method']} method"},
            {'step': 3, 'description': f"Season with {target_cuisine} spices and herbs"},
            {'step': 4, 'description': "Plate beautifully and serve immediately"}
        ]
        
        # Determine dietary tags
        dietary_tags = ['balanced']
        if 'vegetarian' in template['ingredients'] or 'vegetables' in str(template['ingredients']):
            dietary_tags.append('vegetarian')
        if 'gluten' not in str(template['ingredients']).lower():
            dietary_tags.append('gluten-free')
        
        return {
            "meal_name": name,
            "recipe": {
                "title": name,
                "cuisine": target_cuisine,
                "prep_time": random.randint(10, 20),
                "cook_time": random.randint(15, 35),
                "servings": 1,
                "difficulty": random.choice(['easy', 'medium']),
                "summary": f"A delicious {template['cooking_method']} dish with {target_cuisine} flavors",
                "ingredients": ingredients,
                "instructions": instructions,
                "dietary_tags": dietary_tags,
                "nutrition": {
                    "calories": calories,
                    "protein": protein,
                    "carbs": carbs,
                    "fats": fats,
                    "per_serving_calories": calories,
                    "per_serving_protein": protein,
                    "per_serving_carbs": carbs,
                    "per_serving_fats": fats
                },
                "ai_generated": False,
                "database_fallback": True
            },
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fats": fats
        }

# Global instance
fallback_generator = FallbackRecipeGenerator()



