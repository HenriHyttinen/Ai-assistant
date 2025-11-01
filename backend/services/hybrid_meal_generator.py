"""
Smart Hybrid Meal Generator
Combines database recipes (50%) with AI pattern analysis (50%)
"""

import json
import random
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, String
from models.recipe import Recipe, RecipeIngredient, Ingredient
from models.nutrition import MealPlanMeal, MealPlan
from ai.nutrition_ai import NutritionAI
from ai.fallback_recipes import fallback_generator
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial

logger = logging.getLogger(__name__)

class HybridMealGenerator:
    def __init__(self):
        self.nutrition_ai = NutritionAI()
        self.logger = logger
    
    def generate_hybrid_meal_plan(
        self, 
        db: Session, 
        user_preferences: Dict[str, Any], 
        target_calories: int,
        meal_types: List[str] = ['breakfast', 'lunch', 'dinner', 'snack'],
        existing_meals: List[Dict[str, Any]] = None,
        database_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Generate meal plan: AI-only by default (database_only=False), or database-only (database_only=True)
        Database recipes are NOT pulled during initial generation - they're only available for swap/add operations
        """
        try:
            # CRITICAL: For initial meal plan generation, use AI-only (don't pull database recipes)
            # Database recipes are only available through swap/add operations
            # DATABASE FALLBACKS DISABLED - Commented out until we get AI-only working
            # if database_only:
            #     # Only pull database recipes if explicitly requested (database_only=True)
            #     self.logger.info(f"🔄 DATABASE-ONLY MODE: Starting with {len(meal_types)} meal types")
            #     database_meals = self._get_database_recipes(
            #         db, user_preferences, target_calories, meal_types, existing_meals
            #     )
            #     self.logger.info(f"📊 DATABASE MEALS: Got {len(database_meals)} meals from database")
            if database_only:
                # DATABASE FALLBACKS DISABLED - Force AI-only even if database_only is True
                self.logger.warning(f"⚠️ DATABASE-ONLY MODE REQUESTED BUT DISABLED - Using AI-only fallbacks")
                database_meals = []
                # Return database meals only
                return database_meals
            
            # AI-ONLY MODE: Generate all meals with AI (no database recipes)
            self.logger.info(f"🔄 AI-ONLY GENERATION: Starting with {len(meal_types)} meal types (no database recipes)")
            database_meals: List[Dict[str, Any]] = []  # Empty - no database recipes
            
            # Generate all meals with AI (AI-only mode)
            ai_meals: List[Dict[str, Any]] = []
            if not database_only:
                # AI-ONLY MODE: Generate ALL meals with AI (not just complementary ones)
                pattern_analysis = self._analyze_meal_patterns([])  # Empty pattern since no DB meals
                # Generate ALL meals with AI (not just 50%)
                ai_meals = self._generate_all_ai_meals(
                    db, pattern_analysis, user_preferences, target_calories, 
                    meal_types, existing_meals
                )
                self.logger.info(f"🤖 AI-ONLY MODE: Generated {len(ai_meals)} meals from AI (all meals)")
            
            # Step 4: Combine and balance the meal plan
            # CRITICAL: Pass user_preferences for daily calorie targeting
            final_meals = self._combine_and_balance_meals(
                database_meals, ai_meals, target_calories, meal_types, db, user_preferences
            )
            
            # Log final results
            # CRITICAL: Default to False (database) if flag is missing, since DB recipes are the default source
            db_count = len([m for m in final_meals if not m.get('recipe', {}).get('ai_generated', False)])
            ai_count = len([m for m in final_meals if m.get('recipe', {}).get('ai_generated', False) == True])
            self.logger.info(f"🎯 FINAL RESULT: {db_count} database meals, {ai_count} AI meals out of {len(final_meals)} total")
            
            return final_meals
            
        except Exception as e:
            self.logger.error(f"Error generating hybrid meal plan: {e}", exc_info=True)
            # If AI-only mode fails, generate fallback meals marked as AI (don't fall back to database)
            self.logger.warning("⚠️ AI-only generation failed, using fallback recipes marked as AI")
            fallback_meals = []
            existing_names = []
            if existing_meals:
                existing_names.extend([meal.get('meal_name', '') for meal in existing_meals])
            for meal_type in meal_types:
                fb = fallback_generator.generate_unique_recipe(
                    meal_type, target_calories, 'International', existing_names
                )
                if 'recipe' not in fb:
                    fb['recipe'] = {}
                fb['recipe']['ai_generated'] = True
                fb['recipe']['database_source'] = False
                fb['ai_generated'] = True
                fallback_meals.append(fb)
                existing_names.append(fb.get('meal_name', ''))
            return fallback_meals
    
    def _get_database_recipes(
        self, 
        db: Session, 
        user_preferences: Dict[str, Any], 
        target_calories: int,
        meal_types: List[str],
        existing_meals: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get 50% of meals from database recipes
        """
        try:
            # Calculate how many meals to get from database (50%)
            total_meals = len(meal_types)
            # CRITICAL FIX: Get exactly 50% from database, not "up to 50%"
            database_count = total_meals // 2  # Exactly 50%, not "at least 1, up to 50%"
            
            # Get existing meal names to avoid duplicates
            existing_names = []
            if existing_meals:
                existing_names = [meal.get('meal_name', '') for meal in existing_meals]
            # ROOT CAUSE FIX: Get recently used names (last 30 days / 1 month) for this user to prevent duplicates across meal plans
            # This ensures users don't get the same recipes across meal plans for at least a month
            # Can be reset using scripts/reset_meal_plan_memory.py
            # ROOT CAUSE FIX: Check last 30 days (1 month) to prevent duplicates across meal plans
            recent_names = self._get_recently_used_names(db, user_preferences, days=30)
            if recent_names:
                existing_names.extend(recent_names)
            
            # Get a pool of database recipes first
            query = db.query(Recipe).filter(Recipe.is_active == True)
            
            # Apply dietary preferences - handle JSON column safely
            dietary_prefs = user_preferences.get('dietary_preferences', [])
            if dietary_prefs:
                # For JSON columns, use a safer approach that works across databases
                # We'll filter in Python after fetching, or use database-specific JSON functions
                # For now, skip strict filtering to avoid errors - filter later in Python if needed
                pass  # TODO: Implement database-agnostic JSON array filtering
            
            # Filter out allergies - recipes should NOT contain allergens
            allergies = user_preferences.get('allergies', [])
            if allergies:
                # For now, skip strict allergy filtering via dietary_tags to avoid errors
                # The dietary tag inference will handle this in _recipe_to_meal_format
                pass  # TODO: Implement database-agnostic JSON array filtering
            
            # Get a broad pool and filter intelligently per meal type
            # CRITICAL FIX: Use actual database meal types (breakfast, lunch, dinner, snack)
            # not the old mapping (side_dish, main_course)
            needed_db_types = ['breakfast', 'lunch', 'dinner', 'snack']
            all_recipes = query.filter(Recipe.meal_type.in_(needed_db_types)).order_by(func.random()).limit(100).all()
            self.logger.info(f"🔍 DATABASE POOL: Found {len(all_recipes)} recipes to choose from")
            
            database_meals = []
            
            # Map system meal types to database meal types
            # CRITICAL FIX: Database uses same meal types as system (breakfast, lunch, dinner, snack)
            meal_type_mapping = {
                'breakfast': 'breakfast',
                'lunch': 'lunch',
                'dinner': 'dinner',
                'snack': 'snack'
            }
            
            # Assign database recipes to meal types intelligently
            for i, meal_type in enumerate(meal_types[:database_count]):
                if not all_recipes:
                    break
                
                # Get the corresponding database meal type
                db_meal_type = meal_type_mapping.get(meal_type, meal_type)
                self.logger.info(f"🔍 Looking for {db_meal_type} recipes for {meal_type}")
                    
                # Find the best recipe for this meal type by calorie proximity to target
                best_recipe = None
                best_score = None
                for recipe in all_recipes:
                    if recipe.title in existing_names:
                        continue
                    if recipe.meal_type != db_meal_type:
                        continue
                    if meal_type in ("breakfast", "lunch", "dinner") and self._is_beverage_or_sauce(recipe):
                        continue
                    if not self._is_appropriate_for_meal_type(recipe, meal_type):
                        continue
                    calories = (recipe.per_serving_calories or 0)
                    # Penalize undershooting more than overshooting so we aim closer to or above target
                    score = (target_calories - calories) * 2 if calories < target_calories else (calories - target_calories)
                    if best_score is None or score < best_score:
                        best_score = score
                    best_recipe = recipe
                
                # If no exact match, try the broader category
                if not best_recipe:
                    for recipe in all_recipes:
                        if recipe.title in existing_names:
                            continue
                        if meal_type in ("breakfast", "lunch", "dinner") and self._is_beverage_or_sauce(recipe):
                            continue
                        if not self._is_appropriate_for_meal_type(recipe, meal_type):
                            continue
                        # choose the closest calorie match with undershoot penalty
                        calories = (recipe.per_serving_calories or 0)
                        score = (target_calories - calories) * 2 if calories < target_calories else (calories - target_calories)
                        cur_best = (best_recipe.per_serving_calories or 0) if best_recipe else None
                        cur_score = (target_calories - cur_best) * 2 if (cur_best is not None and cur_best < target_calories) else (cur_best - target_calories if cur_best is not None else None)
                        if best_recipe is None or score < (cur_score if cur_score is not None else float('inf')):
                            best_recipe = recipe
                
                if best_recipe:
                    meal_data = self._recipe_to_meal_format(best_recipe, target_calories, meal_type)
                    if meal_data is None:
                        # Recipe had no valid calories, skip and use fallback
                        self.logger.warning(f"❌ DATABASE MEAL: Recipe '{best_recipe.title}' has no valid calories, using fallback")
                        # Remove invalid recipe from pool and try to find another
                        all_recipes = [r for r in all_recipes if r.title != best_recipe.title]
                        # Continue to fallback logic below
                        best_recipe = None
                    else:
                        database_meals.append(meal_data)
                        existing_names.append(best_recipe.title)
                        self.logger.info(f"✅ DATABASE MEAL: {best_recipe.title} ({best_recipe.meal_type}) -> {meal_type}")
                        self.logger.info(f"   📊 SERVING: {best_recipe.per_serving_calories} cal/serving, {best_recipe.servings} servings = {meal_data['calories']} cal")
                        # Remove used recipe from pool
                        all_recipes = [r for r in all_recipes if r.title != best_recipe.title]
                
                # If no recipe was found or recipe was skipped, use fallback
                if not best_recipe:
                    # CRITICAL FIX: Fill missing slots with fallback meals marked as database to maintain 50/50 split
                    self.logger.warning(f"❌ DATABASE MEAL: No suitable recipe found for {meal_type}, using fallback")
                    fallback_meal = fallback_generator.generate_unique_recipe(
                        meal_type, target_calories, 'International', existing_names
                    )
                    # Mark fallback as database source to maintain 50/50 split
                    if 'recipe' not in fallback_meal:
                        fallback_meal['recipe'] = {}
                    fallback_meal['recipe']['ai_generated'] = False
                    fallback_meal['recipe']['database_source'] = True
                    fallback_meal['ai_generated'] = False
                    database_meals.append(fallback_meal)
                    existing_names.append(fallback_meal.get('meal_name', ''))
                    self.logger.info(f"✅ FALLBACK DB MEAL: {fallback_meal.get('meal_name')} for {meal_type}")
            
            # CRITICAL FIX: Ensure we have exactly database_count meals
            if len(database_meals) < database_count:
                self.logger.warning(f"⚠️ Only got {len(database_meals)}/{database_count} database meals, filling remaining slots")
                remaining_count = database_count - len(database_meals)
                for i in range(remaining_count):
                    # Get remaining meal types
                    used_indices = len(database_meals) - remaining_count + i
                    if used_indices < len(meal_types):
                        mt = meal_types[used_indices]
                    else:
                        # Fallback to cycling through base types
                        base_types = ['breakfast', 'lunch', 'dinner', 'snack']
                        mt = base_types[i % len(base_types)]
                    fallback_meal = fallback_generator.generate_unique_recipe(
                        mt, target_calories, 'International', existing_names
                    )
                    if 'recipe' not in fallback_meal:
                        fallback_meal['recipe'] = {}
                    fallback_meal['recipe']['ai_generated'] = False
                    fallback_meal['recipe']['database_source'] = True
                    fallback_meal['ai_generated'] = False
                    database_meals.append(fallback_meal)
                    existing_names.append(fallback_meal.get('meal_name', ''))
                    self.logger.info(f"✅ FILLED DB SLOT {i+1}/{remaining_count}: {fallback_meal.get('meal_name')} for {mt}")
            
            self.logger.info(f"📊 DATABASE RESULT: {len(database_meals)}/{database_count} meals from database")
            return database_meals
            
        except Exception as e:
            self.logger.error(f"Error getting database recipes: {e}")
            return []

    def _get_recently_used_names(self, db: Session, user_preferences: Dict[str, Any], days: int = 30) -> List[str]:
        """Fetch meal names used by the user in the last N days to avoid repeats."""
        try:
            user_id = None
            # user_preferences may contain user_id or nested context
            if isinstance(user_preferences, dict):
                user_id = user_preferences.get('user_id') or user_preferences.get('id')
                if not user_id:
                    # Some callers might pass preferences ORM; ignore if not dict
                    pass
            if not user_id:
                return []
            from datetime import date, timedelta
            since = date.today() - timedelta(days=days)
            plan_ids = [p.id for p in db.query(MealPlan).filter(and_(MealPlan.user_id == user_id, MealPlan.start_date >= since)).all()]
            if not plan_ids:
                return []
            meals = db.query(MealPlanMeal).filter(MealPlanMeal.meal_plan_id.in_(plan_ids)).all()
            names = [m.meal_name for m in meals if getattr(m, 'meal_name', None)]
            unique = list({n: True for n in names}.keys())
            if unique:
                self.logger.info(f"🧠 RECENT MEMORY: Excluding {len(unique)} recent meals from selection")
            return unique
        except Exception:
            return []
    
    def _analyze_meal_patterns(self, meals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze patterns from database meals to guide AI generation
        """
        if not meals:
            return {
                'cuisines': ['International'],
                'cooking_methods': ['simmer'],
                'ingredient_themes': ['vegetables', 'grains'],
                'flavor_profiles': ['balanced'],
                'dietary_tags': ['balanced']
            }
        
        # Extract patterns
        cuisines = [meal.get('cuisine', 'International') for meal in meals]
        cooking_methods = []
        ingredient_themes = []
        dietary_tags = []
        
        for meal in meals:
            recipe = meal.get('recipe', {})
            if recipe:
                # Extract cooking methods from instructions
                instructions = recipe.get('instructions', [])
                for instruction in instructions:
                    desc = instruction.get('description', '').lower()
                    if 'bake' in desc or 'roast' in desc:
                        cooking_methods.append('baking')
                    elif 'fry' in desc or 'sauté' in desc:
                        cooking_methods.append('frying')
                    elif 'grill' in desc:
                        cooking_methods.append('grilling')
                    elif 'simmer' in desc or 'boil' in desc:
                        cooking_methods.append('simmering')
                
                # Extract ingredient themes
                ingredients = recipe.get('ingredients', [])
                for ingredient in ingredients:
                    name = ingredient.get('name', '').lower()
                    if any(veg in name for veg in ['vegetable', 'tomato', 'onion', 'pepper']):
                        ingredient_themes.append('vegetables')
                    elif any(protein in name for protein in ['chicken', 'beef', 'fish', 'tofu']):
                        ingredient_themes.append('proteins')
                    elif any(grain in name for grain in ['rice', 'pasta', 'quinoa', 'bread']):
                        ingredient_themes.append('grains')
                
                # Extract dietary tags
                tags = recipe.get('dietary_tags', [])
                dietary_tags.extend(tags)
        
        # Get most common patterns
        cuisine_counts = {}
        for cuisine in cuisines:
            cuisine_counts[cuisine] = cuisine_counts.get(cuisine, 0) + 1
        
        most_common_cuisine = max(cuisine_counts.items(), key=lambda x: x[1])[0] if cuisine_counts else 'International'
        
        return {
            'cuisines': [most_common_cuisine],
            'cooking_methods': list(set(cooking_methods)) or ['simmering'],
            'ingredient_themes': list(set(ingredient_themes)) or ['vegetables'],
            'flavor_profiles': ['balanced'],
            'dietary_tags': list(set(dietary_tags)) or ['balanced']
        }
    
    def _generate_ai_complementary_recipes(
        self,
        db: Session,
        pattern_analysis: Dict[str, Any],
        user_preferences: Dict[str, Any],
        target_calories: int,
        meal_types: List[str],
        existing_meals: List[Dict[str, Any]] = None,
        database_meals: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate AI recipes that complement the database meals
        """
        try:
            # Calculate how many meals to generate with AI (50% of total)
            total_meals = len(meal_types)
            target_ai_count = total_meals // 2  # Exactly 50% should be AI
            database_count = len(database_meals) if database_meals else 0
            
            # CRITICAL FIX: Ensure we generate exactly 50% AI meals, even if database has more
            # The goal is 50/50 split, so we need exactly target_ai_count AI meals
            ai_count = target_ai_count
            
            # If database returned more than 50%, we'll balance it in combine_and_balance
            # But we still need to generate target_ai_count AI meals for 50/50 split
            self.logger.info(f"🎯 AI Generation Plan: Need {ai_count} AI meals out of {total_meals} total (DB has {database_count})")
            
            # Get existing meal names to avoid duplicates
            existing_names = []
            if existing_meals:
                existing_names.extend([meal.get('meal_name', '') for meal in existing_meals])
            if database_meals:
                existing_names.extend([meal.get('meal_name', '') for meal in database_meals])
            # Include recently used names across weeks (reduced to 7 days to allow more variety)
            # ROOT CAUSE FIX: Check last 30 days (1 month) to prevent duplicates across meal plans
            recent_names = self._get_recently_used_names(db, user_preferences, days=30)
            if recent_names:
                existing_names.extend(recent_names)
            
            ai_meals = []
            # CRITICAL FIX: Always generate exactly target_ai_count AI meals regardless of DB count
            # The combine_and_balance function will handle the final distribution
            ai_count = target_ai_count
            
            # Get meal types for AI generation
            # CRITICAL FIX: Distribute AI meals evenly across base meal types, not just consecutive slots
            base_meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
            
            # Count occurrences of each base type in meal_types list
            meal_type_counts = {}
            for mt in meal_types:
                if mt in base_meal_types:
                    meal_type_counts[mt] = meal_type_counts.get(mt, 0) + 1
            
            # Calculate how many AI meals per base type (roughly half of each)
            ai_meal_type_counts = {}
            total_ai_needed = ai_count
            for mt in base_meal_types:
                total_for_type = meal_type_counts.get(mt, 0)
                # Roughly half of each type should be AI (round up for odd numbers)
                ai_needed_for_type = (total_for_type + 1) // 2
                ai_meal_type_counts[mt] = min(ai_needed_for_type, total_ai_needed)
                total_ai_needed = max(0, total_ai_needed - ai_needed_for_type)
            
            # If we still need more AI meals, distribute evenly
            remaining_ai = ai_count - sum(ai_meal_type_counts.values())
            if remaining_ai > 0:
                # Distribute remaining evenly across types
                for i in range(remaining_ai):
                    mt = base_meal_types[i % len(base_meal_types)]
                    ai_meal_type_counts[mt] = ai_meal_type_counts.get(mt, 0) + 1
            
            # Build list of meal types for AI generation - alternate between types
            ai_meal_types = []
            while len(ai_meal_types) < ai_count:
                for mt in base_meal_types:
                    if len(ai_meal_types) >= ai_count:
                        break
                    count_needed = ai_meal_type_counts.get(mt, 0)
                    count_added = sum(1 for amt in ai_meal_types if amt == mt)
                    if count_added < count_needed:
                        ai_meal_types.append(mt)
            
            # Trim to exact count needed
            ai_meal_types = ai_meal_types[:ai_count]
            
            self.logger.info(f"🎯 Generating {len(ai_meal_types)} AI meals (target: {ai_count}) for types: {ai_meal_types[:10]}...")
            
            for meal_type in ai_meal_types:
                try:
                    # Create AI prompt based on pattern analysis
                    # Include both existing meals and database meals to avoid duplicates
                    all_existing_meals = (existing_meals or []) + (database_meals or [])
                    # Also add recent names as lightweight meal entries for duplicate avoidance
                    for nm in set(recent_names or []):
                        all_existing_meals.append({"meal_name": nm})
                    ai_meal_data = {
                        'meal_type': meal_type,
                        'target_calories': target_calories,
                        'target_cuisine': pattern_analysis['cuisines'][0],
                        'user_preferences': user_preferences,
                        'existing_meals': all_existing_meals,
                        'pattern_analysis': pattern_analysis
                    }
                    
                    # Try AI generation first
                    ai_meal = None
                    try:
                        # Check if OpenAI client is available
                        if hasattr(self.nutrition_ai, 'openai_client') and self.nutrition_ai.openai_client:
                            # Use sequential RAG method (task.md compliant)
                            ai_meal = self.nutrition_ai._generate_single_meal_with_sequential_rag(ai_meal_data, db)
                            self.logger.info(f"🔵 Sequential RAG generation attempted for {meal_type}, result: {ai_meal.get('meal_name') if ai_meal else 'None'}")
                        else:
                            self.logger.warning(f"⚠️ OpenAI client not available, using fallback for {meal_type}")
                    except Exception as ai_error:
                        self.logger.warning(f"⚠️ AI generation failed for {meal_type}: {ai_error}")
                        ai_meal = None
                    
                    if ai_meal and ai_meal.get('meal_name') and ai_meal.get('meal_name') not in existing_names:
                        # Ensure AI flag is set
                        if 'recipe' not in ai_meal:
                            ai_meal['recipe'] = {}
                        ai_meal['recipe']['ai_generated'] = True
                        ai_meal['recipe']['database_source'] = False
                        # Also set top-level flag
                        ai_meal['ai_generated'] = True
                        ai_meals.append(ai_meal)
                        existing_names.append(ai_meal.get('meal_name', ''))
                        self.logger.info(f"✅ AI meal generated: {ai_meal.get('meal_name')}")
                    else:
                        # Fallback to fallback system - still mark as AI for 50/50 split
                        self.logger.info(f"🔄 Using fallback generator for {meal_type} (AI failed or returned duplicate)")
                        fallback_meal = fallback_generator.generate_unique_recipe(
                            meal_type, target_calories, pattern_analysis['cuisines'][0], existing_names
                        )
                        # Mark fallback as AI to maintain 50/50 split
                        if 'recipe' not in fallback_meal:
                            fallback_meal['recipe'] = {}
                        fallback_meal['recipe']['ai_generated'] = True
                        fallback_meal['recipe']['database_source'] = False
                        fallback_meal['ai_generated'] = True  # Top-level flag
                        ai_meals.append(fallback_meal)
                        existing_names.append(fallback_meal.get('meal_name', ''))
                        self.logger.info(f"✅ Fallback AI meal generated: {fallback_meal.get('meal_name')}")
                        
                except Exception as e:
                    self.logger.warning(f"AI generation failed: {e}")
                    # Use fallback system - mark as AI for 50/50 split
                    fallback_meal = fallback_generator.generate_unique_recipe(
                        meal_type, target_calories, pattern_analysis['cuisines'][0], existing_names
                    )
                    # Mark fallback as AI to maintain 50/50 split
                    if 'recipe' not in fallback_meal:
                        fallback_meal['recipe'] = {}
                    fallback_meal['recipe']['ai_generated'] = True
                    fallback_meal['recipe']['database_source'] = False
                    ai_meals.append(fallback_meal)
                    existing_names.append(fallback_meal.get('meal_name', ''))
                    self.logger.info(f"✅ Fallback AI meal (error recovery): {fallback_meal.get('meal_name')}")
            
            # Ensure we have exactly ai_count items; if short, fill with fallback marked as AI
            if len(ai_meals) < ai_count:
                # Get remaining meal types to fill
                remaining_count = ai_count - len(ai_meals)
                
                # Get remaining types from ai_meal_types that haven't been used yet
                used_types_in_ai = [m.get('meal_type') for m in ai_meals if m.get('meal_type')]
                remaining_from_ai = [mt for mt in ai_meal_types if mt not in used_types_in_ai]
                
                # If not enough from ai_meal_types, get unused types from all meal_types
                if len(remaining_from_ai) < remaining_count:
                    used_types_all = set([m.get('meal_type') for m in database_meals + ai_meals if m.get('meal_type')])
                    remaining_from_all = [mt for mt in meal_types if mt not in used_types_all]
                    remaining_types = (remaining_from_ai + remaining_from_all)[:remaining_count]
                else:
                    remaining_types = remaining_from_ai[:remaining_count]
                
                # Generate fallback meals for remaining types
                for mt in remaining_types:
                    fb = fallback_generator.generate_unique_recipe(
                        mt, target_calories, pattern_analysis['cuisines'][0], existing_names
                    )
                    # Mark as AI to reflect intention of hybrid balance
                    if 'recipe' in fb and isinstance(fb['recipe'], dict):
                        fb['recipe']['ai_generated'] = True
                    else:
                        fb.setdefault('recipe', {})
                        fb['recipe']['ai_generated'] = True
                    ai_meals.append(fb)
                    existing_names.append(fb.get('meal_name',''))

            return ai_meals
            
        except Exception as e:
            self.logger.error(f"Error generating AI complementary recipes: {e}")
            return []
    
    def _generate_all_ai_meals(
        self,
        db: Session,
        pattern_analysis: Dict[str, Any],
        user_preferences: Dict[str, Any],
        target_calories: int,
        meal_types: List[str],
        existing_meals: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate ALL meals with AI (AI-only mode - no database recipes)
        """
        try:
            total_meals = len(meal_types)
            self.logger.info(f"🤖 AI-ONLY MODE: Generating {total_meals} meals with AI (no database recipes)")
            
            # Get existing meal names to avoid duplicates
            existing_names = []
            if existing_meals:
                existing_names.extend([meal.get('meal_name', '') for meal in existing_meals])
            # ROOT CAUSE FIX: Check last 30 days (1 month) to prevent duplicates across meal plans
            recent_names = self._get_recently_used_names(db, user_preferences, days=30)
            if recent_names:
                existing_names.extend(recent_names)
            
            # OPTIMIZATION: Generate meals in parallel for faster processing (maintains quality)
            def _generate_single_meal(meal_type: str, existing_names_lock=None) -> Dict[str, Any]:
                """Helper function to generate a single meal (used for parallel execution)"""
                try:
                    # Create AI prompt
                    all_existing_meals = (existing_meals or []).copy()
                    for nm in set(recent_names or []):
                        all_existing_meals.append({"meal_name": nm})
                    
                    ai_meal_data = {
                        'meal_type': meal_type,
                        'target_calories': target_calories,
                        'target_cuisine': pattern_analysis.get('cuisines', ['International'])[0] if pattern_analysis.get('cuisines') else 'International',
                        'user_preferences': user_preferences,
                        'existing_meals': all_existing_meals,
                        'pattern_analysis': pattern_analysis
                    }
                    
                    # Try AI generation first using Sequential RAG (task.md compliant)
                    ai_meal = None
                    try:
                        if hasattr(self.nutrition_ai, 'openai_client') and self.nutrition_ai.openai_client:
                            # Use sequential RAG method (follows task.md requirements)
                            ai_meal = self.nutrition_ai._generate_single_meal_with_sequential_rag(ai_meal_data, db)
                            self.logger.info(f"🔵 Sequential RAG generation attempted for {meal_type}, result: {ai_meal.get('meal_name') if ai_meal else 'None'}")
                        else:
                            self.logger.warning(f"⚠️ OpenAI client not available, using fallback for {meal_type}")
                    except Exception as ai_error:
                        self.logger.warning(f"⚠️ Sequential RAG generation failed for {meal_type}: {ai_error}")
                        # Fallback to fast generation if sequential fails
                        try:
                            ai_meal = self.nutrition_ai._generate_single_meal_fast(ai_meal_data)
                            self.logger.info(f"🔄 Fallback to fast generation for {meal_type}")
                        except Exception:
                            ai_meal = None
                    
                    # Thread-safe check for duplicates
                    current_existing = list(existing_names) if existing_names_lock is None else existing_names.copy()
                    
                    if ai_meal and ai_meal.get('meal_name') and ai_meal.get('meal_name') not in current_existing:
                        # Ensure AI flag is set
                        if 'recipe' not in ai_meal:
                            ai_meal['recipe'] = {}
                        ai_meal['recipe']['ai_generated'] = True
                        ai_meal['recipe']['database_source'] = False
                        ai_meal['ai_generated'] = True
                        ai_meal['meal_type'] = meal_type  # Ensure meal_type is set
                        self.logger.info(f"✅ AI meal generated: {ai_meal.get('meal_name')}")
                        return ai_meal
                    else:
                        # Fallback to fallback system - mark as AI
                        self.logger.info(f"🔄 Using fallback generator for {meal_type} (AI failed or returned duplicate)")
                        fallback_meal = fallback_generator.generate_unique_recipe(
                            meal_type, target_calories, pattern_analysis.get('cuisines', ['International'])[0] if pattern_analysis.get('cuisines') else 'International', current_existing
                        )
                        if 'recipe' not in fallback_meal:
                            fallback_meal['recipe'] = {}
                        fallback_meal['recipe']['ai_generated'] = True
                        fallback_meal['recipe']['database_source'] = False
                        fallback_meal['ai_generated'] = True
                        fallback_meal['meal_type'] = meal_type  # Ensure meal_type is set
                        self.logger.info(f"✅ Fallback AI meal generated: {fallback_meal.get('meal_name')}")
                        return fallback_meal
                        
                except Exception as e:
                    self.logger.warning(f"AI generation failed for {meal_type}: {e}")
                    # Use fallback system - mark as AI
                    current_existing = list(existing_names) if existing_names_lock is None else existing_names.copy()
                    fallback_meal = fallback_generator.generate_unique_recipe(
                        meal_type, target_calories, pattern_analysis.get('cuisines', ['International'])[0] if pattern_analysis.get('cuisines') else 'International', current_existing
                    )
                    if 'recipe' not in fallback_meal:
                        fallback_meal['recipe'] = {}
                    fallback_meal['recipe']['ai_generated'] = True
                    fallback_meal['recipe']['database_source'] = False
                    fallback_meal['ai_generated'] = True
                    fallback_meal['meal_type'] = meal_type  # Ensure meal_type is set
                    self.logger.info(f"✅ Fallback AI meal (error recovery): {fallback_meal.get('meal_name')}")
                    return fallback_meal
            
            # OPTIMIZATION: Use ThreadPoolExecutor for parallel generation (max 8 workers to avoid rate limits)
            # This maintains the same quality but speeds up generation significantly
            ai_meals = []
            max_workers = min(8, len(meal_types))  # Limit workers to avoid API rate limits
            
            if max_workers > 1 and hasattr(self.nutrition_ai, 'openai_client') and self.nutrition_ai.openai_client:
                # Parallel generation for faster processing (same quality)
                self.logger.info(f"🚀 OPTIMIZATION: Generating {total_meals} meals in parallel ({max_workers} workers)")
                with ThreadPoolExecutor(max_workers=max_workers) as thread_pool:
                    # Submit all tasks
                    future_to_meal_type = {thread_pool.submit(_generate_single_meal, mt): mt for mt in meal_types}
                    
                    # Collect results as they complete (preserve order if needed)
                    results_by_type = {}
                    for future in as_completed(future_to_meal_type):
                        meal_type = future_to_meal_type[future]
                        try:
                            result = future.result()
                            if result:
                                results_by_type[meal_type] = result
                                # Thread-safe update to existing_names
                                result_name = result.get('meal_name', '')
                                if result_name and result_name not in existing_names:
                                    existing_names.append(result_name)
                        except Exception as e:
                            self.logger.error(f"❌ Parallel generation failed for {meal_type}: {e}")
                            # Generate fallback on error
                            result = _generate_single_meal(meal_type)
                            if result:
                                results_by_type[meal_type] = result
                    
                    # Reconstruct meals in original order
                    for meal_type in meal_types:
                        if meal_type in results_by_type:
                            ai_meals.append(results_by_type[meal_type])
                        else:
                            # Fallback if missing
                            result = _generate_single_meal(meal_type)
                            if result:
                                ai_meals.append(result)
            else:
                # Fallback to sequential generation if parallel is not available
                self.logger.info(f"🔄 Using sequential generation (parallel not available)")
                for meal_type in meal_types:
                    result = _generate_single_meal(meal_type)
                    if result:
                        ai_meals.append(result)
                        existing_names.append(result.get('meal_name', ''))
            
            # Ensure we have exactly the requested number of meals
            if len(ai_meals) < total_meals:
                remaining_count = total_meals - len(ai_meals)
                self.logger.warning(f"⚠️ Only generated {len(ai_meals)} AI meals, need {total_meals}. Generating {remaining_count} more fallback meals.")
                # Get remaining meal types
                used_types = [m.get('meal_type') for m in ai_meals]
                remaining_types = [mt for mt in meal_types if mt not in used_types or used_types.count(mt) < meal_types.count(mt)]
                remaining_types = remaining_types[:remaining_count]
                
                for mt in remaining_types:
                    fb = fallback_generator.generate_unique_recipe(
                        mt, target_calories, pattern_analysis.get('cuisines', ['International'])[0] if pattern_analysis.get('cuisines') else 'International', existing_names
                    )
                    if 'recipe' not in fb:
                        fb['recipe'] = {}
                    fb['recipe']['ai_generated'] = True
                    fb['recipe']['database_source'] = False
                    fb['ai_generated'] = True
                    ai_meals.append(fb)
                    existing_names.append(fb.get('meal_name',''))
            
            self.logger.info(f"✅ AI-ONLY MODE: Generated {len(ai_meals)} AI meals (expected {total_meals})")
            return ai_meals[:total_meals]  # Trim to exact count if needed
            
        except Exception as e:
            self.logger.error(f"Error generating all AI meals: {e}", exc_info=True)
            return []
    
    def _combine_and_balance_meals(
        self,
        database_meals: List[Dict[str, Any]],
        ai_meals: List[Dict[str, Any]],
        target_calories: int,
        meal_types: List[str],
        db: Session = None,
        user_preferences: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Combine database and AI meals into a balanced meal plan
        """
        # CRITICAL: Log counts before combining
        self.logger.info(f"📊 BEFORE COMBINE: {len(database_meals)} DB meals, {len(ai_meals)} AI meals, need {len(meal_types)} total")
        
        # Ensure AI meals are properly marked
        for ai_meal in ai_meals:
            if 'recipe' not in ai_meal:
                ai_meal['recipe'] = {}
            if 'ai_generated' not in ai_meal.get('recipe', {}) or ai_meal.get('recipe', {}).get('ai_generated') is None:
                ai_meal['recipe']['ai_generated'] = True
                ai_meal['recipe']['database_source'] = False
            if 'ai_generated' not in ai_meal:
                ai_meal['ai_generated'] = True
        
        # Ensure database meals are properly marked (explicitly False)
        for db_meal in database_meals:
            if 'recipe' not in db_meal:
                db_meal['recipe'] = {}
            # Explicitly set to False (not just missing)
            db_meal['recipe']['ai_generated'] = False
            db_meal['recipe']['database_source'] = True
            db_meal['ai_generated'] = False
        
        # CRITICAL FIX: Detect AI-only mode (no database meals)
        is_ai_only_mode = len(database_meals) == 0
        
        if not is_ai_only_mode:
            # Only apply 50/50 split logic if we have database meals
            # CRITICAL FIX: If database returned more than 50%, trim it to exactly 50%
            target_ai = len(meal_types) // 2
            target_db = len(meal_types) - target_ai  # Remaining should be DB
            
            if len(database_meals) > target_db:
                self.logger.warning(f"⚠️ Database returned {len(database_meals)} meals but we need only {target_db} - trimming")
                database_meals = database_meals[:target_db]
        
        all_meals = database_meals + ai_meals
        
        # Ensure we have EXACTLY len(meal_types) meals - fill any missing slots
        if len(all_meals) < len(meal_types):
            self.logger.warning(f"⚠️ Only have {len(all_meals)} meals but need {len(meal_types)} - filling missing slots")
            remaining_types = meal_types[len(all_meals):]
            used_names_in_plan = [meal.get('meal_name', '') for meal in all_meals]
            
            if is_ai_only_mode:
                # AI-ONLY MODE: All fill meals should be AI
                self.logger.info(f"🤖 AI-ONLY MODE: Filling {len(remaining_types)} slots with AI meals")
                for i, meal_type in enumerate(remaining_types):
                    fallback_meal = fallback_generator.generate_unique_recipe(
                        meal_type, target_calories, 'International', used_names_in_plan
                    )
                    fallback_meal.setdefault('recipe', {})
                    fallback_meal['recipe']['ai_generated'] = True
                    fallback_meal['recipe']['database_source'] = False
                    fallback_meal['ai_generated'] = True
                    all_meals.append(fallback_meal)
                    used_names_in_plan.append(fallback_meal.get('meal_name', ''))
                    self.logger.info(f"✅ Filled slot {i+1}/{len(remaining_types)} with {meal_type}: {fallback_meal.get('meal_name')} (AI)")
            else:
                # 50/50 MODE: Balance AI/database
                ai_count_so_far = sum(1 for m in all_meals if m.get('recipe',{}).get('ai_generated') == True)
                db_count_so_far = len(all_meals) - ai_count_so_far
                # CRITICAL FIX: Recalculate target for remaining slots to maintain 50/50 split
                remaining_count = len(remaining_types)
                total_needed = len(meal_types)
                # Calculate how many AI and DB we need total
                target_ai_total = total_needed // 2
                target_db_total = total_needed - target_ai_total
                # Calculate how many more we need of each
                ai_needed = max(0, target_ai_total - ai_count_so_far)
                db_needed = max(0, target_db_total - db_count_so_far)
                self.logger.info(f"📊 FILL STATUS: {ai_count_so_far} AI, {db_count_so_far} DB, need {ai_needed} more AI, {db_needed} more DB out of {remaining_count} slots")
                
                for i, meal_type in enumerate(remaining_types):
                    fallback_meal = fallback_generator.generate_unique_recipe(
                        meal_type, target_calories, 'International', used_names_in_plan
                    )
                    # Balance AI/database to maintain 50/50 split - prioritize whichever we need more
                    if ai_needed > 0 and (db_needed == 0 or ai_needed >= db_needed):
                        fallback_meal.setdefault('recipe', {})
                        fallback_meal['recipe']['ai_generated'] = True
                        fallback_meal['recipe']['database_source'] = False
                        ai_count_so_far += 1
                        ai_needed -= 1
                    elif db_needed > 0:
                        fallback_meal.setdefault('recipe', {})
                        fallback_meal['recipe']['ai_generated'] = False
                        fallback_meal['recipe']['database_source'] = True
                        db_count_so_far += 1
                        db_needed -= 1
                    else:
                        # Default to AI if neither is needed (maintain AI-first approach)
                        fallback_meal.setdefault('recipe', {})
                        fallback_meal['recipe']['ai_generated'] = True
                        fallback_meal['recipe']['database_source'] = False
                        ai_count_so_far += 1
                    all_meals.append(fallback_meal)
                    used_names_in_plan.append(fallback_meal.get('meal_name', ''))
                    self.logger.info(f"✅ Filled slot {i+1}/{len(remaining_types)} with {meal_type}: {fallback_meal.get('meal_name')} ({'AI' if fallback_meal.get('recipe',{}).get('ai_generated') else 'DB'})")
        
        # CRITICAL FIX: Detect duplicates by both name AND ingredients AND instructions similarity
        def _normalize_title(raw: str) -> str:
            import re
            txt = (raw or "").lower()
            drop_words = {
                'artisan','gourmet','delight','special','deluxe','power','fusion','morning','evening',
                'bowl','plate','wrap','skillet','style','inspired','authentic','classic','chef','homestyle'
            }
            tokens = re.sub(r"[^a-z0-9]+"," ", txt).split()
            tokens = [t for t in tokens if t and t not in drop_words]
            core = sorted(set(tokens))
            return " ".join(core).strip()
        
        def _get_ingredient_signature(meal: Dict[str, Any]) -> str:
            """Create a normalized signature from ingredients to detect duplicates"""
            recipe = meal.get('recipe', {}) or {}
            ingredients = recipe.get('ingredients', []) or meal.get('ingredients', [])
            if not ingredients:
                return ""
            
            # Normalize ingredient names: lowercase, strip, sort
            ing_names = []
            for ing in ingredients:
                if isinstance(ing, dict):
                    name = str(ing.get('name', '')).lower().strip()
                else:
                    name = str(ing).lower().strip()
                if name and name not in ['', 'none', 'null']:
                    ing_names.append(name)
            
            # Sort and join to create a consistent signature
            return "|".join(sorted(set(ing_names)))
        
        def _get_instruction_signature(meal: Dict[str, Any]) -> str:
            """Create a normalized signature from instructions to detect duplicates"""
            recipe = meal.get('recipe', {}) or {}
            instructions = recipe.get('instructions', []) or meal.get('instructions', [])
            if not instructions:
                return ""
            
            # Extract instruction text, normalize, and create signature
            import re
            inst_texts = []
            for inst in instructions:
                if isinstance(inst, dict):
                    text = str(inst.get('description', '') or inst.get('text', '') or '').lower()
                else:
                    text = str(inst).lower()
                if text:
                    # Remove extra whitespace and punctuation
                    text = re.sub(r'[^\w\s]+', ' ', text)
                    text = ' '.join(text.split())
                    if text and text not in ['', 'none', 'null']:
                        inst_texts.append(text[:100])  # Limit length to avoid huge signatures
            
            # Sort and join to create a consistent signature (use first 5 steps to avoid too much detail)
            return "|".join(sorted(set(inst_texts[:5])))

        used_names = set()
        used_core_titles = set()
        used_ingredient_signatures = set()
        used_instruction_signatures = set()
        unique_meals = []
        for m in all_meals:
            name = m.get('meal_name', '').strip()
            is_duplicate = False
            
            # Check for exact name match
            if name and name in used_names:
                is_duplicate = True
                self.logger.warning(f"⚠️ Duplicate name detected: {name}")
            
            # Check for normalized title match (catches "Artisan" vs "Gourmet" variants)
            if not is_duplicate and name:
                core_title = _normalize_title(name)
                if core_title and core_title in used_core_titles:
                    is_duplicate = True
                    self.logger.warning(f"⚠️ Duplicate normalized title detected: {name} (normalized: {core_title})")
            
            # Check for ingredient similarity (same recipe with different name)
            if not is_duplicate:
                ingredient_signature = _get_ingredient_signature(m)
                if ingredient_signature and ingredient_signature in used_ingredient_signatures:
                    is_duplicate = True
                    self.logger.warning(f"⚠️ Duplicate ingredients detected: {name} (same ingredients as another meal)")
            
            # Check for instruction similarity (same recipe with different name/title)
            if not is_duplicate:
                instruction_signature = _get_instruction_signature(m)
                if instruction_signature and instruction_signature in used_instruction_signatures:
                    is_duplicate = True
                    self.logger.warning(f"⚠️ Duplicate instructions detected: {name} (same instructions as another meal)")
            
            if not is_duplicate and name:
                unique_meals.append(m)
                used_names.add(name)
                ingredient_sig = _get_ingredient_signature(m)
                if ingredient_sig:
                    used_ingredient_signatures.add(ingredient_sig)
                instruction_sig = _get_instruction_signature(m)
                if instruction_sig:
                    used_instruction_signatures.add(instruction_sig)
                core = _normalize_title(name)
                if core:
                    used_core_titles.add(core)
            else:
                # Replace duplicate with a fallback unique meal
                # CRITICAL FIX: In AI-only mode, preserve AI flag from original meal
                replacement = fallback_generator.generate_unique_recipe(
                    m.get('meal_type','dinner'), target_calories, m.get('cuisine') or 'International', list(used_names)
                )
                replacement_name = replacement.get('meal_name','')
                replacement_ing_sig = _get_ingredient_signature(replacement)
                replacement_inst_sig = _get_instruction_signature(replacement)
                rep_core = _normalize_title(replacement_name)
                
                # CRITICAL: Preserve AI flag from original meal (maintain AI-only mode)
                if 'recipe' not in replacement:
                    replacement['recipe'] = {}
                if is_ai_only_mode:
                    # AI-ONLY MODE: Always mark replacement as AI
                    replacement['recipe']['ai_generated'] = True
                    replacement['recipe']['database_source'] = False
                    replacement['ai_generated'] = True
                else:
                    # 50/50 MODE: Preserve original meal's flag
                    original_is_ai = m.get('recipe', {}).get('ai_generated', False)
                    if original_is_ai:
                        replacement['recipe']['ai_generated'] = True
                        replacement['recipe']['database_source'] = False
                    else:
                        replacement['recipe']['ai_generated'] = False
                        replacement['recipe']['database_source'] = True
                
                # Ensure replacement is also unique (check all criteria)
                if (
                    replacement_name not in used_names and
                    (not rep_core or rep_core not in used_core_titles) and
                    (not replacement_ing_sig or replacement_ing_sig not in used_ingredient_signatures) and
                    (not replacement_inst_sig or replacement_inst_sig not in used_instruction_signatures)
                ):
                    unique_meals.append(replacement)
                    used_names.add(replacement_name)
                    if replacement_ing_sig:
                        used_ingredient_signatures.add(replacement_ing_sig)
                    if replacement_inst_sig:
                        used_instruction_signatures.add(replacement_inst_sig)
                    if rep_core:
                        used_core_titles.add(rep_core)
                    self.logger.info(f"✅ Replaced duplicate with unique meal: {replacement_name}")
                else:
                    # If replacement is also duplicate, try one more time with different parameters
                    replacement = fallback_generator.generate_unique_recipe(
                        m.get('meal_type','dinner'), target_calories * 1.2, 'International', list(used_names)
                    )
                    replacement_name = replacement.get('meal_name','')
                    # CRITICAL: Preserve AI flag for second attempt too
                    if 'recipe' not in replacement:
                        replacement['recipe'] = {}
                    if is_ai_only_mode:
                        replacement['recipe']['ai_generated'] = True
                        replacement['recipe']['database_source'] = False
                        replacement['ai_generated'] = True
                    else:
                        original_is_ai = m.get('recipe', {}).get('ai_generated', False)
                        if original_is_ai:
                            replacement['recipe']['ai_generated'] = True
                            replacement['recipe']['database_source'] = False
                        else:
                            replacement['recipe']['ai_generated'] = False
                            replacement['recipe']['database_source'] = True
                    if (replacement_name not in used_names and 
                        _normalize_title(replacement_name) not in used_core_titles and
                        _get_ingredient_signature(replacement) not in used_ingredient_signatures and
                        _get_instruction_signature(replacement) not in used_instruction_signatures):
                        unique_meals.append(replacement)
                        used_names.add(replacement_name)
                        rep_ing = _get_ingredient_signature(replacement)
                        rep_inst = _get_instruction_signature(replacement)
                        rep_c = _normalize_title(replacement_name)
                        if rep_ing:
                            used_ingredient_signatures.add(rep_ing)
                        if rep_inst:
                            used_instruction_signatures.add(rep_inst)
                        if rep_c:
                            used_core_titles.add(rep_c)
        
        all_meals = unique_meals

        # Reorder meals to exactly follow the requested meal_types sequence
        buckets: Dict[str, List[Dict[str, Any]]] = {}
        for m in all_meals:
            buckets.setdefault(m.get('meal_type','dinner'), []).append(m)
        ordered: List[Dict[str, Any]] = []
        for mt in meal_types:
            bucket = buckets.get(mt) or []
            pick = bucket.pop(0) if bucket else None
            if pick is None:
                # borrow from any non-empty bucket
                for k in list(buckets.keys()):
                    if buckets[k]:
                        pick = buckets[k].pop(0)
                        break
            if pick is None:
                # as last resort, generate a fallback meal of the right type
                # CRITICAL FIX: In AI-only mode, ALL fallbacks must be AI (not 50/50)
                used_names = [m.get('meal_name', '') for m in ordered]
                fallback = fallback_generator.generate_unique_recipe(
                    mt, target_calories, 'International', used_names
                )
                # In AI-only mode, always mark as AI
                if 'recipe' not in fallback:
                    fallback['recipe'] = {}
                if is_ai_only_mode:
                    # AI-ONLY MODE: Always mark fallbacks as AI
                    fallback['recipe']['ai_generated'] = True
                    fallback['recipe']['database_source'] = False
                    fallback['ai_generated'] = True
                else:
                    # 50/50 MODE: Check current AI/DB balance to maintain 50/50 split
                    current_ai_count = sum(1 for m in ordered if m.get('recipe', {}).get('ai_generated'))
                    target_ai = len(meal_types) // 2
                    if current_ai_count < target_ai:
                        fallback['recipe']['ai_generated'] = True
                        fallback['recipe']['database_source'] = False
                    else:
                        fallback['recipe']['ai_generated'] = False
                        fallback['recipe']['database_source'] = True
                pick = fallback
                self.logger.warning(f"⚠️ Generated fallback meal for {mt}: {fallback.get('meal_name')} ({'AI' if fallback.get('recipe',{}).get('ai_generated') else 'DB'})")
            ordered.append(pick)
        # Ensure we have exactly len(meal_types) meals - if somehow short, fill remaining
        if len(ordered) < len(meal_types):
            self.logger.error(f"❌ CRITICAL: Ordered list has {len(ordered)} meals but need {len(meal_types)}!")
            # Fill remaining slots
            for i in range(len(ordered), len(meal_types)):
                mt = meal_types[i]
                used_names = [m.get('meal_name', '') for m in ordered]
                fallback = fallback_generator.generate_unique_recipe(mt, target_calories, 'International', used_names)
                if 'recipe' not in fallback:
                    fallback['recipe'] = {}
                # CRITICAL FIX: In AI-only mode, ALL fallbacks must be AI (not 50/50)
                if is_ai_only_mode:
                    # AI-ONLY MODE: Always mark fallbacks as AI
                    fallback['recipe']['ai_generated'] = True
                    fallback['recipe']['database_source'] = False
                    fallback['ai_generated'] = True
                else:
                    # 50/50 MODE: Check current AI/DB balance to maintain 50/50 split
                    current_ai_count = sum(1 for m in ordered if m.get('recipe', {}).get('ai_generated'))
                    target_ai = len(meal_types) // 2
                    if current_ai_count < target_ai:
                        fallback['recipe']['ai_generated'] = True
                        fallback['recipe']['database_source'] = False
                    else:
                        fallback['recipe']['ai_generated'] = False
                        fallback['recipe']['database_source'] = True
                ordered.append(fallback)
                self.logger.warning(f"✅ Emergency fill slot {i+1}: {fallback.get('meal_name')}")
        all_meals = ordered[:len(meal_types)]
        
        # Final validation: ensure we have exactly len(meal_types) meals
        if len(all_meals) != len(meal_types):
            self.logger.error(f"❌ CRITICAL: Final meal list has {len(all_meals)} meals but need {len(meal_types)}!")
            # Fill to exact count
            while len(all_meals) < len(meal_types):
                mt = meal_types[len(all_meals)]
                used_names = [m.get('meal_name', '') for m in all_meals]
                fallback = fallback_generator.generate_unique_recipe(mt, target_calories, 'International', used_names)
                if 'recipe' not in fallback:
                    fallback['recipe'] = {}
                # CRITICAL FIX: In AI-only mode, ALL fallbacks must be AI (not 50/50)
                if is_ai_only_mode:
                    # AI-ONLY MODE: Always mark fallbacks as AI
                    fallback['recipe']['ai_generated'] = True
                    fallback['recipe']['database_source'] = False
                    fallback['ai_generated'] = True
                else:
                    # 50/50 MODE: Check current AI/DB balance to maintain 50/50 split
                    current_ai_count = sum(1 for m in all_meals if m.get('recipe', {}).get('ai_generated'))
                    target_ai = len(meal_types) // 2
                    if current_ai_count < target_ai:
                        fallback['recipe']['ai_generated'] = True
                        fallback['recipe']['database_source'] = False
                    else:
                        fallback['recipe']['ai_generated'] = False
                        fallback['recipe']['database_source'] = True
                all_meals.append(fallback)
                self.logger.warning(f"✅ Final emergency fill: {fallback.get('meal_name')}")

        # Validate and correct AI-generated recipes using database as ground truth
        try:
            from services.ai_validator import AIRecipeValidator
            validator = AIRecipeValidator(db)
            
            for meal in all_meals:
                rec = meal.get('recipe') or {}
                
                # Only validate AI-generated recipes (database recipes are already validated)
                if rec.get('ai_generated', True):
                    try:
                        # Validate and correct the AI recipe
                        validated_recipe = validator.validate_and_correct_recipe(
                            rec,
                            recalculate_nutrition=True,
                            correct_ingredient_names=True
                        )
                        
                        # Ensure validated_recipe is a dict
                        if not isinstance(validated_recipe, dict):
                            validated_recipe = rec.copy() if isinstance(rec, dict) else {}
                        
                        # Update meal with validated recipe - ensure AI flag persists
                        meal['recipe'] = validated_recipe
                        # Ensure ai_generated flag is preserved
                        if meal.get('recipe', {}).get('ai_generated') or validated_recipe.get('ai_generated'):
                            validated_recipe['ai_generated'] = True
                            validated_recipe['database_source'] = False
                        
                        # Use per-serving calories from validated recipe
                        recipe_nutrition = validated_recipe.get('nutrition', {}) or {}
                        per_serving_cal = (
                            recipe_nutrition.get('per_serving_calories') or 
                            recipe_nutrition.get('calories') or 
                            validated_recipe.get('calories') or 
                            meal.get('calories')
                        )
                        try:
                            per_serving_cal = int(float(per_serving_cal)) if per_serving_cal else None
                        except (ValueError, TypeError):
                            per_serving_cal = None
                        
                        # If no calories found, estimate from ingredients
                        if not per_serving_cal or per_serving_cal <= 0:
                            ingredients = validated_recipe.get('ingredients') or rec.get('ingredients') or []
                            if ingredients:
                                try:
                                    from services.nutrition_service import NutritionService
                                    nutrition_service = NutritionService()
                                    est = nutrition_service._estimate_nutrition_from_ingredients(ingredients)
                                    servings = validated_recipe.get('servings') or rec.get('servings') or 1
                                    if est and est.get('calories') and est.get('calories') > 0:
                                        # Divide by servings to get per-serving
                                        per_serving_cal = int(est.get('calories') / max(1, servings))
                                        # Update nutrition in recipe
                                        validated_recipe.setdefault('nutrition', {})
                                        validated_recipe['nutrition']['per_serving_calories'] = per_serving_cal
                                        validated_recipe['nutrition']['calories'] = per_serving_cal
                                        # Also update macros per-serving
                                        validated_recipe['nutrition']['per_serving_protein'] = round(est.get('protein', 0) / max(1, servings), 1)
                                        validated_recipe['nutrition']['per_serving_carbs'] = round(est.get('carbs', 0) / max(1, servings), 1)
                                        validated_recipe['nutrition']['per_serving_fats'] = round(est.get('fats', 0) / max(1, servings), 1)
                                except Exception as est_err:
                                    self.logger.warning(f"Could not estimate calories from ingredients: {est_err}")
                                    per_serving_cal = None
                        
                        # Final fallback: if still no calories, skip this meal (don't use 500 placeholder)
                        if not per_serving_cal or per_serving_cal <= 0:
                            self.logger.warning(f"⚠️ No valid calories found for meal '{meal.get('meal_name', 'unknown')}', skipping")
                            continue
                        
                        meal['calories'] = per_serving_cal
                        meal['per_serving_calories'] = per_serving_cal  # CRITICAL: Set explicitly for extraction
                        meal['protein'] = recipe_nutrition.get('per_serving_protein') or recipe_nutrition.get('protein') or validated_recipe.get('protein', meal.get('protein', 0))
                        meal['carbs'] = recipe_nutrition.get('per_serving_carbs') or recipe_nutrition.get('carbs') or validated_recipe.get('carbs', meal.get('carbs', 0))
                        meal['fats'] = recipe_nutrition.get('per_serving_fats') or recipe_nutrition.get('fats') or validated_recipe.get('fats', meal.get('fats', 0))
                        
                        # CRITICAL: Also set in recipe.nutrition for consistency
                        validated_recipe.setdefault('nutrition', {})
                        validated_recipe['nutrition']['per_serving_calories'] = per_serving_cal
                        validated_recipe['per_serving_calories'] = per_serving_cal
                    except Exception as e:
                        self.logger.warning(f"Error validating AI recipe: {e}")
                        # Fallback to nutrition service estimation
                        from services.nutrition_service import NutritionService
                        nutrition_service = NutritionService()
                        ingredients = rec.get('ingredients') or []
                        if ingredients:
                            try:
                                est = nutrition_service._estimate_nutrition_from_ingredients(ingredients)
                                if est and any((est.get('calories') or 0, est.get('protein') or 0, est.get('carbs') or 0, est.get('fats') or 0)):
                                    rec.setdefault('nutrition', {})
                                    rec['nutrition'].update({
                                        'calories': int(est.get('calories') or 0),
                                        'protein': int(est.get('protein') or 0),
                                        'carbs': int(est.get('carbs') or 0),
                                        'fats': int(est.get('fats') or 0),
                                    })
                                    est_cal = int(est.get('calories') or meal.get('calories') or 0)
                                    meal['calories'] = est_cal
                                    meal['per_serving_calories'] = est_cal  # CRITICAL: Set explicitly
                                    meal['protein'] = int(est.get('protein') or meal.get('protein') or 0)
                                    meal['carbs'] = int(est.get('carbs') or meal.get('carbs') or 0)
                                    meal['fats'] = int(est.get('fats') or meal.get('fats') or 0)
                                    # CRITICAL: Also set in recipe.nutrition for consistency
                                    rec.setdefault('nutrition', {})
                                    rec['nutrition']['per_serving_calories'] = est_cal
                                    rec['per_serving_calories'] = est_cal
                                    meal['recipe'] = rec
                            except Exception:
                                continue
        except Exception as e:
            self.logger.warning(f"AI validator not available: {e}")
            # Best-effort fallback to nutrition service estimation
            try:
                from services.nutrition_service import NutritionService
                nutrition_service = NutritionService()
                for meal in all_meals:
                    rec = meal.get('recipe') or {}
                    ingredients = rec.get('ingredients') or []
                    if ingredients:
                        try:
                            est = nutrition_service._estimate_nutrition_from_ingredients(ingredients)
                            if est and any((est.get('calories') or 0, est.get('protein') or 0, est.get('carbs') or 0, est.get('fats') or 0)):
                                rec.setdefault('nutrition', {})
                                rec['nutrition'].update({
                                    'calories': int(est.get('calories') or 0),
                                    'protein': int(est.get('protein') or 0),
                                    'carbs': int(est.get('carbs') or 0),
                                    'fats': int(est.get('fats') or 0),
                                })
                                est_cal = int(est.get('calories') or meal.get('calories') or 0)
                                meal['calories'] = est_cal
                                meal['per_serving_calories'] = est_cal  # CRITICAL: Set explicitly
                                meal['protein'] = int(est.get('protein') or meal.get('protein') or 0)
                                meal['carbs'] = int(est.get('carbs') or meal.get('carbs') or 0)
                                meal['fats'] = int(est.get('fats') or meal.get('fats') or 0)
                                # CRITICAL: Also set in recipe.nutrition for consistency
                                rec.setdefault('nutrition', {})
                                rec['nutrition']['per_serving_calories'] = est_cal
                                rec['per_serving_calories'] = est_cal
                                meal['recipe'] = rec
                        except Exception:
                            continue
            except Exception as balance_err:
                self.logger.error(f"❌ Error in day-level calorie balancing: {balance_err}", exc_info=True)
                # Don't fail completely - just log and continue with unbalanced meals

        # CRITICAL: Final day-level balancing to hit user's daily calorie target
        # This is the MOST IMPORTANT step - ensure daily totals match user's set intake
        try:
            # Get meals_per_day from user preferences (default to 4)
            meals_per_day = user_preferences.get('meals_per_day', 4)
            base_types = ['breakfast','lunch','dinner','snack']
            # CRITICAL: Use actual meals_per_day, not hardcoded base_types
            # If user sets 3 meals/day, use 3 meal types (not 4)
            if meals_per_day == 3:
                day_base_types = ['breakfast', 'lunch', 'dinner']
            elif meals_per_day == 5:
                day_base_types = ['breakfast', 'snack', 'lunch', 'dinner', 'snack']
            else:  # Default to 4
                day_base_types = ['breakfast', 'lunch', 'dinner', 'snack']
            
            # Track used meal names for balancing adjustments
            used_names = set([m.get('meal_name', '') for m in all_meals if m.get('meal_name')])
            
            # Calculate days based on actual meals_per_day
            if len(meal_types) % meals_per_day == 0:
                days = len(meal_types) // meals_per_day
                
                # Get actual daily calorie target from user preferences (CRITICAL!)
                actual_daily_target = user_preferences.get('daily_calorie_target')
                if actual_daily_target:
                    daily_target = int(actual_daily_target)
                    self.logger.info(f"🎯 Using user's daily calorie target: {daily_target} kcal")
                else:
                    # Fallback: calculate from per-meal target * meals_per_day
                    daily_target = target_calories * meals_per_day
                    self.logger.warning(f"⚠️ No daily_calorie_target in preferences, using calculated: {daily_target} kcal (target_calories={target_calories} * meals_per_day={meals_per_day})")
                for day_idx in range(days):
                    start = day_idx * meals_per_day  # Use actual meals_per_day, not len(base_types)
                    end = start + meals_per_day
                    day_slice = all_meals[start:end]
                    # CRITICAL FIX: Compute current daily calories using PER-SERVING values
                    # Must use per-serving calories, not total recipe calories
                    current = 0
                    for m in day_slice:
                        # CRITICAL: Extract per-serving calories consistently
                        # Priority: per_serving_calories (explicit) > calories (if reasonable) > calculated
                        meal_cal = None
                        
                        # First try: explicit per_serving_calories
                        meal_cal = (
                            m.get('per_serving_calories') or
                            m.get('recipe', {}).get('per_serving_calories') or
                            m.get('recipe', {}).get('nutrition', {}).get('per_serving_calories')
                        )
                        # Ensure meal_cal is numeric
                        try:
                            meal_cal = float(meal_cal) if meal_cal is not None else None
                        except (ValueError, TypeError):
                            meal_cal = None
                        
                        # Second try: calories field (if it looks like per-serving < 800)
                        if not meal_cal or meal_cal == 0:
                            cal_value = m.get('calories') or m.get('recipe', {}).get('nutrition', {}).get('calories') or m.get('recipe', {}).get('calories')
                            try:
                                cal_value = float(cal_value) if cal_value is not None else None
                            except (ValueError, TypeError):
                                cal_value = None
                            
                            if cal_value is not None and cal_value > 0:
                                servings = m.get('recipe', {}).get('servings') or m.get('servings') or 1
                                try:
                                    servings = int(float(servings)) if servings else 1
                                except (ValueError, TypeError):
                                    servings = 1
                                
                                # If calories > 800 and servings > 1, likely total - divide
                                if cal_value > 800 and servings > 1:
                                    meal_cal = cal_value / servings
                                elif cal_value <= 800:
                                    # Likely already per-serving
                                    meal_cal = cal_value
                                else:
                                    meal_cal = cal_value
                        
                        # Fallback: use target_calories as safer default
                        if not meal_cal or meal_cal <= 0:
                            meal_cal = float(max(100, min(int(target_calories), 800)))
                        
                        meal_cal = float(meal_cal)
                        current += meal_cal
                    self.logger.info(f"📊 Day {day_idx + 1}: Current = {current:.0f} cal, Target = {daily_target} cal, Diff = {daily_target - current:.0f} cal")
                    # Identify snack index within this day's sequence
                    # If not found, use the last meal as adjustable
                    snack_local_idx = None
                    for i, mt in enumerate(meal_types[start:end]):
                        if mt == 'snack':
                            snack_local_idx = i
                            break
                    # If no snack, use last meal of the day
                    adj_idx = start + (snack_local_idx if snack_local_idx is not None else (meals_per_day - 1))
                    # Get actual daily target from user preferences if available
                    actual_daily_target = user_preferences.get('daily_calorie_target', daily_target)
                    if actual_daily_target != daily_target:
                        daily_target = actual_daily_target
                    
                    # CRITICAL: Detect AI-only mode before balancing
                    day_ai_count = sum(1 for m in all_meals[start:end] if (m.get('recipe') or {}).get('ai_generated') == True)
                    day_db_count = len(all_meals[start:end]) - day_ai_count
                    is_ai_only_day = day_db_count == 0 and day_ai_count > 0
                    
                    # CRITICAL: If we are off by more than 50 calories, adjust meals to get closer to target
                    # Use absolute threshold (50 cal) instead of percentage for more reliable balancing
                    if daily_target <= 0:
                        continue
                    diff = daily_target - current
                    # Adjust if off by more than 50 calories (not percentage-based)
                    threshold_calories = 50  # Absolute threshold
                    if abs(diff) >= threshold_calories:
                        self.logger.info(f"   🔧 Day {day_idx + 1} is off by {abs(diff)/daily_target*100:.1f}% ({diff:+.0f} cal) - adjusting meals")
                        # AI-ONLY MODE: Don't pull database recipes - always use fallback marked as AI
                        def find_db_replacement(meal_type: str, desired: int) -> Dict[str, Any]:
                            # DATABASE FALLBACKS DISABLED - Always return empty to force AI fallback
                            # AI-ONLY MODE: Skip database replacement
                            # if is_ai_only_day:
                            return {}  # Always force fallback to AI (database fallbacks disabled)
                            # 50/50 MODE: Try database replacement
                            if db is None:
                                return {}
                            try:
                                # CRITICAL FIX: Database uses same meal types (breakfast, lunch, dinner, snack)
                                # NOT the old mapping (side_dish, main_course)
                                from models.recipe import Recipe
                                q = db.query(Recipe).filter(Recipe.is_active == True, Recipe.meal_type == meal_type)
                                # choose 5 closest by absolute difference
                                candidates = q.all()
                                if not candidates:
                                    return {}
                                candidates.sort(key=lambda r: abs((r.per_serving_calories or 0) - desired))
                                for rec in candidates[:10]:
                                    if rec.title in used_names:  # used_names is in outer scope
                                        continue
                                    return self._recipe_to_meal_format(rec, int(desired), meal_type)
                                return {}
                            except Exception:
                                return {}

                        # CRITICAL: Distribute calorie adjustment across multiple meals for better balance
                        # Strategy: Adjust 2-3 meals instead of just snack to avoid large single-meal changes
                        meals_to_adjust = []
                        
                        # Find adjustable meals (snack, lunch, dinner - prefer snack first)
                        for i, mt in enumerate(meal_types[start:end]):
                            meal_idx = start + i
                            meal = all_meals[meal_idx]
                            # Skip breakfast - keep it stable
                            if mt == 'breakfast':
                                continue
                            # Prioritize snack, then lunch, then dinner
                            priority = {'snack': 3, 'lunch': 2, 'dinner': 1}.get(mt, 0)
                            if priority > 0:
                                meals_to_adjust.append((priority, meal_idx, mt, meal))
                        
                        # Sort by priority (highest first)
                        meals_to_adjust.sort(reverse=True)
                        
                        if meals_to_adjust:
                            # Distribute the adjustment across top 2-3 meals
                            num_to_adjust = min(len(meals_to_adjust), 2 if abs(diff) < 300 else 3)
                            calories_per_meal = diff / num_to_adjust
                            
                            for priority, meal_idx, meal_type, meal in meals_to_adjust[:num_to_adjust]:
                                # CRITICAL: Extract per-serving calories consistently
                                current_meal_cal = None
                                # Try explicit per_serving_calories first
                                current_meal_cal = (
                                    meal.get('per_serving_calories') or
                                    meal.get('recipe', {}).get('per_serving_calories') or
                                    meal.get('recipe', {}).get('nutrition', {}).get('per_serving_calories')
                                )
                                # Ensure current_meal_cal is numeric
                                try:
                                    current_meal_cal = float(current_meal_cal) if current_meal_cal is not None else None
                                except (ValueError, TypeError):
                                    current_meal_cal = None
                                # If not found, check calories field
                                if not current_meal_cal or current_meal_cal == 0:
                                    cal_value = meal.get('calories') or meal.get('recipe', {}).get('nutrition', {}).get('calories') or meal.get('recipe', {}).get('calories')
                                    try:
                                        cal_value = float(cal_value) if cal_value is not None else None
                                    except (ValueError, TypeError):
                                        cal_value = None
                                    
                                    if cal_value is not None and cal_value > 0:
                                        servings = meal.get('recipe', {}).get('servings') or meal.get('servings') or 1
                                        try:
                                            servings = int(float(servings)) if servings else 1
                                        except (ValueError, TypeError):
                                            servings = 1
                                        
                                        # If calories > 800 and servings > 1, likely total - divide
                                        if cal_value > 800 and servings > 1:
                                            current_meal_cal = cal_value / servings
                                        elif cal_value <= 800:
                                            current_meal_cal = cal_value
                                        else:
                                            current_meal_cal = cal_value
                                # Fallback
                                if not current_meal_cal or current_meal_cal <= 0:
                                    current_meal_cal = float(max(100, min(int(target_calories), 800)))
                                current_meal_cal = float(current_meal_cal)
                                
                                # Calculate desired calories for this meal
                                desired_meal_cal = current_meal_cal + calories_per_meal
                                # Set reasonable bounds based on meal type
                                if meal_type == 'snack':
                                    desired_meal_cal = max(100, min(int(desired_meal_cal), 600))
                                elif meal_type == 'lunch':
                                    desired_meal_cal = max(300, min(int(desired_meal_cal), 800))
                                else:  # dinner
                                    desired_meal_cal = max(400, min(int(desired_meal_cal), 1000))
                                
                                self.logger.info(f"   🔧 Adjusting {meal_type} from {current_meal_cal:.0f} to {desired_meal_cal:.0f} cal (+{calories_per_meal:+.0f})")
                                
                                # AI-ONLY MODE: Don't pull database recipes during balancing
                                # Skip database replacement to maintain AI-only generation
                                replacement = {}  # Skip database replacement
                                if not replacement:
                                    # Use fallback meal generator (marked as AI to maintain AI-only mode)
                                    replacement = fallback_generator.generate_unique_recipe(
                                        meal_type, int(desired_meal_cal), meal.get('cuisine') or 'International', list(used_names)
                                    )
                                    replacement.setdefault('recipe', {})
                                    # Preserve AI flag from original meal (maintain AI-only mode)
                                    if meal.get('recipe', {}).get('ai_generated'):
                                        replacement['recipe']['ai_generated'] = True
                                    else:
                                        # Mark as AI to maintain AI-only mode (don't introduce DB recipes)
                                        replacement['recipe']['ai_generated'] = True
                                        replacement['recipe']['database_source'] = False
                                
                                all_meals[meal_idx] = replacement
                                used_names.add(replacement.get('meal_name',''))
                        else:
                            # Fallback: adjust snack only if no other meals found
                            current_snack = all_meals[adj_idx]
                            current_snack_cal = (
                                current_snack.get('per_serving_calories') or
                                current_snack.get('recipe', {}).get('nutrition', {}).get('per_serving_calories') or
                                current_snack.get('recipe', {}).get('per_serving_calories') or
                                current_snack.get('calories') or
                                current_snack.get('recipe', {}).get('nutrition', {}).get('calories') or 0
                            )
                            servings = current_snack.get('recipe', {}).get('servings') or current_snack.get('servings') or 1
                            if current_snack_cal > 600 and servings > 1:
                                current_snack_cal = current_snack_cal / servings
                            desired_snack_cal = max(100, min(int(current_snack_cal + diff), 900))
                            self.logger.info(f"   🔧 Adjusting snack from {current_snack_cal:.0f} to {desired_snack_cal:.0f} cal")
                            # AI-ONLY: Don't pull database recipes, use fallback marked as AI
                            replacement = {}  # Skip database replacement
                            if not replacement:
                                replacement = fallback_generator.generate_unique_recipe(
                                    'snack', desired_snack_cal, current_snack.get('cuisine') or 'International', list(used_names)
                                )
                                replacement.setdefault('recipe', {})
                                # Preserve AI flag from original meal
                                if current_snack.get('recipe', {}).get('ai_generated'):
                                    replacement['recipe']['ai_generated'] = True
                                else:
                                    replacement['recipe']['ai_generated'] = True  # Mark as AI in AI-only mode
                                    replacement['recipe']['database_source'] = False
                            all_meals[adj_idx] = replacement
                            used_names.add(replacement.get('meal_name',''))

                        # If still off by >3%, adjust lunch as a secondary lever
                        # CRITICAL: Use per-serving calories with type safety
                        new_current = 0
                        for m in all_meals[start:end]:
                            meal_cal = None
                            # Try explicit per_serving_calories first
                            meal_cal = (
                                m.get('per_serving_calories') or
                                m.get('recipe', {}).get('per_serving_calories') or
                                m.get('recipe', {}).get('nutrition', {}).get('per_serving_calories')
                            )
                            try:
                                meal_cal = float(meal_cal) if meal_cal is not None else None
                            except (ValueError, TypeError):
                                meal_cal = None
                            
                            # Fallback to calories field
                            if not meal_cal or meal_cal == 0:
                                cal_value = m.get('calories') or m.get('recipe', {}).get('nutrition', {}).get('calories') or m.get('recipe', {}).get('calories')
                                try:
                                    cal_value = float(cal_value) if cal_value is not None else None
                                except (ValueError, TypeError):
                                    cal_value = None
                                
                                if cal_value is not None and cal_value > 0:
                                    servings = m.get('recipe', {}).get('servings') or m.get('servings') or 1
                                    try:
                                        servings = int(float(servings)) if servings else 1
                                    except (ValueError, TypeError):
                                        servings = 1
                                    if cal_value > 800 and servings > 1:
                                        meal_cal = cal_value / servings
                                    else:
                                        meal_cal = cal_value
                            
                            if not meal_cal or meal_cal <= 0:
                                meal_cal = float(max(100, min(int(target_calories), 800)))
                            meal_cal = float(meal_cal)
                            new_current += meal_cal
                        remaining = daily_target - new_current
                        if abs(remaining) >= threshold_calories:  # Use absolute threshold
                            # Find lunch index
                            lunch_local_idx = None
                            for i, mt in enumerate(meal_types[start:end]):
                                if mt == 'lunch':
                                    lunch_local_idx = i
                                    break
                            if lunch_local_idx is not None:
                                lunch_idx = start + lunch_local_idx
                                cur_lunch = all_meals[lunch_idx]
                                # CRITICAL: Extract per-serving calories
                                cur_lunch_cal = (
                                    cur_lunch.get('per_serving_calories') or
                                    cur_lunch.get('recipe', {}).get('nutrition', {}).get('per_serving_calories') or
                                    cur_lunch.get('recipe', {}).get('per_serving_calories') or
                                    cur_lunch.get('calories') or
                                    cur_lunch.get('recipe', {}).get('nutrition', {}).get('calories') or 0
                                )
                                servings = cur_lunch.get('recipe', {}).get('servings') or cur_lunch.get('servings') or 1
                                if cur_lunch_cal > 600 and servings > 1:
                                    cur_lunch_cal = cur_lunch_cal / servings
                                desired_lunch_cal = max(200, min(int(cur_lunch_cal + remaining), 1100))
                                self.logger.info(f"   🔧 Adjusting lunch from {cur_lunch_cal:.0f} to {desired_lunch_cal:.0f} cal (remaining diff: {remaining:.0f})")
                                # AI-ONLY MODE: Skip database replacement
                                repl_lunch = {} if is_ai_only_day else find_db_replacement('lunch', desired_lunch_cal)
                                if not repl_lunch:
                                    repl_lunch = fallback_generator.generate_unique_recipe(
                                        'lunch', desired_lunch_cal, cur_lunch.get('cuisine') or 'International', list(used_names)
                                    )
                                    repl_lunch.setdefault('recipe', {})
                                    # Preserve AI flag from original meal or set as AI in AI-only mode
                                    if is_ai_only_day or cur_lunch.get('recipe', {}).get('ai_generated'):
                                        repl_lunch['recipe']['ai_generated'] = True
                                        repl_lunch['recipe']['database_source'] = False
                                    else:
                                        repl_lunch['recipe']['ai_generated'] = True  # Default to AI to maintain AI-only
                                        repl_lunch['recipe']['database_source'] = False
                                all_meals[lunch_idx] = repl_lunch
                                used_names.add(repl_lunch.get('meal_name',''))
                        
                        # Final check: if still significantly off (>1.5%), adjust breakfast or dinner
                        # CRITICAL: Use per-serving calories
                        final_current = 0
                        for m in all_meals[start:end]:
                            meal_cal = (
                                m.get('per_serving_calories') or
                                m.get('recipe', {}).get('nutrition', {}).get('per_serving_calories') or
                                m.get('recipe', {}).get('per_serving_calories') or
                                m.get('calories') or
                                m.get('recipe', {}).get('nutrition', {}).get('calories') or 0
                            )
                            servings = m.get('recipe', {}).get('servings') or m.get('servings') or 1
                            if meal_cal > 600 and servings > 1:
                                meal_cal = meal_cal / servings
                            final_current += meal_cal
                        final_diff = daily_target - final_current
                        if abs(final_diff) / daily_target >= 0.015:
                            # Find breakfast or dinner to adjust
                            for adj_meal_type in ['breakfast', 'dinner']:
                                adj_local_idx = None
                                for i, mt in enumerate(meal_types[start:end]):
                                    if mt == adj_meal_type:
                                        adj_local_idx = i
                                        break
                                if adj_local_idx is not None:
                                    adj_idx = start + adj_local_idx
                                    cur_meal = all_meals[adj_idx]
                                    # CRITICAL: Extract per-serving calories
                                    cur_meal_cal = (
                                        cur_meal.get('per_serving_calories') or
                                        cur_meal.get('recipe', {}).get('nutrition', {}).get('per_serving_calories') or
                                        cur_meal.get('recipe', {}).get('per_serving_calories') or
                                        cur_meal.get('calories') or
                                        cur_meal.get('recipe', {}).get('nutrition', {}).get('calories') or 0
                                    )
                                    servings = cur_meal.get('recipe', {}).get('servings') or cur_meal.get('servings') or 1
                                    if cur_meal_cal > 600 and servings > 1:
                                        cur_meal_cal = cur_meal_cal / servings
                                    desired_cal = max(200, min(int(cur_meal_cal + final_diff * 0.5), 900))
                                    self.logger.info(f"   🔧 Adjusting {adj_meal_type} from {cur_meal_cal:.0f} to {desired_cal:.0f} cal (final diff: {final_diff:.0f})")
                                    # AI-ONLY MODE: Skip database replacement
                                    repl = {} if is_ai_only_day else find_db_replacement(adj_meal_type, desired_cal)
                                    if not repl:
                                        repl = fallback_generator.generate_unique_recipe(
                                            adj_meal_type, desired_cal, cur_meal.get('cuisine') or 'International', list(used_names)
                                        )
                                        repl.setdefault('recipe', {})
                                        # Preserve AI flag from original meal or set as AI in AI-only mode
                                        if is_ai_only_day or cur_meal.get('recipe', {}).get('ai_generated'):
                                            repl['recipe']['ai_generated'] = True
                                            repl['recipe']['database_source'] = False
                                        else:
                                            repl['recipe']['ai_generated'] = True  # Default to AI to maintain AI-only
                                            repl['recipe']['database_source'] = False
                                    all_meals[adj_idx] = repl
                                    used_names.add(repl.get('meal_name',''))
                                    break  # Only adjust one more meal
                    
                    # Final verification: log actual daily total after all adjustments
                    final_after_adjust = 0
                    for m in all_meals[start:end]:
                        meal_cal = (
                            m.get('per_serving_calories') or
                            m.get('recipe', {}).get('nutrition', {}).get('per_serving_calories') or
                            m.get('recipe', {}).get('per_serving_calories') or
                            m.get('calories') or
                            m.get('recipe', {}).get('nutrition', {}).get('calories') or 0
                        )
                        servings = m.get('recipe', {}).get('servings') or m.get('servings') or 1
                        if meal_cal > 600 and servings > 1:
                            meal_cal = meal_cal / servings
                        final_after_adjust += meal_cal
                    
                    final_diff_after = daily_target - final_after_adjust
                    accuracy = (1 - abs(final_diff_after) / daily_target) * 100 if daily_target > 0 else 0
                    self.logger.info(f"✅ Day {day_idx + 1} Final: {final_after_adjust:.0f} cal (target: {daily_target} cal, diff: {final_diff_after:+.0f} cal, accuracy: {accuracy:.1f}%)")
                    
        except Exception as e:
            # Balancing is best-effort; log errors but continue
            self.logger.error(f"Error in day-level balancing: {e}", exc_info=True)
            pass

        return all_meals
    
    def _is_appropriate_for_meal_type(self, recipe: Recipe, meal_type: str) -> bool:
        """
        Check if a recipe is appropriate for a specific meal type
        """
        title_lower = recipe.title.lower()
        summary_lower = (recipe.summary or "").lower()
        
        # Breakfast keywords - light, morning foods
        breakfast_keywords = ['breakfast', 'morning', 'cereal', 'toast', 'pancake', 'waffle', 'oatmeal', 'yogurt', 'smoothie', 'muffin', 'bagel', 'croissant', 'eggs', 'bacon', 'sausage', 'porridge', 'granola', 'fruit', 'berry']
        
        # Lunch keywords - lighter main dishes, salads, bowls
        lunch_keywords = ['lunch', 'salad', 'sandwich', 'wrap', 'soup', 'pasta', 'rice', 'quinoa', 'bowl', 'stir-fry', 'noodles', 'vegetable', 'chicken', 'fish', 'light', 'fresh']
        
        # Dinner keywords - hearty main dishes
        dinner_keywords = ['dinner', 'roast', 'grilled', 'baked', 'steak', 'chicken', 'fish', 'pork', 'beef', 'lamb', 'curry', 'stew', 'casserole', 'lasagna', 'pizza', 'meat', 'main', 'hearty', 'rich']
        
        # Snack keywords - small portions, finger foods
        snack_keywords = ['snack', 'crackers', 'nuts', 'trail mix', 'fruit', 'vegetable', 'dip', 'spread', 'chips', 'popcorn', 'granola', 'energy bar', 'small', 'bite', 'finger']
        
        # Check for explicit meal type matches first
        if meal_type in title_lower or meal_type in summary_lower:
            return True
        
        if meal_type == 'breakfast':
            # For breakfast, prefer lighter foods or anything with breakfast keywords
            return any(keyword in title_lower or keyword in summary_lower for keyword in breakfast_keywords)
        elif meal_type == 'lunch':
            # For lunch, prefer lighter main dishes or anything with lunch keywords
            return any(keyword in title_lower or keyword in summary_lower for keyword in lunch_keywords)
        elif meal_type == 'dinner':
            # For dinner, prefer hearty main dishes or anything with dinner keywords
            return any(keyword in title_lower or keyword in summary_lower for keyword in dinner_keywords)
        elif meal_type == 'snack':
            # For snacks, prefer small portions or anything with snack keywords
            return any(keyword in title_lower or keyword in summary_lower for keyword in snack_keywords)
        
        # If no specific keywords match, allow it (better than nothing)
        return True
    
    def _is_beverage_or_sauce(self, recipe: Recipe) -> bool:
        """Enhanced beverage/sauce detection - checks title, summary, ingredients, and instructions"""
        title = (recipe.title or "").lower()
        summary = (recipe.summary or "").lower()
        
        # Get ingredients text
        ingredients_text = ""
        if hasattr(recipe, 'ingredients') and recipe.ingredients:
            ingredient_names = []
            for ri in recipe.ingredients:
                if ri.ingredient:
                    ingredient_names.append(ri.ingredient.name.lower())
            ingredients_text = " ".join(ingredient_names)
        
        # Get instructions text
        instructions_text = ""
        if hasattr(recipe, 'instructions') and recipe.instructions:
            instruction_descs = []
            for inst in recipe.instructions:
                instruction_descs.append(inst.description.lower() if inst.description else "")
            instructions_text = " ".join(instruction_descs)
        
        # Combine all text for comprehensive checking
        text = f"{title} {summary} {ingredients_text} {instructions_text}"
        
        # Beverage keywords (expanded to catch drinks like "Boccie Ball")
        beverage_keywords = [
            "sangria", "cocktail", "smoothie", "shake", "juice", "punch", "cider", 
            "tea", "coffee", "latte", "mojito", "spritzer", "spritz", "ball",
            "amaretto", "vodka", "rum", "gin", "whiskey", "beer", "wine", "liquor",
            "highball", "glass", "drink", "beverage", "mixed drink", "shot",
            "margarita", "daiquiri", "martini", "cosmopolitan"
        ]
        
        # Sauce keywords
        sauce_keywords = ["sauce", "dressing", "marinade", "relish", "salsa", "ketchup", "gravy", "dip", "guacamole"]
        
        # Dessert keywords (exclude from main meals)
        dessert_keywords = ["ice cream", "sorbet", "cookie", "brownie", "cake", "pudding", "mousse", "dessert"]
        
        # Check for beverage indicators in any part of the recipe
        return any(k in text for k in beverage_keywords + sauce_keywords + dessert_keywords)

    def _recipe_to_meal_format(self, recipe: Recipe, target_calories: int, meal_type: str = None) -> Dict[str, Any]:
        """
        Convert database recipe to meal format
        """
        # Use the actual per-serving calories from the database
        recipe_calories = recipe.per_serving_calories
        recipe_servings = recipe.servings or 1
        
        # If no calories in database, estimate from ingredients
        if not recipe_calories or recipe_calories <= 0:
            ingredients = self._get_recipe_ingredients(recipe)
            if ingredients:
                try:
                    from services.nutrition_service import NutritionService
                    nutrition_service = NutritionService()
                    est = nutrition_service._estimate_nutrition_from_ingredients(ingredients)
                    if est and est.get('calories') and est.get('calories') > 0:
                        # Calculate per-serving from total estimated calories
                        recipe_calories = int(est.get('calories') / max(1, recipe_servings))
                        self.logger.info(f"📊 Estimated {recipe_calories} calories per serving for recipe '{recipe.title}' from ingredients")
                    else:
                        self.logger.warning(f"⚠️ Could not estimate calories from ingredients for recipe '{recipe.title}'")
                        recipe_calories = None
                except Exception as est_err:
                    self.logger.warning(f"Error estimating calories for recipe '{recipe.title}': {est_err}")
                    recipe_calories = None
            else:
                self.logger.warning(f"⚠️ No ingredients found for recipe '{recipe.title}', cannot estimate calories")
                recipe_calories = None
        
        # If still no calories, skip this recipe (don't return a meal with invalid calories)
        if not recipe_calories or recipe_calories <= 0:
            self.logger.warning(f"⚠️ Skipping recipe '{recipe.title}' - no valid calories available")
            return None
        
        # Calculate total recipe calories
        total_recipe_calories = recipe_calories * recipe_servings
        
        # Build ingredients/instructions
        ingredients = self._get_recipe_ingredients(recipe)
        instructions = self._get_recipe_instructions(recipe)
        
        # Infer dietary tags from ingredients and sanitize
        try:
            from services.nutrition_service import NutritionService
            inferred = NutritionService()._infer_dietary_tags_from_ingredients(
                ingredients,
                existing_tags=list(recipe.dietary_tags or []),
                title=recipe.title or ""
            )
            # Sanitize: remove vegan if eggs/dairy; remove vegetarian if eggs/fish/meat
            text = f"{recipe.title} " + " ".join([str(i.get('name','')).lower() for i in ingredients])
            has_egg_or_dairy = any(k in text for k in ["egg","eggs","milk","cheese","yogurt","butter","cream"])
            has_meat_or_fish = any(k in text for k in ["chicken","beef","pork","lamb","turkey","bacon","ham","sausage","fish","salmon","tuna","shrimp","prawn","anchovy"])
            if has_egg_or_dairy and "vegan" in inferred:
                inferred = [t for t in inferred if t != "vegan"]
            if (has_meat_or_fish or ("eggs" in text)) and "vegetarian" in inferred:
                inferred = [t for t in inferred if t != "vegetarian"]
            # Remove nut-free if sesame present
            if any(k in text for k in ["sesame","tahini","sesame oil","sesame seed","sesame seeds"]):
                inferred = [t for t in inferred if t != "nut-free"]
            dietary_tags = inferred
        except Exception:
            dietary_tags = list(recipe.dietary_tags or [])
        
        # For meal planning, use per-serving values (not adjusted to daily target)
        # CRITICAL: Always set per_serving_calories explicitly to ensure correct extraction
        return {
            "meal_name": recipe.title,
            "meal_type": meal_type or recipe.meal_type,  # Use assigned meal type
            "calories": int(recipe_calories),  # Per serving calories
            "per_serving_calories": int(recipe_calories),  # CRITICAL: Explicitly set for extraction logic
            "protein": int(recipe.per_serving_protein or 0),
            "carbs": int(recipe.per_serving_carbs or 0),
            "fats": int(recipe.per_serving_fat or 0),
            "cuisine": recipe.cuisine,
            "recipe": {
                "title": recipe.title,
                "cuisine": recipe.cuisine,
                "prep_time": recipe.prep_time,
                "cook_time": recipe.cook_time,
                "servings": recipe.servings or 1,
                "difficulty": recipe.difficulty_level,
                "summary": recipe.summary or f"A delicious {recipe.cuisine} {recipe.meal_type}",
                "ingredients": ingredients,
                "instructions": instructions,
                "dietary_tags": dietary_tags,
                "per_serving_calories": int(recipe_calories),  # CRITICAL: Also set here for extraction
                "nutrition": {
                    "calories": int(recipe_calories),  # Per serving
                    "per_serving_calories": int(recipe_calories),  # CRITICAL: Also set here
                    "protein": int(recipe.per_serving_protein or 0),
                    "carbs": int(recipe.per_serving_carbs or 0),
                    "fats": int(recipe.per_serving_fat or 0)
                },
                "ai_generated": False,
                "database_source": True
            }
        }
    
    def _get_recipe_ingredients(self, recipe: Recipe) -> List[Dict[str, Any]]:
        """
        Get recipe ingredients in the expected format
        """
        ingredients = []
        for recipe_ingredient in recipe.ingredients:
            ingredients.append({
                "name": recipe_ingredient.ingredient.name,
                "quantity": recipe_ingredient.quantity,
                "unit": recipe_ingredient.unit
            })
        return ingredients
    
    def _get_recipe_instructions(self, recipe: Recipe) -> List[Dict[str, Any]]:
        """
        Get recipe instructions in the expected format
        """
        instructions = []
        for instruction in recipe.instructions:
            instructions.append({
                "step": instruction.step_number,
                "description": instruction.description
            })
        return instructions
