import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy import and_, or_, func, desc, case, text, String

from models.recipe import Recipe, Ingredient, RecipeIngredient, RecipeInstruction
from models.nutrition import (
    MealPlan, MealPlanMeal, MealPlanRecipe,
    NutritionalLog, ShoppingList, ShoppingListItem, UserNutritionPreferences
)
from models.health_profile import HealthProfile
from models.metrics_history import MetricsHistory
from schemas.nutrition import (
    MealPlanRequest, RecipeSearchRequest, ShoppingListCreate,
    NutritionalAnalysisRequest
)
from ai.nutrition_ai import NutritionAI
from services.measurement_standardization_service import MeasurementStandardizationService
from services.ai_nutritional_analysis_service import AINutritionalAnalysisService
from services.ai_improvement_suggestions_service import AIImprovementSuggestionsService
from services.meal_plan_versioning_service import meal_plan_versioning_service
from services.enhanced_dietary_service import EnhancedDietaryService
from services.enhanced_personalization_service import EnhancedPersonalizationService
from ai.enhanced_nutrition_ai import EnhancedNutritionAI

logger = logging.getLogger(__name__)

class NutritionService:
    def __init__(self):
        self.nutrition_ai = NutritionAI()
        self.enhanced_nutrition_ai = EnhancedNutritionAI()
        self.measurement_service = MeasurementStandardizationService()
        self.ai_analysis_service = AINutritionalAnalysisService()
        self.ai_suggestions_service = AIImprovementSuggestionsService()
        self.enhanced_dietary_service = EnhancedDietaryService()
        self.enhanced_personalization_service = EnhancedPersonalizationService()
    
    def calculate_personalized_targets(self, db: Session, user_id: int) -> Dict[str, Any]:
        """
        Calculate personalized nutrition targets based on health profile, BMI, and activity level
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary with personalized nutrition targets
        """
        try:
            # Get user's health profile
            health_profile = db.query(HealthProfile).filter(HealthProfile.user_id == user_id).first()
            if not health_profile:
                return self._get_default_targets()
            
            # Get latest metrics
            latest_metrics = db.query(MetricsHistory).filter(
                MetricsHistory.health_profile_id == health_profile.id
            ).order_by(desc(MetricsHistory.recorded_at)).first()
            
            if not latest_metrics:
                return self._get_default_targets()
            
            # Extract health data
            weight = latest_metrics.weight
            height = health_profile.height  # in cm
            age = health_profile.age
            gender = health_profile.gender.lower()
            activity_level = health_profile.activity_level.lower()
            fitness_goal = health_profile.fitness_goal.lower()
            
            # Calculate BMI
            bmi = weight / ((height / 100) ** 2)
            
            # Calculate BMR (Basal Metabolic Rate) using Mifflin-St Jeor Equation
            if gender == "male":
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161
            
            # Activity multipliers
            activity_multipliers = {
                "sedentary": 1.2,
                "lightly_active": 1.375,
                "moderately_active": 1.55,
                "very_active": 1.725,
                "extremely_active": 1.9
            }
            
            activity_multiplier = activity_multipliers.get(activity_level, 1.2)
            tdee = bmr * activity_multiplier  # Total Daily Energy Expenditure
            
            # Adjust calories based on fitness goal
            if fitness_goal == "weight_loss":
                calorie_target = tdee - 500  # 500 calorie deficit
            elif fitness_goal == "weight_gain":
                calorie_target = tdee + 500  # 500 calorie surplus
            elif fitness_goal == "muscle_gain":
                calorie_target = tdee + 300  # 300 calorie surplus
            else:  # maintenance
                calorie_target = tdee
            
            # Calculate macronutrient targets based on goals
            if fitness_goal == "weight_loss":
                protein_ratio = 0.3  # Higher protein for weight loss
                carbs_ratio = 0.4
                fats_ratio = 0.3
            elif fitness_goal == "muscle_gain":
                protein_ratio = 0.25  # Higher protein for muscle building
                carbs_ratio = 0.45
                fats_ratio = 0.3
            else:  # maintenance
                protein_ratio = 0.2
                carbs_ratio = 0.5
                fats_ratio = 0.3
            
            # Calculate macro targets in grams
            protein_target = (calorie_target * protein_ratio) / 4  # 4 cal/g protein
            carbs_target = (calorie_target * carbs_ratio) / 4  # 4 cal/g carbs
            fats_target = (calorie_target * fats_ratio) / 9  # 9 cal/g fat
            
            # Adjust for activity level
            if activity_level in ["very_active", "extremely_active"]:
                # Increase carbs for high activity
                carbs_target *= 1.2
                calorie_target += 200
            
            return {
                "calorie_target": round(calorie_target),
                "protein_target": round(protein_target, 1),
                "carbs_target": round(carbs_target, 1),
                "fats_target": round(fats_target, 1),
                "bmi": round(bmi, 1),
                "bmr": round(bmr),
                "tdee": round(tdee),
                "activity_level": activity_level,
                "fitness_goal": fitness_goal,
                "personalized": True
            }
            
        except Exception as e:
            logger.error(f"Error calculating personalized targets: {str(e)}")
            return self._get_default_targets()
    
    def _get_default_targets(self) -> Dict[str, Any]:
        """Get default nutrition targets when health data is unavailable"""
        return {
            "calorie_target": 2000,
            "protein_target": 150,
            "carbs_target": 250,
            "fats_target": 65,
            "personalized": False
        }

    # --- Helpers used when persisting generated meals ---
    def _sanitize_meal_type(self, meal_type: str, title: str = "", ingredients: Any = None) -> str:
        """Map/adjust meal types based on title/ingredients to keep grid sensible.
        - Breakfast: light items, eggs, oats, yogurt, smoothies
        - Lunch: salads, soups, sandwiches, bowls
        - Dinner: hearty mains
        - Snack: very small/side-like items
        - Morning snack/Afternoon snack: preserve specific snack types for 5 meals per day
        """
        try:
            t = (title or "").lower()
            mt = (meal_type or "dinner").lower()
            
            # CRITICAL FIX: Preserve specific snack types (morning snack, afternoon snack) for 5 meals per day
            if mt in ["morning snack", "afternoon snack", "evening snack"]:
                return mt
            
            def any_kw(kws):
                return any(k in t for k in kws)
            if any_kw(["oat", "pancake", "waffle", "yogurt", "smoothie", "granola", "egg", "scramble", "toast"]):
                return "breakfast"
            if any_kw(["salad", "sandwich", "wrap", "soup", "bowl", "noodle", "pasta", "rice", "quinoa"]):
                return "lunch"
            if any_kw(["snack", "bar", "bites", "hummus", "guacamole"]) and not any_kw(["bowl", "salad", "soup", "plate"]):
                return "snack"
            if mt in ["breakfast", "lunch", "dinner", "snack"]:
                return mt
            # default to dinner for mains
            return "dinner"
        except Exception:
            return meal_type or "dinner"
    
    def _infer_dietary_tags_from_ingredients(
        self, 
        ingredients: List[Dict[str, Any]], 
        existing_tags: List[str] = None, 
        title: str = ""
    ) -> List[str]:
        """Infer dietary tags from ingredient list"""
        try:
            if existing_tags is None:
                existing_tags = []
            
            # Convert to set to avoid duplicates
            tags = set(existing_tags)
            
            # Extract ingredient names (handle both dict and string formats)
            ingredient_names = []
            for ing in (ingredients or []):
                if isinstance(ing, dict):
                    name = ing.get('name', '') or ing.get('ingredient', '')
                elif isinstance(ing, str):
                    name = ing
                else:
                    continue
                if name:
                    ingredient_names.append(name.lower())
            
            # Combine with title for analysis
            text = ' '.join(ingredient_names + [title.lower() if title else ''])
            
            # Define ingredient categories
            meat_keywords = {'beef', 'pork', 'chicken', 'turkey', 'lamb', 'veal', 'duck', 'goose', 
                           'bacon', 'ham', 'sausage', 'chorizo', 'pepperoni', 'salami', 'prosciutto',
                           'ground beef', 'ground pork', 'ground turkey', 'ground lamb',
                           'steak', 'roast', 'chop', 'cutlet', 'tenderloin', 'ribs', 'wings'}
            
            fish_seafood_keywords = {'fish', 'salmon', 'tuna', 'cod', 'halibut', 'mackerel', 'sardines',
                                    'shrimp', 'prawns', 'crab', 'lobster', 'scallops', 'mussels', 'clams',
                                    'oysters', 'squid', 'octopus', 'anchovies', 'caviar', 'roe',
                                    'seafood', 'shellfish', 'crustacean', 'mollusk',
                                    'mahi-mahi', 'mahi mahi', 'dolphinfish', 'swordfish', 'tilapia',
                                    'trout', 'bass', 'perch', 'snapper', 'grouper', 'redfish'}
            
            dairy_keywords = {'milk', 'cream', 'butter', 'cheese', 'yogurt', 'sour cream', 'buttermilk',
                            'heavy cream', 'half and half', 'whipping cream', 'mascarpone', 'ricotta',
                            'mozzarella', 'cheddar', 'parmesan', 'feta', 'goat cheese', 'blue cheese'}
            
            egg_keywords = {'egg', 'eggs', 'egg white', 'egg yolk', 'whole egg', 'beaten egg'}
            
            gluten_keywords = {'wheat', 'flour', 'bread', 'pasta', 'noodles', 'couscous', 'bulgur',
                             'barley', 'rye', 'oats', 'spelt', 'kamut', 'semolina',
                             'breadcrumbs', 'panko', 'crackers', 'cereal', 'granola'}
            
            nut_keywords = {'almond', 'walnut', 'pecan', 'hazelnut', 'pistachio', 'cashew',
                          'brazil nut', 'macadamia', 'pine nut', 'peanut', 'peanut butter',
                          'almond butter', 'nut butter', 'nuts'}
            
            # CRITICAL FIX: Sesame is NOT nut-free (it's a seed allergen often grouped with nuts)
            sesame_keywords = {'sesame', 'sesame oil', 'sesame seed', 'sesame seeds', 'tahini'}
            
            soy_keywords = {'soy', 'soybean', 'tofu', 'tempeh', 'miso', 'soy sauce', 'tamari',
                          'soy milk', 'soy yogurt', 'soy cheese', 'edamame', 'soy protein'}
            
            # Check for ingredients
            has_meat = any(any(kw in ing for kw in meat_keywords) for ing in ingredient_names)
            has_fish = any(any(kw in ing for kw in fish_seafood_keywords) for ing in ingredient_names)
            has_dairy = any(any(kw in ing for kw in dairy_keywords) for ing in ingredient_names)
            has_eggs = any(any(kw in ing for kw in egg_keywords) for ing in ingredient_names)
            has_gluten = any(any(kw in ing for kw in gluten_keywords) for ing in ingredient_names)
            has_nuts = any(any(kw in ing for kw in nut_keywords) for ing in ingredient_names)
            has_sesame = any(any(kw in ing for kw in sesame_keywords) for ing in ingredient_names)
            has_soy = any(any(kw in ing for kw in soy_keywords) for ing in ingredient_names)
            
            # CRITICAL FIX: Vegetarian means NO animal products (including eggs)
            # Only add vegetarian if there's no meat, fish, OR eggs
            # Also remove vegetarian from existing tags if eggs are present
            if has_eggs:
                tags.discard('vegetarian')  # Remove vegetarian if eggs are present
                tags.discard('vegan')  # Also remove vegan if eggs are present
            
            if not has_meat and not has_fish and not has_eggs:
                tags.add('vegetarian')
                # Vegan means no animal products at all (no meat, fish, eggs, dairy)
                if not has_dairy:
                    tags.add('vegan')
            
            if not has_gluten:
                tags.add('gluten-free')
            
            if not has_dairy:
                tags.add('dairy-free')
            
            # CRITICAL FIX: Nut-free means NO nuts AND NO sesame (sesame is a seed allergen)
            if not has_nuts and not has_sesame:
                tags.add('nut-free')
            
            if not has_soy:
                tags.add('soy-free')
            
            # Add allergen warnings and content tags
            if has_dairy:
                tags.add('contains-dairy')
            if has_eggs:
                tags.add('contains-eggs')
            if has_gluten:
                tags.add('contains-gluten')
            if has_nuts:
                tags.add('contains-tree-nuts')
            if has_sesame:
                tags.add('contains-sesame')
            if has_soy:
                tags.add('contains-soy')
            if has_meat:
                tags.add('contains-meat')
            if has_fish:
                tags.add('contains-fish')
                # Also add seafood tag for shellfish/crustaceans
                if any(kw in text for kw in ['shrimp', 'prawn', 'crab', 'lobster', 'scallop', 'mussel', 'clam', 'oyster', 'shellfish', 'crustacean']):
                    tags.add('contains-seafood')
            
            return sorted(list(tags))
            
        except Exception as e:
            logger.warning(f"Error inferring dietary tags: {e}")
            return existing_tags or []
    
    def adjust_recipe_portions(self, recipe: Recipe, new_servings: float) -> Dict[str, Any]:
        """
        Adjust recipe ingredients and nutrition for different serving sizes
        All ingredient quantities are automatically recalculated and standardized
        
        Args:
            recipe: Recipe object
            new_servings: New number of servings
            
        Returns:
            Dictionary with adjusted recipe data (standardized measurements)
        """
        try:
            original_servings = recipe.servings or 1.0
            multiplier = new_servings / original_servings
            
            # Adjust ingredients with automatic standardization
            adjusted_ingredients = []
            for ri in recipe.ingredients:
                original_qty = ri.quantity
                original_unit = ri.unit or 'g'
                
                # Calculate adjusted quantity
                adjusted_quantity = original_qty * multiplier
                
                # Standardize measurement (ensures grams/ml/piece)
                standardized = self.measurement_service.standardize_ingredient_measurement(
                    ri.ingredient.name if ri.ingredient else "Unknown",
                    adjusted_quantity,
                    original_unit
                )
                
                adjusted_ingredients.append({
                    "ingredient_id": ri.ingredient_id,
                    "name": ri.ingredient.name if ri.ingredient else "Unknown",
                    "quantity": round(standardized['standardized_quantity'], 2),
                    "unit": standardized['standardized_unit'],  # Standardized (g/ml/piece)
                    "original_quantity": original_qty,
                    "original_unit": original_unit,
                    "multiplier": round(multiplier, 2),
                    "measurement_type": standardized.get('measurement_type', 'weight')
                })
            
            # Adjust nutrition (assuming we have calculated nutrition)
            nutrition_multiplier = multiplier
            adjusted_nutrition = {
                "calories": round(getattr(recipe, 'calculated_calories', 0) * nutrition_multiplier, 1),
                "protein": round(getattr(recipe, 'calculated_protein', 0) * nutrition_multiplier, 1),
                "carbs": round(getattr(recipe, 'calculated_carbs', 0) * nutrition_multiplier, 1),
                "fats": round(getattr(recipe, 'calculated_fats', 0) * nutrition_multiplier, 1),
                "fiber": round(getattr(recipe, 'calculated_fiber', 0) * nutrition_multiplier, 1),
                "sugar": round(getattr(recipe, 'calculated_sugar', 0) * nutrition_multiplier, 1),
                "sodium": round(getattr(recipe, 'calculated_sodium', 0) * nutrition_multiplier, 1)
            }
            
            return {
                "recipe_id": recipe.id,
                "title": recipe.title,
                "original_servings": original_servings,
                "new_servings": new_servings,
                "multiplier": round(multiplier, 2),
                "adjusted_ingredients": adjusted_ingredients,
                "adjusted_nutrition": adjusted_nutrition,
                "prep_time": recipe.prep_time,
                "cook_time": recipe.cook_time,
                "total_time": recipe.prep_time + recipe.cook_time
            }
            
        except Exception as e:
            logger.error(f"Error adjusting recipe portions: {str(e)}")
            return {"error": f"Failed to adjust portions: {str(e)}"}
    
    def get_portion_suggestions(self, db: Session, user_id: int, recipe: Recipe) -> Dict[str, Any]:
        """
        Get personalized portion suggestions based on user's health data
        
        Args:
            db: Database session
            user_id: User ID
            recipe: Recipe object
            
        Returns:
            Dictionary with portion suggestions
        """
        try:
            # Get personalized targets
            targets = self.calculate_personalized_targets(db, user_id)
            
            # Calculate suggested servings based on calorie target
            recipe_calories = getattr(recipe, 'calculated_calories', 0)
            if recipe_calories == 0:
                return {"error": "Recipe nutrition not calculated"}
            
            # Suggest servings to meet daily calorie target
            daily_calorie_target = targets.get("calorie_target", 2000)
            meals_per_day = 3  # Default, could be from user preferences
            
            target_calories_per_meal = daily_calorie_target / meals_per_day
            suggested_servings = target_calories_per_meal / recipe_calories
            
            # Round to reasonable serving sizes
            if suggested_servings < 0.5:
                suggested_servings = 0.5
            elif suggested_servings > 4:
                suggested_servings = 4
            else:
                suggested_servings = round(suggested_servings, 1)
            
            # Get adjusted recipe for suggested servings
            adjusted_recipe = self.adjust_recipe_portions(recipe, suggested_servings)
            
            return {
                "suggested_servings": suggested_servings,
                "reasoning": f"Based on your daily calorie target of {daily_calorie_target} calories",
                "adjusted_recipe": adjusted_recipe,
                "targets_used": targets
            }
            
        except Exception as e:
            logger.error(f"Error getting portion suggestions: {str(e)}")
            return {"error": f"Failed to get portion suggestions: {str(e)}"}
    
    def standardize_recipe_measurements(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize all measurements in a recipe to common units
        """
        try:
            return self.measurement_service.standardize_recipe_measurements(recipe_data)
        except Exception as e:
            logger.error(f"Error standardizing recipe measurements: {str(e)}")
            return recipe_data

    def _standardize_and_clean_ai_recipe(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert imperial units to metric (g/ml/kg) and drop generic placeholders.
        Preserves original text as original_text per ingredient.
        """
        ingredients = recipe_data.get("ingredients", []) or []
        cleaned: List[Dict[str, Any]] = []
        generic_terms = {"protein", "vegetables", "veggies", "spices", "herbs", "dried fruits", "sauce"}
        for item in ingredients:
            try:
                name = str((item or {}).get("name", "")).strip()
                if not name or name.lower() in generic_terms:
                    continue
                qty = (item or {}).get("quantity", None)
                unit = (item or {}).get("unit", "")
                original_text = f"{name} - {qty}{unit}"
                std = self.standardize_ingredient_measurement(name, float(qty or 0), str(unit))
                std_qty = std.get("standardized_quantity", qty)
                std_unit = std.get("standardized_unit", unit)
                if std_unit == "g" and isinstance(std_qty, (int, float)) and std_qty >= 1000:
                    std_qty = round(std_qty / 1000.0, 3)
                    std_unit = "kg"
                cleaned.append({
                    "name": name,
                    "quantity": std_qty,
                    "unit": std_unit,
                    "original_text": original_text
                })
            except Exception:
                if item:
                    item["original_text"] = f"{item.get('name','')} - {item.get('quantity','')}{item.get('unit','')}"
                    cleaned.append(item)
        recipe_data["ingredients"] = cleaned
        return recipe_data
    
    def standardize_ingredient_measurement(self, ingredient_name: str, quantity: float, unit: str) -> Dict[str, Any]:
        """
        Standardize a single ingredient measurement
        """
        try:
            return self.measurement_service.standardize_ingredient_measurement(ingredient_name, quantity, unit)
        except Exception as e:
            logger.error(f"Error standardizing ingredient measurement: {str(e)}")
            return {
                'original_quantity': quantity,
                'original_unit': unit,
                'standardized_quantity': quantity,
                'standardized_unit': unit,
                'measurement_type': 'unknown',
                'conversion_applied': False,
                'error': str(e)
            }
    
    def get_comprehensive_ai_analysis(self, db: Session, user_id: int, 
                                    start_date: date, end_date: date, 
                                    analysis_type: str = "daily") -> Dict[str, Any]:
        """
        Get comprehensive AI-driven nutritional analysis with achievements, concerns, and balance analysis
        """
        try:
            return self.ai_analysis_service.generate_comprehensive_analysis(
                db, user_id, start_date, end_date, analysis_type
            )
        except Exception as e:
            logger.error(f"Error getting comprehensive AI analysis: {str(e)}")
            return self.ai_analysis_service._generate_fallback_analysis()
    
    def get_ai_improvement_suggestions(self, db: Session, user_id: int, 
                                     start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Get comprehensive AI-driven improvement suggestions including food recommendations, timing, portions, and alternatives
        """
        try:
            return self.ai_suggestions_service.generate_comprehensive_suggestions(
                db, user_id, start_date, end_date
            )
        except Exception as e:
            logger.error(f"Error getting AI improvement suggestions: {str(e)}")
            return self.ai_suggestions_service._generate_fallback_suggestions()
    
    def optimize_meal_timing(self, db: Session, user_id: int, meal_plan: MealPlan) -> Dict[str, Any]:
        """
        Optimize meal timing based on user's activity level and preferences
        
        Args:
            db: Database session
            user_id: User ID
            meal_plan: Meal plan to optimize
            
        Returns:
            Dictionary with meal timing
        """
        try:
            # Get user's health profile and preferences
            health_profile = db.query(HealthProfile).filter(HealthProfile.user_id == user_id).first()
            nutrition_prefs = db.query(UserNutritionPreferences).filter(
                UserNutritionPreferences.user_id == user_id
            ).first()
            
            if not health_profile:
                return {"error": "Health profile not found"}
            
            activity_level = health_profile.activity_level.lower()
            preferred_meal_times = nutrition_prefs.preferred_meal_times if nutrition_prefs else {}
            timezone = nutrition_prefs.timezone if nutrition_prefs else "UTC"
            
            # Default meal times based on activity level
            default_times = {
                "sedentary": {
                    "breakfast": "08:00",
                    "lunch": "13:00", 
                    "dinner": "19:00"
                },
                "lightly_active": {
                    "breakfast": "07:30",
                    "lunch": "12:30",
                    "dinner": "18:30"
                },
                "moderately_active": {
                    "breakfast": "07:00",
                    "lunch": "12:00",
                    "dinner": "18:00"
                },
                "very_active": {
                    "breakfast": "06:30",
                    "lunch": "11:30",
                    "dinner": "17:30"
                },
                "extremely_active": {
                    "breakfast": "06:00",
                    "lunch": "11:00",
                    "dinner": "17:00"
                }
            }
            
            # Use preferred times or defaults
            meal_times = preferred_meal_times if preferred_meal_times else default_times.get(activity_level, default_times["moderately_active"])
            
            # Add snacks for high activity levels
            if activity_level in ["very_active", "extremely_active"]:
                meal_times["snack_1"] = "10:00"
                meal_times["snack_2"] = "15:00"
            
            timed_meals = []
            for meal in meal_plan.meals:
                meal_type = meal.meal_type
                meal_time = meal_times.get(meal_type, "12:00")
                
                # Adjust timing based on meal calories
                if meal.calories > 600:  # Large meal
                    # Suggest earlier for better digestion
                    if meal_type == "dinner":
                        meal_time = self._adjust_time_earlier(meal_time, 30)
                elif meal.calories < 200:  # Small meal/snack
                    # Can be more flexible
                    pass
                
                timed_meals.append({
                    "meal_id": meal.id,
                    "meal_type": meal_type,
                    "meal_name": meal.meal_name,
                    "original_time": meal.meal_time,
                    "meal_time": meal_time,
                    "calories": meal.calories,
                    "reasoning": self._get_timing_reasoning(meal_type, activity_level, meal.calories)
                })
            
            return {
                "timed_meals": timed_meals,
                "activity_level": activity_level,
                "timezone": timezone,
                "recommendations": self._get_meal_timing_recommendations(activity_level)
            }
            
        except Exception as e:
            logger.error(f"Error optimizing meal timing: {str(e)}")
            return {"error": f"Failed to optimize meal timing: {str(e)}"}
    
    def _adjust_time_earlier(self, time_str: str, minutes: int) -> str:
        """Adjust time string to be earlier by specified minutes"""
        try:
            from datetime import datetime, timedelta
            time_obj = datetime.strptime(time_str, "%H:%M")
            adjusted_time = time_obj - timedelta(minutes=minutes)
            return adjusted_time.strftime("%H:%M")
        except:
            return time_str
    
    def _get_timing_reasoning(self, meal_type: str, activity_level: str, calories: float) -> str:
        """Get reasoning for meal timing optimization"""
        if meal_type == "breakfast":
            if activity_level in ["very_active", "extremely_active"]:
                return "Early breakfast provides energy for morning activities"
            else:
                return "Standard breakfast time for your activity level"
        elif meal_type == "lunch":
            return "Midday meal to maintain energy levels"
        elif meal_type == "dinner":
            if calories > 600:
                return "Earlier dinner for better digestion of large meal"
            else:
                return "Standard dinner time"
        elif meal_type == "snack":
            return "Strategic snack timing for sustained energy"
        else:
            return "Timing based on your activity level"
    
    def _get_meal_timing_recommendations(self, activity_level: str) -> List[str]:
        """Get general meal timing recommendations"""
        recommendations = []
        
        if activity_level == "sedentary":
            level_recs = [
                "Space meals 4-5 hours apart for better digestion",
                "Avoid eating 2-3 hours before bedtime",
                "Consider smaller, more frequent meals"
            ]
        elif activity_level in ["lightly_active", "moderately_active"]:
            level_recs = [
                "Maintain consistent meal times",
                "Eat within 1 hour of waking up",
                "Have dinner 3-4 hours before bedtime"
            ]
        else:  # very_active or extremely_active
            level_recs = [
                "Eat within 30 minutes of waking up",
                "Include pre and post-workout nutrition",
                "Consider 5-6 smaller meals throughout the day",
                "Stay hydrated between meals"
            ]
        recommendations.extend(level_recs)
        
        return recommendations
    
    def update_wellness_score_from_nutrition(self, db: Session, user_id: int, analysis_period: str = "week") -> Dict[str, Any]:
        """
        Update wellness score based on nutritional intake and adherence to goals
        
        Args:
            db: Database session
            user_id: User ID
            analysis_period: Period to analyze (day, week, month)
            
        Returns:
            Dictionary with updated wellness score and factors
        """
        try:
            # Get user's health profile
            health_profile = db.query(HealthProfile).filter(HealthProfile.user_id == user_id).first()
            if not health_profile:
                return {"error": "Health profile not found"}
            
            # Calculate date range
            today = date.today()
            if analysis_period == "day":
                start_date = end_date = today
            elif analysis_period == "week":
                start_date = today - timedelta(days=6)
                end_date = today
            elif analysis_period == "month":
                start_date = today - timedelta(days=29)
                end_date = today
            else:
                start_date = end_date = today
            
            # Get nutritional analysis
            nutrition_analysis = self.get_nutritional_analysis(
                db=db,
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                analysis_type=analysis_period
            )
            
            # Get personalized targets
            targets = self.calculate_personalized_targets(db, user_id)
            
            # Calculate nutrition adherence score (0-100)
            nutrition_score = self._calculate_nutrition_adherence_score(nutrition_analysis, targets)
            
            # Calculate micronutrient diversity score
            micronutrient_score = self._calculate_micronutrient_score(db, user_id, start_date, end_date)
            
            # Calculate meal consistency score
            consistency_score = self._calculate_meal_consistency_score(db, user_id, start_date, end_date)
            
            # Calculate overall nutrition wellness score
            nutrition_wellness_score = (
                nutrition_score * 0.4 +  # 40% weight to macro adherence
                micronutrient_score * 0.3 +  # 30% weight to micronutrient diversity
                consistency_score * 0.3  # 30% weight to meal consistency
            )
            
            # Get current wellness score
            latest_metrics = db.query(MetricsHistory).filter(
                MetricsHistory.health_profile_id == health_profile.id
            ).order_by(desc(MetricsHistory.recorded_at)).first()
            
            current_wellness_score = latest_metrics.wellness_score if latest_metrics else 50
            
            # Update wellness score (weighted average with existing score)
            updated_wellness_score = (current_wellness_score * 0.7) + (nutrition_wellness_score * 0.3)
            updated_wellness_score = min(100, max(0, updated_wellness_score))
            
            # Create new metrics entry
            new_metrics = MetricsHistory(
                health_profile_id=health_profile.id,
                weight=latest_metrics.weight if latest_metrics else health_profile.weight,
                bmi=latest_metrics.bmi if latest_metrics else 0,
                wellness_score=updated_wellness_score,
                recorded_at=datetime.utcnow()
            )
            db.add(new_metrics)
            db.commit()
            
            return {
                "previous_wellness_score": current_wellness_score,
                "updated_wellness_score": round(updated_wellness_score, 1),
                "nutrition_wellness_score": round(nutrition_wellness_score, 1),
                "nutrition_score": round(nutrition_score, 1),
                "micronutrient_score": round(micronutrient_score, 1),
                "consistency_score": round(consistency_score, 1),
                "analysis_period": analysis_period,
                "factors": {
                    "macro_adherence": round(nutrition_score, 1),
                    "micronutrient_diversity": round(micronutrient_score, 1),
                    "meal_consistency": round(consistency_score, 1)
                },
                "recommendations": self._get_wellness_improvement_recommendations(
                    nutrition_score, micronutrient_score, consistency_score
                )
            }
            
        except Exception as e:
            logger.error(f"Error updating wellness score from nutrition: {str(e)}")
            return {"error": f"Failed to update wellness score: {str(e)}"}
    
    def _calculate_nutrition_adherence_score(self, analysis: Dict, targets: Dict) -> float:
        """Calculate how well user adheres to nutritional targets (0-100)"""
        try:
            percentages = analysis.get("percentages", {})
            
            # Weight different nutrients
            weights = {
                "calories": 0.4,
                "protein": 0.3,
                "carbs": 0.2,
                "fats": 0.1
            }
            
            total_score = 0
            for nutrient, weight in weights.items():
                percentage = percentages.get(nutrient, 0)
                # Optimal range is 80-120% of target
                if 80 <= percentage <= 120:
                    score = 100
                elif 70 <= percentage < 80 or 120 < percentage <= 130:
                    score = 80
                elif 60 <= percentage < 70 or 130 < percentage <= 140:
                    score = 60
                else:
                    score = max(0, 100 - abs(percentage - 100))
                
                total_score += score * weight
            
            return min(100, total_score)
            
        except Exception:
            return 50  # Default score if calculation fails
    
    def _calculate_micronutrient_score(self, db: Session, user_id: int, start_date: date, end_date: date) -> float:
        """Calculate micronutrient diversity score (0-100)"""
        try:
            # This would use the micronutrient service
            # For now, return a placeholder score
            return 75.0
        except Exception:
            return 50.0
    
    def _calculate_meal_consistency_score(self, db: Session, user_id: int, start_date: date, end_date: date) -> float:
        """Calculate meal consistency score based on regular eating patterns (0-100)"""
        try:
            # Get meal logs for the period
            logs = db.query(NutritionalLog).filter(
                and_(
                    NutritionalLog.user_id == user_id,
                    NutritionalLog.log_date >= start_date,
                    NutritionalLog.log_date <= end_date
                )
            ).all()
            
            if not logs:
                return 0
            
            # Count days with meals
            days_with_meals = len(set(log.log_date for log in logs))
            total_days = (end_date - start_date).days + 1
            
            # Base score on meal frequency
            frequency_score = (days_with_meals / total_days) * 100
            
            # Bonus for consistent meal timing (simplified)
            meal_times = [log.log_date for log in logs]
            consistency_bonus = min(20, len(set(meal_times)) * 2)
            
            return min(100, frequency_score + consistency_bonus)
            
        except Exception:
            return 50.0
    
    def _get_wellness_improvement_recommendations(self, nutrition_score: float, micronutrient_score: float, consistency_score: float) -> List[str]:
        """Get recommendations to improve wellness score"""
        recommendations = []
        
        if nutrition_score < 70:
            recommendations.append("Focus on meeting your daily calorie and macro targets")
        
        if micronutrient_score < 70:
            recommendations.append("Increase variety in your diet to improve micronutrient intake")
        
        if consistency_score < 70:
            recommendations.append("Try to eat meals at consistent times each day")
        
        if not recommendations:
            recommendations.append("Great job! Your nutrition habits are supporting your wellness goals")
        
        return recommendations
    
    def generate_enhanced_meal_plan(self, db: Session, user_id: int, plan_request: MealPlanRequest) -> Dict[str, Any]:
        """
        Generate enhanced meal plan with advanced personalization and dietary restrictions
        
        Args:
            db: Database session
            user_id: User ID
            plan_request: Meal plan generation request
            
        Returns:
            Enhanced meal plan with personalization metadata
        """
        try:
            # Get user preferences
            preferences = db.query(UserNutritionPreferences).filter(
                UserNutritionPreferences.user_id == user_id
            ).first()
            
            if not preferences:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Please set up your nutrition preferences first"
                )
            
            # Get personalized targets
            personalized_targets = self.calculate_personalized_targets(db, user_id)
            
            # Get wellness score for additional personalization
            wellness_data = self.update_wellness_score_from_nutrition(db, user_id, "week")
            
            # Build enhanced user preferences
            enhanced_preferences = {
                "dietary_preferences": preferences.dietary_preferences or [],
                "allergies": preferences.allergies or [],
                "disliked_ingredients": preferences.disliked_ingredients or [],
                "cuisine_preferences": preferences.cuisine_preferences or [],
                "daily_calorie_target": personalized_targets.get("calorie_target") or preferences.daily_calorie_target,
                "protein_target": personalized_targets.get("protein_target") or preferences.protein_target,
                "carbs_target": personalized_targets.get("carbs_target") or preferences.carbs_target,
                "fats_target": personalized_targets.get("fats_target") or preferences.fats_target,
                "meals_per_day": preferences.meals_per_day,
                "personalization_context": {
                    "bmi": personalized_targets.get("bmi"),
                    "activity_level": personalized_targets.get("activity_level"),
                    "fitness_goal": personalized_targets.get("fitness_goal"),
                    "wellness_score": wellness_data.get("wellness_score"),
                    "is_personalized": personalized_targets.get("personalized", False),
                    "age": personalized_targets.get("age"),
                    "gender": personalized_targets.get("gender"),
                    "cultural_background": preferences.cultural_background,
                    "lifestyle": preferences.lifestyle_type
                }
            }
            
            # Override with request preferences if provided
            # preferences_override may not exist on some request types
            override_prefs = getattr(plan_request, 'preferences_override', None)
            if override_prefs:
                for key, value in override_prefs.items():
                    if value is not None:
                        enhanced_preferences[key] = value
            
            # Get user behavior patterns (simplified for now)
            behavior_patterns = self._get_user_behavior_patterns(db, user_id)
            
            # Generate enhanced meal plan
            enhanced_meal_plan = self.enhanced_nutrition_ai.generate_enhanced_meal_plan(
                enhanced_preferences, plan_request, db, behavior_patterns
            )
            
            return enhanced_meal_plan
            
        except Exception as e:
            logger.error(f"Error generating enhanced meal plan: {str(e)}")
            # Fallback to regular meal plan generation
            return self._generate_fallback_meal_plan(db, user_id, plan_request)
    
    def _get_user_behavior_patterns(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """Get user behavior patterns for personalization (simplified implementation)"""
        try:
            # This is a simplified implementation - in practice, you'd analyze meal history, ratings, etc.
            # For now, return empty patterns
            return []
        except Exception as e:
            logger.error(f"Error getting user behavior patterns: {e}")
            return []
    
    def _generate_fallback_meal_plan(self, db: Session, user_id: int, plan_request: MealPlanRequest) -> Dict[str, Any]:
        """Generate fallback meal plan when enhanced features fail"""
        try:
            # Use the regular nutrition AI as fallback
            preferences = db.query(UserNutritionPreferences).filter(
                UserNutritionPreferences.user_id == user_id
            ).first()
            
            if not preferences:
                raise Exception("No preferences found")
            
            # Convert to the format expected by regular AI
            prefs_dict = {
                "dietary_preferences": preferences.dietary_preferences or [],
                "allergies": preferences.allergies or [],
                "disliked_ingredients": preferences.disliked_ingredients or [],
                "cuisine_preferences": preferences.cuisine_preferences or [],
                "daily_calorie_target": preferences.daily_calorie_target,
                "protein_target": preferences.protein_target,
                "carbs_target": preferences.carbs_target,
                "fats_target": preferences.fats_target,
                "meals_per_day": preferences.meals_per_day
            }
            
            # Generate using regular AI
            ai_meal_plan = self.nutrition_ai.generate_meal_plan_sequential(prefs_dict, plan_request, db)
            
            # Add fallback metadata
            ai_meal_plan["enhancement_metadata"] = {
                "ai_available": False,
                "fallback_mode": True,
                "enhancement_features_used": []
            }
            
            return ai_meal_plan
            
        except Exception as e:
            logger.error(f"Error in fallback meal plan generation: {e}")
            return {
                "error": "Failed to generate meal plan",
                "enhancement_metadata": {
                    "ai_available": False,
                    "fallback_mode": True,
                    "error": str(e)
                }
            }

    def create_meal_plan(self, db: Session, user_id: int, plan_request: MealPlanRequest, ai_meal_plan: Dict[str, Any]) -> MealPlan:
        """Create meal plan from AI generation with versioning support"""
        try:
            # Check if there's an existing meal plan for this date and type
            existing_plan = db.query(MealPlan).filter(
                and_(
                    MealPlan.user_id == user_id,
                    MealPlan.start_date == plan_request.start_date,
                    MealPlan.plan_type == plan_request.plan_type,
                    MealPlan.is_active == True
                )
            ).first()
            
            # If there's an existing plan, create a new version
            if existing_plan:
                new_plan_id = meal_plan_versioning_service.create_meal_plan_version(
                    db, user_id, existing_plan.id, "regenerate_plan", "New meal plan generated"
                )
                if new_plan_id:
                    # Load the newly created versioned plan instead of mutating the primary key
                    meal_plan = db.query(MealPlan).filter(MealPlan.id == new_plan_id).first()
                    should_add = False
                else:
                    # Fallback to creating new plan
                    import time
                    unique_id = f"mp_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{int(time.time() * 1000) % 10000}"
                    # Normalize weekly plan dates to start on Monday before saving
                    normalized_start = plan_request.start_date
                    normalized_end = plan_request.end_date
                    try:
                        if plan_request.plan_type == 'weekly':
                            from datetime import timedelta, datetime as _dt
                            _sd = plan_request.start_date if isinstance(plan_request.start_date, _dt) else _dt.combine(plan_request.start_date, _dt.min.time())
                            monday_date = (_sd + timedelta(days=-_sd.weekday())).date()
                            normalized_start = monday_date
                            normalized_end = monday_date + timedelta(days=6)
                    except Exception:
                        pass

                    meal_plan = MealPlan(
                        id=unique_id,
                        user_id=user_id,
                        plan_type=plan_request.plan_type,
                        start_date=normalized_start,
                        end_date=normalized_end,
                        version="1.0",
                        generation_strategy={"strategy": "balanced"},
                        ai_model_used="gpt-3.5-turbo"
                    )
                    should_add = True
            else:
                # Create new meal plan record with unique ID
                import time
                unique_id = f"mp_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{int(time.time() * 1000) % 10000}"
                # Normalize weekly plan dates to start on Monday before saving
                normalized_start = plan_request.start_date
                normalized_end = plan_request.end_date
                try:
                    if plan_request.plan_type == 'weekly':
                        from datetime import timedelta, datetime as _dt
                        _sd = plan_request.start_date if isinstance(plan_request.start_date, _dt) else _dt.combine(plan_request.start_date, _dt.min.time())
                        monday_date = (_sd + timedelta(days=-_sd.weekday())).date()
                        normalized_start = monday_date
                        normalized_end = monday_date + timedelta(days=6)
                except Exception:
                    pass

                meal_plan = MealPlan(
                    id=unique_id,
                    user_id=user_id,
                    plan_type=plan_request.plan_type,
                    start_date=normalized_start,
                    end_date=normalized_end,
                    version="1.0",
                    generation_strategy={"strategy": "balanced"},
                    ai_model_used="gpt-3.5-turbo"
                )
                should_add = True
            if 'should_add' in locals() and should_add:
                db.add(meal_plan)
                db.flush()
            else:
                # Ensure the loaded plan is attached and up-to-date
                db.flush()
            
            # Create meals and recipes
            # Handle AI output structure - meals can be nested
            meal_plan_data = ai_meal_plan.get("meal_plan", {})
            weekly_plan_data = ai_meal_plan.get("weekly_meal_plan", {})
            
            # CRITICAL DEBUG: Log the AI response structure to diagnose parsing issues
            logger.info(f"🔍 AI meal plan structure: keys={list(ai_meal_plan.keys())}")
            if weekly_plan_data:
                logger.info(f"🔍 Weekly plan data: keys={list(weekly_plan_data.keys()) if isinstance(weekly_plan_data, dict) else type(weekly_plan_data)}")
                if isinstance(weekly_plan_data, dict) and "weekly_plan" in weekly_plan_data:
                    logger.info(f"🔍 Weekly plan has {len(weekly_plan_data['weekly_plan'])} days")
                    # CRITICAL: Log meals for ALL days, not just first day
                    for day_idx, day_plan in enumerate(weekly_plan_data['weekly_plan']):
                        if isinstance(day_plan, dict):
                            day_meals = day_plan.get('meals', [])
                            logger.info(f"🔍 Day {day_idx+1}: {len(day_meals)} meals - {[m.get('meal_name', 'unnamed') for m in day_meals[:3]]}")
                        else:
                            logger.warning(f"⚠️ Day {day_idx+1} is not a dict: {type(day_plan)}")
                else:
                    logger.error(f"❌ Weekly plan data missing 'weekly_plan' key! Structure: {type(weekly_plan_data)}")
            else:
                logger.error(f"❌ No weekly_plan_data found in AI response! Available keys: {list(ai_meal_plan.keys())}")

            # If we have a weekly plan, assign meals across the 7 days starting at start_date
            if weekly_plan_data and "weekly_plan" in weekly_plan_data:
                from datetime import timedelta
                from ai.fallback_recipes import fallback_generator
                
                # CRITICAL FIX: If weekly AI generation failed (only Day 1 has meals), use individual meal generation
                # This uses the same working code path as daily generation
                days_with_meals = sum(1 for day_plan in weekly_plan_data["weekly_plan"] if isinstance(day_plan, dict) and day_plan.get('meals'))
                total_days = len(weekly_plan_data["weekly_plan"])
                
                if days_with_meals < total_days:
                    logger.warning(f"⚠️ Weekly AI generation incomplete: only {days_with_meals}/{total_days} days have meals")
                    logger.info("🔄 Switching to individual meal generation (same approach as daily generation)")
                    # Use individual meal generation for missing days (same code path as daily generation)
                    # This ensures ingredient validation and nutrition calculation work correctly
                
                # Determine base meal types from user preferences or default to 4
                # Guard: plan_request may not have preferences_override
                _override = getattr(plan_request, 'preferences_override', None)
                meals_per_day = (_override.get('meals_per_day', 4) if isinstance(_override, dict) else 4)
                def build_meal_types(meals_per_day: int) -> list:
                    if meals_per_day <= 3:
                        return ['breakfast','lunch','dinner']
                    if meals_per_day == 4:
                        return ['breakfast','lunch','dinner','snack']
                    # CRITICAL FIX: Use 'morning snack' and 'afternoon snack' for 5 meals per day to match frontend expectations
                    if meals_per_day == 5:
                        return ['breakfast','lunch','dinner','morning snack','afternoon snack']
                    # For 6+ meals, use all snack types
                    return ['breakfast','morning snack','lunch','afternoon snack','dinner','evening snack']
                base_types = build_meal_types(meals_per_day)
                _override = getattr(plan_request, 'preferences_override', None)
                # Calculate target calories per meal from daily target (default 2000 kcal/day)
                daily_target = (_override.get('daily_calorie_target', 2000) if isinstance(_override, dict) else 2000) if _override else 2000
                target_calories = int(daily_target / max(1, len(base_types)))
                
                # CRITICAL FIX: Collect all meal names from the entire meal plan to prevent duplicates across days
                all_meal_names = []
                for day_plan in weekly_plan_data["weekly_plan"]:
                    day_meals = day_plan.get("meals", []) if day_plan else []
                    all_meal_names.extend([m.get('meal_name', '') for m in day_meals if m.get('meal_name')])
                
                for day_index, day_plan in enumerate(weekly_plan_data["weekly_plan"]):
                    meal_date_for_day = plan_request.start_date + timedelta(days=day_index)
                    
                    # CRITICAL: Ensure every day has all required meals
                    day_meals = day_plan.get("meals", []) if day_plan else []
                    day_meal_names = [m.get('meal_name', '') for m in day_meals if m.get('meal_name')]
                    # CRITICAL FIX: Use all meal names from entire meal plan to prevent duplicates across days
                    used_names = list(set(all_meal_names))  # Remove duplicates
                    
                    # CRITICAL FIX: Check if all required meals are present for this day
                    # Get meal types that should exist for this meals_per_day
                    required_meal_types = build_meal_types(meals_per_day)
                    existing_meal_types = [m.get('meal_type', '').lower() for m in day_meals]
                    
                    # Check for missing meals (especially afternoon snack for 5 meals/day)
                    missing_meal_types = []
                    # Track which snack types we have
                    morning_snack_count = sum(1 for m in day_meals if m.get('meal_type', '').lower() in ['morning snack', 'snack'])
                    afternoon_snack_count = sum(1 for m in day_meals if m.get('meal_type', '').lower() == 'afternoon snack')
                    generic_snack_count = sum(1 for m in day_meals if m.get('meal_type', '').lower() == 'snack')
                    
                    for required_type in required_meal_types:
                        # For snacks, check both specific and generic types
                        if required_type == 'morning snack':
                            # Check if we have morning snack specifically, or if we have a generic snack that could be assigned
                            has_morning_snack = any(
                                m.get('meal_type', '').lower() == 'morning snack' 
                                or (m.get('recipe', {}).get('meal_type', '').lower() == 'morning snack')
                                for m in day_meals
                            )
                            # If we have generic snacks but no morning snack assigned yet, we can use one
                            if not has_morning_snack and generic_snack_count == 0:
                                missing_meal_types.append(required_type)
                        elif required_type == 'afternoon snack':
                            # CRITICAL: Check if we have afternoon snack specifically
                            has_afternoon_snack = any(
                                m.get('meal_type', '').lower() == 'afternoon snack' 
                                or (m.get('recipe', {}).get('meal_type', '').lower() == 'afternoon snack')
                                for m in day_meals
                            )
                            # CRITICAL FIX: Always add afternoon snack to missing if not found
                            # Don't try to be smart about generic snacks - just ensure we have the specific type
                            if not has_afternoon_snack:
                                missing_meal_types.append(required_type)
                                logger.warning(f"⚠️ Afternoon snack missing for day {day_index+1} - will generate fallback")
                        elif required_type in ['evening snack']:
                            # Similar logic for evening snack
                            has_evening_snack = any(
                                m.get('meal_type', '').lower() == 'evening snack' 
                                or (m.get('recipe', {}).get('meal_type', '').lower() == 'evening snack')
                                for m in day_meals
                            )
                            if not has_evening_snack:
                                missing_meal_types.append(required_type)
                        else:
                            # For non-snacks, check exact match
                            if required_type.lower() not in existing_meal_types:
                                missing_meal_types.append(required_type)
                    
                    # Log missing meals
                    if missing_meal_types:
                        logger.warning(f"⚠️ Day {day_index+1} ({meal_date_for_day}) is missing {len(missing_meal_types)} meals: {missing_meal_types}")
                        logger.warning(f"   Expected {meals_per_day} meals ({required_meal_types}), found {len(day_meals)} meals")
                    
                    # CRITICAL FIX: Fill missing meal types for this day
                    # First, ensure meal_type is set on all existing meals
                    generic_snacks = []  # Track generic 'snack' meals that need conversion
                    for meal_data in day_meals:
                        if not meal_data.get('meal_type'):
                            # Try to infer from meal name or default
                            meal_name_lower = (meal_data.get('meal_name') or '').lower()
                            if any(word in meal_name_lower for word in ['breakfast', 'morning', 'cereal', 'oatmeal', 'pancake', 'waffle', 'egg']):
                                meal_data['meal_type'] = 'breakfast'
                            elif any(word in meal_name_lower for word in ['lunch', 'noon', 'salad', 'sandwich']):
                                meal_data['meal_type'] = 'lunch'
                            elif any(word in meal_name_lower for word in ['snack', 'hummus', 'trail', 'nuts']):
                                meal_data['meal_type'] = 'snack'
                            else:
                                meal_data['meal_type'] = 'dinner'  # Default
                        
                        # Collect generic 'snack' meals for conversion
                        if meals_per_day == 5 and meal_data.get('meal_type') == 'snack':
                            generic_snacks.append(meal_data)
                    
                    # CRITICAL FIX: Convert generic 'snack' to specific snack types for 5 meals per day
                    # Check which snack types we already have
                    has_morning_snack = any(
                        m.get('meal_type', '').lower() == 'morning snack' 
                        or (m.get('recipe', {}).get('meal_type', '').lower() == 'morning snack')
                        for m in day_meals
                    )
                    has_afternoon_snack = any(
                        m.get('meal_type', '').lower() == 'afternoon snack' 
                        or (m.get('recipe', {}).get('meal_type', '').lower() == 'afternoon snack')
                        for m in day_meals
                    )
                    
                    # Convert generic snacks to specific types
                    # Priority: assign to missing types first
                    for i, snack_meal in enumerate(generic_snacks):
                        if not has_morning_snack:
                            # Assign first generic snack to morning snack
                            snack_meal['meal_type'] = 'morning snack'
                            if snack_meal.get('recipe'):
                                snack_meal['recipe']['meal_type'] = 'morning snack'
                            has_morning_snack = True
                            logger.info(f"✅ Converted generic snack {i+1} to 'morning snack' for day {day_index+1}")
                        elif not has_afternoon_snack:
                            # Assign second generic snack to afternoon snack
                            snack_meal['meal_type'] = 'afternoon snack'
                            if snack_meal.get('recipe'):
                                snack_meal['recipe']['meal_type'] = 'afternoon snack'
                            has_afternoon_snack = True
                            logger.info(f"✅ Converted generic snack {i+1} to 'afternoon snack' for day {day_index+1}")
                        else:
                            # Both slots filled, but we have extra snacks - keep as generic (shouldn't happen)
                            logger.warning(f"⚠️ Extra generic snack found for day {day_index+1} - both morning and afternoon snacks already assigned")
                    
                    # CRITICAL FIX: Re-check meal types after conversion (snack conversion might have changed things)
                    meal_types_present = {m.get('meal_type', '').strip().lower() for m in day_meals if m.get('meal_type')}
                    # Also check recipe_details.meal_type for preserved types
                    for m in day_meals:
                        if m.get('recipe', {}).get('meal_type'):
                            meal_types_present.add(m.get('recipe', {}).get('meal_type', '').strip().lower())
                    
                    # Find missing types - check against base_types (which are lowercase)
                    missing_types = []
                    for mt in base_types:
                        mt_lower = mt.lower()
                        # Check if we have this exact type
                        if mt_lower not in meal_types_present:
                            missing_types.append(mt)
                    
                    # CRITICAL: Log what we have vs what we need
                    logger.info(f"📊 Day {day_index+1} ({meal_date_for_day}): Have {len(day_meals)} meals, need {len(base_types)}")
                    logger.info(f"   Present types: {sorted(meal_types_present)}")
                    logger.info(f"   Required types: {sorted([mt.lower() for mt in base_types])}")
                    logger.info(f"   Missing types: {missing_types}")
                    
                    # CRITICAL: Ensure we have exactly len(base_types) meals for this day
                    for mt in missing_types:
                        # Generate fallback meal for missing type
                        logger.warning(f"Missing {mt} for day {day_index+1} ({meal_date_for_day}) - generating fallback")
                        # CRITICAL FIX: Use all_meal_names to prevent duplicates across days
                        fallback = fallback_generator.generate_unique_recipe(mt, target_calories, 'International', used_names, db=db)
                        if 'recipe' not in fallback:
                            fallback['recipe'] = {}
                        # CRITICAL: Set meal_type explicitly
                        fallback['meal_type'] = mt
                        # CRITICAL: Detect AI-only mode from existing meals
                        ai_count_day = sum(1 for m in day_meals if (m.get('recipe') or {}).get('ai_generated') == True)
                        db_count_day = len(day_meals) - ai_count_day
                        is_ai_only_day = db_count_day == 0 and ai_count_day > 0
                        if is_ai_only_day:
                            # AI-ONLY MODE: Mark fallback as AI
                            fallback['recipe']['ai_generated'] = True
                            fallback['recipe']['database_source'] = False
                            fallback['ai_generated'] = True
                        else:
                            # 50/50 MODE: Maintain balance - check current day balance
                            current_ai_count = sum(1 for m in day_meals if (m.get('recipe') or {}).get('ai_generated') == True)
                            target_ai = len(base_types) // 2
                            if current_ai_count < target_ai:
                                fallback['recipe']['ai_generated'] = True
                                fallback['recipe']['database_source'] = False
                            else:
                                fallback['recipe']['ai_generated'] = False
                                fallback['recipe']['database_source'] = True
                        day_meals.append(fallback)
                        fallback_name = fallback.get('meal_name', '')
                        if fallback_name:
                            used_names.append(fallback_name)
                            # CRITICAL FIX: Update all_meal_names to prevent duplicates across days
                            all_meal_names.append(fallback_name)
                    
                    # CRITICAL: Final validation - ensure we have exactly len(base_types) meals
                    if len(day_meals) < len(base_types):
                        logger.error(f"CRITICAL: Day {day_index+1} ({meal_date_for_day}) only has {len(day_meals)} meals but need {len(base_types)} - filling remaining")
                        meal_types_present_now = {m.get('meal_type', '').strip().lower() for m in day_meals if m.get('meal_type')}
                        # Also check recipe_details.meal_type
                        for m in day_meals:
                            if m.get('recipe', {}).get('meal_type'):
                                meal_types_present_now.add(m.get('recipe', {}).get('meal_type', '').strip().lower())
                        
                        for mt in base_types:
                            mt_lower = mt.lower()
                            if mt_lower not in meal_types_present_now:
                                logger.error(f"Still missing {mt} for day {day_index+1} - generating emergency fallback")
                                fallback = fallback_generator.generate_unique_recipe(mt, target_calories, 'International', used_names, db=db)
                                if 'recipe' not in fallback:
                                    fallback['recipe'] = {}
                                fallback['meal_type'] = mt
                                # CRITICAL: Detect AI-only mode from existing meals
                                ai_count_emergency = sum(1 for m in day_meals if (m.get('recipe') or {}).get('ai_generated') == True)
                                db_count_emergency = len(day_meals) - ai_count_emergency
                                is_ai_only_emergency = db_count_emergency == 0 and ai_count_emergency > 0
                                if is_ai_only_emergency:
                                    # AI-ONLY MODE: Mark fallback as AI
                                    fallback['recipe']['ai_generated'] = True
                                    fallback['recipe']['database_source'] = False
                                    fallback['ai_generated'] = True
                                else:
                                    # 50/50 MODE: Balance AI/DB
                                    current_ai = sum(1 for m in day_meals if (m.get('recipe') or {}).get('ai_generated') == True)
                                    if current_ai < len(base_types) // 2:
                                        fallback['recipe']['ai_generated'] = True
                                        fallback['recipe']['database_source'] = False
                                    else:
                                        fallback['recipe']['ai_generated'] = False
                                        fallback['recipe']['database_source'] = True
                                day_meals.append(fallback)
                                used_names.append(fallback.get('meal_name', ''))
                    
                    # CRITICAL: Final check before processing - ensure we have exactly the right number of meals
                    final_meal_types_check = {m.get('meal_type', '').strip().lower() for m in day_meals if m.get('meal_type')}
                    # Also check recipe_details.meal_type
                    for m in day_meals:
                        if m.get('recipe', {}).get('meal_type'):
                            final_meal_types_check.add(m.get('recipe', {}).get('meal_type', '').strip().lower())
                    
                    # CRITICAL FIX: If we still don't have all required meals, generate them now
                    if len(day_meals) < len(base_types) or len(final_meal_types_check) < len(base_types):
                        logger.error(f"FATAL: Day {day_index+1} ({meal_date_for_day}) has {len(day_meals)} meals ({sorted(final_meal_types_check)}) but need {len(base_types)} ({sorted([mt.lower() for mt in base_types])}) - generating missing meals")
                        for mt in base_types:
                            mt_lower = mt.lower()
                            if mt_lower not in final_meal_types_check:
                                logger.error(f"🔴 CRITICAL: Still missing {mt} for day {day_index+1} - generating final fallback")
                                fallback = fallback_generator.generate_unique_recipe(mt, target_calories, 'International', used_names, db=db)
                                if 'recipe' not in fallback:
                                    fallback['recipe'] = {}
                                fallback['meal_type'] = mt
                                # Mark as AI-generated to match other meals
                                fallback['recipe']['ai_generated'] = True
                                fallback['recipe']['database_source'] = False
                                fallback['ai_generated'] = True
                                day_meals.append(fallback)
                                used_names.append(fallback.get('meal_name', ''))
                                final_meal_types_check.add(mt_lower)
                                logger.info(f"✅ Generated final fallback for {mt} on day {day_index+1}")
                    
                    # Final validation
                    if len(day_meals) != len(base_types):
                        logger.error(f"FATAL: Day {day_index+1} ({meal_date_for_day}) STILL has {len(day_meals)} meals but need {len(base_types)} - THIS SHOULD NOT HAPPEN")
                    
                    # Process all meals for this day (including filled ones)
                    for meal_data in day_meals:
                        recipe_data = meal_data.get("recipe", {})
                        # If missing detailed recipe, synthesize one quickly
                        if not recipe_data:
                            try:
                                # Use target_calories from context or estimate from meal type
                                meal_type_for_gen = meal_data.get('meal_type', 'dinner')
                                default_cal_by_type = {'breakfast': 400, 'lunch': 500, 'dinner': 600, 'snack': 200}
                                meal_target_cal = meal_data.get('calories') or default_cal_by_type.get(meal_type_for_gen, 500)
                                # Use sequential RAG method (task.md compliant) with fast fallback
                                try:
                                    quick_meal = self.nutrition_ai._generate_single_meal_with_sequential_rag({
                                        'meal_type': meal_type_for_gen,
                                        'target_calories': int(meal_target_cal),
                                        'target_cuisine': meal_data.get('cuisine') or 'International',
                                        'user_preferences': {},
                                        'existing_meals': []
                                    }, db)
                                except Exception:
                                    # Fallback to fast generation if sequential fails
                                    quick_meal = self.nutrition_ai._generate_single_meal_fast({
                                        'meal_type': meal_type_for_gen,
                                        'target_calories': int(meal_target_cal),
                                        'target_cuisine': meal_data.get('cuisine') or 'International',
                                        'user_preferences': {},
                                        'existing_meals': []
                                    })
                                recipe_data = quick_meal.get('recipe', {}) or {}
                                # CRITICAL: Ensure AI flag is set on quick-generated meals
                                if 'recipe' not in quick_meal:
                                    quick_meal['recipe'] = {}
                                if 'recipe' not in recipe_data:
                                    recipe_data = quick_meal.get('recipe', {}) or {}
                                # Quick meals are always AI-generated
                                recipe_data['ai_generated'] = True
                                recipe_data['database_source'] = False
                                # backfill nutrition onto meal_data for totals
                                if 'nutrition' in recipe_data:
                                    nd = recipe_data['nutrition']
                                    meal_data['calories'] = nd.get('calories', meal_data.get('calories', 0))
                                    meal_data['protein'] = nd.get('protein', meal_data.get('protein', 0))
                                    meal_data['carbs'] = nd.get('carbs', meal_data.get('carbs', 0))
                                    meal_data['fats'] = nd.get('fats', meal_data.get('fats', 0))
                            except Exception:
                                recipe_data = {}

                        # ROOT CAUSE FIX: Preserve specific snack types BEFORE sanitization
                        # Check if meal_type is already a specific snack type (morning snack, afternoon snack)
                        original_meal_type = meal_data.get('meal_type', '').strip()
                        is_specific_snack = original_meal_type.lower() in ['morning snack', 'afternoon snack', 'evening snack']
                        
                        # Sanitize meal type and dietary tags (but preserve specific snack types)
                        if is_specific_snack:
                            # Don't sanitize specific snack types - preserve them
                            sanitized_meal_type = original_meal_type
                        else:
                            sanitized_meal_type = self._sanitize_meal_type(
                                meal_data.get("meal_type", "dinner"),
                                recipe_data.get("title", meal_data.get("meal_name", "")),
                                recipe_data.get("ingredients", [])
                            )
                        
                        corrected_tags = self._infer_dietary_tags_from_ingredients(
                            recipe_data.get("ingredients", []),
                            recipe_data.get("dietary_tags", []),
                            recipe_data.get("title", meal_data.get("meal_name", ""))
                        )
                        recipe_data["dietary_tags"] = corrected_tags
                        
                        servings = recipe_data.get("servings", 1) or 1
                        
                        # ROOT CAUSE FIX: ALWAYS recalculate nutrition from ingredients if available
                        # Don't trust AI's placeholder values (452, 28, 50, 15) - calculate from actual ingredients
                        nutrition_data = None
                        ingredients_list = recipe_data.get("ingredients", [])
                        if ingredients_list and len(ingredients_list) > 0:
                            try:
                                # Calculate from actual ingredients using ingredient database
                                calculated_nutrition = self.nutrition_ai._calculate_recipe_nutrition(
                                    ingredients_list, db
                                )
                                if calculated_nutrition and calculated_nutrition.get('calories', 0) > 0:
                                    # Use calculated nutrition (accurate)
                                    nutrition_data = {
                                        "calories": int(calculated_nutrition.get('calories', 0)),
                                        "protein": round(calculated_nutrition.get('protein', 0), 1),
                                        "carbs": round(calculated_nutrition.get('carbs', 0), 1),
                                        "fats": round(calculated_nutrition.get('fats', 0), 1),
                                        "per_serving_calories": int(calculated_nutrition.get('calories', 0)),
                                        "per_serving_protein": round(calculated_nutrition.get('protein', 0), 1),
                                        "per_serving_carbs": round(calculated_nutrition.get('carbs', 0), 1),
                                        "per_serving_fats": round(calculated_nutrition.get('fats', 0), 1)
                                    }
                                    logger.info(f"✅ Calculated nutrition from {len(ingredients_list)} ingredients: {nutrition_data.get('calories', 0)} cal, {nutrition_data.get('protein', 0)}g protein, {nutrition_data.get('carbs', 0)}g carbs, {nutrition_data.get('fats', 0)}g fats")
                                else:
                                    logger.warning(f"⚠️ Nutrition calculation returned 0 calories for meal '{meal_data.get('meal_name', 'unknown')}' with {len(ingredients_list)} ingredients")
                            except Exception as e:
                                logger.error(f"⚠️ Failed to calculate nutrition from ingredients for meal '{meal_data.get('meal_name', 'unknown')}': {e}", exc_info=True)
                        else:
                            logger.warning(f"⚠️ No ingredients available for nutrition calculation for meal '{meal_data.get('meal_name', 'unknown')}'")
                        
                        # Fallback to estimate if calculation failed
                        if not nutrition_data:
                            nutrition_data = recipe_data.get("nutrition", {})
                            # If nutrition is missing or zeros, estimate from ingredients
                            if not nutrition_data or all(not nutrition_data.get(k) for k in ["calories","protein","carbs","fats"]):
                                nutrition_data = self._estimate_nutrition_from_ingredients(recipe_data.get("ingredients", []))
                        
                        recipe_data["nutrition"] = nutrition_data
                        
                        # CRITICAL FIX: Ensure nutrition is PER-SERVING, not total
                        # If nutrition looks like total (> 500 cal and servings > 1), divide by servings
                        if nutrition_data.get("calories") and servings > 1 and nutrition_data.get("calories", 0) > 500:
                            # Likely total calories, convert to per-serving
                            nutrition_data["per_serving_calories"] = int(nutrition_data["calories"] / servings)
                            nutrition_data["per_serving_protein"] = round(nutrition_data.get("protein", 0) / servings, 1)
                            nutrition_data["per_serving_carbs"] = round(nutrition_data.get("carbs", 0) / servings, 1)
                            nutrition_data["per_serving_fats"] = round(nutrition_data.get("fats", 0) / servings, 1)
                            # Update main values to per-serving
                            nutrition_data["calories"] = nutrition_data["per_serving_calories"]
                            nutrition_data["protein"] = nutrition_data["per_serving_protein"]
                            nutrition_data["carbs"] = nutrition_data["per_serving_carbs"]
                            nutrition_data["fats"] = nutrition_data["per_serving_fats"]
                        else:
                            # Ensure per-serving fields exist
                            nutrition_data["per_serving_calories"] = nutrition_data.get("calories", 0)
                            nutrition_data["per_serving_protein"] = nutrition_data.get("protein", 0)
                            nutrition_data["per_serving_carbs"] = nutrition_data.get("carbs", 0)
                            nutrition_data["per_serving_fats"] = nutrition_data.get("fats", 0)
                        
                        # CRITICAL: Preserve AI flag from recipe_data - don't override it!
                        # The flag should already be correctly set from hybrid generator
                        if recipe_data:
                            # Check if flag exists - if missing, infer from database_source
                            if "ai_generated" not in recipe_data:
                                # Only infer if flag is missing - preserve explicit flags
                                has_database_source = recipe_data.get("database_source", False)
                                recipe_data["ai_generated"] = not bool(has_database_source)
                            # Ensure database_source is consistent
                            if "database_source" not in recipe_data:
                                recipe_data["database_source"] = not bool(recipe_data.get("ai_generated", False))

                        if recipe_data.get("ai_generated", False):
                            try:
                                # CRITICAL FIX: Ensure recipe_data is a dict, not a string
                                if isinstance(recipe_data, str):
                                    import json
                                    try:
                                        recipe_data = json.loads(recipe_data)
                                    except:
                                        logger.error(f"Failed to parse recipe_data as JSON when creating recipe")
                                        recipe_data = {}
                                if not isinstance(recipe_data, dict):
                                    logger.error(f"recipe_data is not a dict when creating recipe, got {type(recipe_data)}")
                                    recipe_data = {}
                                
                                # Ensure meal_type is present on recipe for persistence
                                recipe_data.setdefault("meal_type", sanitized_meal_type)
                                created_recipe = self._create_recipe_from_ai(db, recipe_data)
                                if created_recipe:
                                    recipe_data["database_source"] = False
                                    recipe_data["title"] = created_recipe.title or recipe_data.get("title")
                            except Exception as _:
                                pass

                        # Use PER-SERVING calories for meal
                        meal_calories = nutrition_data.get("per_serving_calories") or nutrition_data.get("calories", 0)
                        meal_protein = nutrition_data.get("per_serving_protein") or nutrition_data.get("protein", 0)
                        meal_carbs = nutrition_data.get("per_serving_carbs") or nutrition_data.get("carbs", 0)
                        meal_fats = nutrition_data.get("per_serving_fats") or nutrition_data.get("fats", 0)
                        
                        # CRITICAL: Ensure meal_type is set - if not, use sanitized_meal_type or fallback
                        # CRITICAL FIX: Preserve specific snack types (already preserved in sanitized_meal_type if is_specific_snack)
                        if is_specific_snack:
                            # Use the preserved specific snack type
                            final_meal_type = sanitized_meal_type
                        else:
                            # Use sanitized_meal_type or fallback
                            final_meal_type = sanitized_meal_type or original_meal_type or 'dinner'
                        
                        # CRITICAL FIX: Allow specific snack types in validation
                        valid_meal_types = ['breakfast', 'lunch', 'dinner', 'snack', 'morning snack', 'afternoon snack', 'evening snack']
                        if not final_meal_type or final_meal_type.strip() not in valid_meal_types:
                            logger.warning(f"Invalid meal_type '{final_meal_type}' for meal '{meal_data.get('meal_name')}' on day {day_index+1}, defaulting to 'dinner'")
                            final_meal_type = 'dinner'
                        else:
                            final_meal_type = final_meal_type.strip()
                        
                        try:
                            # CRITICAL FIX: Strip ID numbers from meal names (e.g., "Asian Sunrise Stir-Fry 2030" -> "Asian Sunrise Stir-Fry")
                            # CRITICAL FIX: Check for duplicate base names (normalized) across the entire meal plan
                            # This prevents the AI from bypassing duplicate detection by appending ID numbers
                            import re
                            
                            def clean_meal_name(name: str) -> str:
                                """Remove trailing ID numbers from meal names"""
                                if not name:
                                    return name
                                # Remove trailing numbers (4+ digits) that look like IDs
                                # Pattern: space followed by 4+ digits at the end
                                cleaned = re.sub(r'\s+\d{4,}$', '', name.strip())
                                return cleaned if cleaned else name
                            
                            def normalize_meal_name(name: str) -> str:
                                """Normalize meal name for duplicate detection (remove IDs, suffixes, etc.)"""
                                if not name:
                                    return ""
                                # Remove trailing numbers (4+ digits) that look like IDs
                                normalized = re.sub(r'\s+\d{4,}$', '', name.strip())
                                # Remove common suffixes that create duplicates
                                normalized = re.sub(r'\s+(Special|Deluxe|Gourmet|Premium|Artisan|Ultimate|Classic|Traditional)$', '', normalized, flags=re.IGNORECASE)
                                return normalized.lower().strip()
                            
                            # ROOT CAUSE FIX: Get meal name and clean it
                            raw_meal_name = meal_data.get("meal_name", recipe_data.get("title", "Meal"))
                            cleaned_meal_name = clean_meal_name(raw_meal_name)
                            normalized_cleaned_name = normalize_meal_name(cleaned_meal_name)
                            
                            # CRITICAL FIX: Only check for duplicates on the SAME DAY, not across all days
                            # The same meal can be eaten on different days, so we should allow duplicates across days
                            existing_meals_same_day = db.query(MealPlanMeal).filter(
                                MealPlanMeal.meal_plan_id == meal_plan.id,
                                MealPlanMeal.meal_date == meal_date_for_day
                            ).all()
                            
                            duplicate_found = False
                            for existing_meal_check in existing_meals_same_day:
                                existing_normalized = normalize_meal_name(existing_meal_check.meal_name)
                                if existing_normalized == normalized_cleaned_name and existing_normalized:
                                    duplicate_found = True
                                    logger.warning(f"⚠️ DUPLICATE DETECTED: '{cleaned_meal_name}' (normalized: '{normalized_cleaned_name}') matches existing meal '{existing_meal_check.meal_name}' (normalized: '{existing_normalized}') on the same day - rejecting duplicate")
                                    break
                            
                            if duplicate_found:
                                # CRITICAL FIX: Instead of rejecting, generate a new unique meal
                                logger.warning(f"⚠️ Duplicate meal name '{cleaned_meal_name}' (normalized: '{normalized_cleaned_name}') detected on same day - generating new unique meal instead of rejecting")
                                # Generate a new unique meal for this slot
                                try:
                                    fallback = fallback_generator.generate_unique_recipe(
                                        final_meal_type, 
                                        target_calories, 
                                        recipe_data.get('cuisine', 'International'), 
                                        used_names, 
                                        db=db
                                    )
                                    if 'recipe' not in fallback:
                                        fallback['recipe'] = {}
                                    fallback['meal_type'] = final_meal_type
                                    # Update meal_data with the new unique meal
                                    meal_data['meal_name'] = fallback.get('meal_name', cleaned_meal_name)
                                    recipe_data = fallback.get('recipe', {})
                                    # Mark as AI-generated to match other meals
                                    recipe_data['ai_generated'] = True
                                    recipe_data['database_source'] = False
                                    # Update cleaned_meal_name for the rest of the processing
                                    cleaned_meal_name = fallback.get('meal_name', cleaned_meal_name)
                                    normalized_cleaned_name = normalize_meal_name(cleaned_meal_name)
                                    logger.info(f"✅ Generated new unique meal '{cleaned_meal_name}' to replace duplicate")
                                except Exception as gen_err:
                                    logger.error(f"❌ CRITICAL: Failed to generate replacement meal for duplicate '{cleaned_meal_name}' (type: {final_meal_type}): {gen_err}")
                                    # CRITICAL FIX: Don't skip the meal - use a simple fallback instead
                                    # Create a minimal meal to ensure the slot is filled
                                    logger.warning(f"⚠️ Using emergency fallback for {final_meal_type} on day {day_index+1}")
                                    meal_data['meal_name'] = f"{final_meal_type.title()} Meal"
                                    recipe_data = {
                                        'title': meal_data['meal_name'],
                                        'ingredients': [],
                                        'instructions': [],
                                        'nutrition': {
                                            'calories': target_calories,
                                            'protein': int(target_calories * 0.25 / 4),
                                            'carbs': int(target_calories * 0.45 / 4),
                                            'fats': int(target_calories * 0.30 / 9)
                                        },
                                        'ai_generated': True,
                                        'database_source': False
                                    }
                                    cleaned_meal_name = meal_data['meal_name']
                                    normalized_cleaned_name = normalize_meal_name(cleaned_meal_name)
                                    logger.warning(f"⚠️ Using emergency fallback meal for {final_meal_type} - meal will be generated but may need manual adjustment")
                            
                            # CRITICAL: Check if meal already exists for this date/type to prevent duplicates
                            existing_meal = db.query(MealPlanMeal).filter(
                                MealPlanMeal.meal_plan_id == meal_plan.id,
                                MealPlanMeal.meal_date == meal_date_for_day,
                                MealPlanMeal.meal_type == final_meal_type
                            ).first()
                            
                            if existing_meal:
                                # Update existing meal instead of creating duplicate
                                logger.warning(f"Meal already exists for day {day_index+1} ({meal_date_for_day}), type {final_meal_type} - updating instead of creating duplicate")
                                meal = existing_meal
                                meal.meal_name = cleaned_meal_name
                                meal.calories = meal_calories
                                meal.protein = meal_protein
                                meal.carbs = meal_carbs
                                meal.fats = meal_fats
                            else:
                                # Create new meal
                                meal = MealPlanMeal(
                                    meal_plan_id=meal_plan.id,
                                    meal_date=meal_date_for_day,
                                    meal_type=final_meal_type,
                                    meal_name=cleaned_meal_name,
                                    calories=meal_calories,  # PER-SERVING
                                    protein=meal_protein,
                                    carbs=meal_carbs,
                                    fats=meal_fats
                                )
                                db.add(meal)
                            db.flush()
                            
                            # CRITICAL: Verify meal was added
                            if not meal.id:
                                logger.error(f"🔴 Meal not properly added for day {day_index+1} ({meal_date_for_day}), type {final_meal_type}, name: {meal.meal_name}")
                            else:
                                logger.info(f"✅ Added meal: Day {day_index+1} ({meal_date_for_day}), type '{final_meal_type}', name '{meal.meal_name}', ID: {meal.id}, calories: {meal.calories}")
                                # CRITICAL: Log afternoon snack specifically
                                if final_meal_type.lower() == 'afternoon snack':
                                    logger.info(f"🎯 AFTERNOON SNACK SAVED: Day {day_index+1}, ID: {meal.id}, name: {meal.meal_name}, type: {meal.meal_type}")
                                
                                # CRITICAL FIX: Preserve original meal_type in recipe_details for frontend slot assignment
                                if recipe_data:
                                    recipe_data['meal_type'] = final_meal_type  # Preserve specific snack types (morning snack, afternoon snack)
                        except Exception as meal_err:
                            logger.error(f"❌ CRITICAL ERROR adding meal for day {day_index+1} ({meal_date_for_day}), type {final_meal_type}: {meal_err}", exc_info=True)
                            # CRITICAL FIX: Don't skip the meal - try to create a minimal meal to ensure the slot is filled
                            try:
                                logger.warning(f"⚠️ Attempting emergency meal creation for {final_meal_type} on day {day_index+1}")
                                emergency_meal = MealPlanMeal(
                                    meal_plan_id=meal_plan.id,
                                    meal_date=meal_date_for_day,
                                    meal_type=final_meal_type,
                                    meal_name=f"{final_meal_type.title()} Meal",
                                    calories=target_calories,
                                    protein=int(target_calories * 0.25 / 4),
                                    carbs=int(target_calories * 0.45 / 4),
                                    fats=int(target_calories * 0.30 / 9),
                                    recipe_details={
                                        'title': f"{final_meal_type.title()} Meal",
                                        'ingredients': [],
                                        'instructions': [],
                                        'nutrition': {
                                            'calories': target_calories,
                                            'protein': int(target_calories * 0.25 / 4),
                                            'carbs': int(target_calories * 0.45 / 4),
                                            'fats': int(target_calories * 0.30 / 9)
                                        },
                                        'ai_generated': True,
                                        'database_source': False
                                    }
                                )
                                db.add(emergency_meal)
                                db.flush()
                                logger.warning(f"⚠️ Created emergency meal for {final_meal_type} on day {day_index+1} (ID: {emergency_meal.id}) - user should regenerate this meal")
                            except Exception as emergency_err:
                                logger.error(f"❌ FATAL: Even emergency meal creation failed for {final_meal_type} on day {day_index+1}: {emergency_err}", exc_info=True)
                                # Only skip if emergency creation also fails
                                continue
                        if recipe_data:
                            # CRITICAL: Ensure ai_generated flag is explicitly set in recipe_details
                            # Default to AI (True) in AI-only mode if flag is missing
                            ai_flag_raw = recipe_data.get("ai_generated")
                            # Check if explicitly set (True or False), or if we need to infer
                            if ai_flag_raw is None or ai_flag_raw not in [True, False]:
                                # Flag is missing - check if database_source is explicitly True
                                has_explicit_db = recipe_data.get("database_source", False) == True
                                if has_explicit_db:
                                    ai_flag = False  # Explicitly marked as database
                                    logger.debug(f"Inferred ai_generated=False for meal '{meal_data.get('meal_name')}' (has explicit database_source=True)")
                                else:
                                    # No explicit flags - default to AI (AI-only mode)
                                    ai_flag = True
                                    logger.warning(f"Missing ai_generated flag for meal '{meal_data.get('meal_name')}' - defaulting to AI (True) in AI-only mode")
                            else:
                                ai_flag = bool(ai_flag_raw)
                            
                            # Ensure flags are consistent
                            if ai_flag:
                                recipe_data["ai_generated"] = True
                                recipe_data["database_source"] = False
                            else:
                                recipe_data["ai_generated"] = False
                                recipe_data["database_source"] = True
                            
                            meal.recipe_details = {
                                "title": recipe_data.get("title", meal_data.get("meal_name", "Meal")),
                                "cuisine": recipe_data.get("cuisine", ""),
                                "prep_time": recipe_data.get("prep_time", 0),
                                "cook_time": recipe_data.get("cook_time", 0),
                                "servings": servings,
                                "difficulty": recipe_data.get("difficulty", "easy"),
                                "ingredients": recipe_data.get("ingredients", []),
                                "instructions": recipe_data.get("instructions", []),
                                "dietary_tags": recipe_data.get("dietary_tags", []),
                                "nutrition": nutrition_data,
                                "ai_generated": ai_flag,  # Explicitly set AI flag
                                "database_source": not ai_flag,  # Explicitly set database flag
                                "meal_type": final_meal_type  # CRITICAL FIX: Preserve specific snack types (morning snack, afternoon snack) for frontend slot assignment
                            }
                            logger.debug(f"💾 Saved meal '{meal_data.get('meal_name')}' with ai_generated={ai_flag}, database_source={not ai_flag}")
                            meal.cuisine = recipe_data.get("cuisine", "")
            else:
                # Handle non-weekly structures by defaulting all meals to start_date
                meals_data = []
                if "meal_plan" in meal_plan_data and isinstance(meal_plan_data["meal_plan"], list):
                    for day_plan in meal_plan_data["meal_plan"]:
                        if "meals" in day_plan:
                            meals_data.extend(day_plan["meals"])
                else:
                    meals_data = meal_plan_data.get("meals", [])

                for meal_data in meals_data:
                    recipe_data = meal_data.get("recipe", {})
                    # If missing detailed recipe, synthesize one quickly
                    if not recipe_data:
                        try:
                            # Use target_calories from context or estimate from meal type
                            meal_type_for_gen = meal_data.get('meal_type', 'dinner')
                            default_cal_by_type = {'breakfast': 400, 'lunch': 500, 'dinner': 600, 'snack': 200}
                            meal_target_cal = meal_data.get('calories') or default_cal_by_type.get(meal_type_for_gen, 500)
                            # Use sequential RAG method (task.md compliant) with fast fallback
                            try:
                                quick_meal = self.nutrition_ai._generate_single_meal_with_sequential_rag({
                                    'meal_type': meal_type_for_gen,
                                    'target_calories': int(meal_target_cal),
                                    'target_cuisine': meal_data.get('cuisine') or 'International',
                                    'user_preferences': {},
                                    'existing_meals': []
                                }, db)
                            except Exception:
                                # Fallback to fast generation if sequential fails
                                quick_meal = self.nutrition_ai._generate_single_meal_fast({
                                    'meal_type': meal_type_for_gen,
                                    'target_calories': int(meal_target_cal),
                                    'target_cuisine': meal_data.get('cuisine') or 'International',
                                    'user_preferences': {},
                                    'existing_meals': []
                                })
                            recipe_data = quick_meal.get('recipe', {}) or {}
                            # CRITICAL: Ensure AI flag is set on quick-generated meals
                            if 'recipe' not in quick_meal:
                                quick_meal['recipe'] = {}
                            if 'recipe' not in recipe_data or not recipe_data:
                                recipe_data = quick_meal.get('recipe', {}) or {}
                            # Quick meals are always AI-generated
                            recipe_data['ai_generated'] = True
                            recipe_data['database_source'] = False
                            if 'nutrition' in recipe_data:
                                nd = recipe_data['nutrition']
                                meal_data['calories'] = nd.get('calories', meal_data.get('calories', 0))
                                meal_data['protein'] = nd.get('protein', meal_data.get('protein', 0))
                                meal_data['carbs'] = nd.get('carbs', meal_data.get('carbs', 0))
                                meal_data['fats'] = nd.get('fats', meal_data.get('fats', 0))
                        except Exception:
                            recipe_data = {}

                    # Sanitize meal type and dietary tags
                    sanitized_meal_type = self._sanitize_meal_type(
                        meal_data.get("meal_type", "dinner"),
                        recipe_data.get("title", meal_data.get("meal_name", "")),
                        recipe_data.get("ingredients", [])
                    )
                    corrected_tags = self._infer_dietary_tags_from_ingredients(
                        recipe_data.get("ingredients", []),
                        recipe_data.get("dietary_tags", []),
                        recipe_data.get("title", meal_data.get("meal_name", ""))
                    )
                    recipe_data["dietary_tags"] = corrected_tags
                    nutrition_data = recipe_data.get("nutrition", {})
                    servings = recipe_data.get("servings", 1) or 1
                    # Estimate if nutrition missing or zeros
                    if not nutrition_data or all(not nutrition_data.get(k) for k in ["calories","protein","carbs","fats"]):
                        nutrition_data = self._estimate_nutrition_from_ingredients(recipe_data.get("ingredients", []))
                        recipe_data["nutrition"] = nutrition_data
                    
                    # CRITICAL FIX: Ensure nutrition is PER-SERVING, not total
                    if nutrition_data.get("calories") and servings > 1 and nutrition_data.get("calories", 0) > 500:
                        # Likely total calories, convert to per-serving
                        nutrition_data["per_serving_calories"] = int(nutrition_data["calories"] / servings)
                        nutrition_data["per_serving_protein"] = round(nutrition_data.get("protein", 0) / servings, 1)
                        nutrition_data["per_serving_carbs"] = round(nutrition_data.get("carbs", 0) / servings, 1)
                        nutrition_data["per_serving_fats"] = round(nutrition_data.get("fats", 0) / servings, 1)
                        nutrition_data["calories"] = nutrition_data["per_serving_calories"]
                        nutrition_data["protein"] = nutrition_data["per_serving_protein"]
                        nutrition_data["carbs"] = nutrition_data["per_serving_carbs"]
                        nutrition_data["fats"] = nutrition_data["per_serving_fats"]
                    else:
                        nutrition_data["per_serving_calories"] = nutrition_data.get("calories", 0)
                        nutrition_data["per_serving_protein"] = nutrition_data.get("protein", 0)
                        nutrition_data["per_serving_carbs"] = nutrition_data.get("carbs", 0)
                        nutrition_data["per_serving_fats"] = nutrition_data.get("fats", 0)
                    
                    # CRITICAL: Preserve AI flag from recipe_data - don't override it!
                    # The flag should already be correctly set from hybrid generator
                    if recipe_data:
                        # Check if flag exists - if missing, infer from database_source
                        if "ai_generated" not in recipe_data:
                            # Only infer if flag is missing - preserve explicit flags
                            has_database_source = recipe_data.get("database_source", False)
                            recipe_data["ai_generated"] = not bool(has_database_source)
                        # Ensure database_source is consistent
                        if "database_source" not in recipe_data:
                            recipe_data["database_source"] = not bool(recipe_data.get("ai_generated", False))

                    if recipe_data.get("ai_generated", False):
                        try:
                            # CRITICAL FIX: Ensure recipe_data is a dict, not a string
                            if isinstance(recipe_data, str):
                                import json
                                try:
                                    recipe_data = json.loads(recipe_data)
                                except:
                                    logger.error(f"Failed to parse recipe_data as JSON when creating recipe")
                                    recipe_data = {}
                            if not isinstance(recipe_data, dict):
                                logger.error(f"recipe_data is not a dict when creating recipe, got {type(recipe_data)}")
                                recipe_data = {}
                            
                            recipe_data.setdefault("meal_type", sanitized_meal_type)
                            created_recipe = self._create_recipe_from_ai(db, recipe_data)
                            if created_recipe:
                                recipe_data["database_source"] = False
                                recipe_data["title"] = created_recipe.title or recipe_data.get("title")
                        except Exception as _:
                            pass

                    # Use PER-SERVING calories for meal
                    meal_calories = nutrition_data.get("per_serving_calories") or nutrition_data.get("calories", 0)
                    meal_protein = nutrition_data.get("per_serving_protein") or nutrition_data.get("protein", 0)
                    meal_carbs = nutrition_data.get("per_serving_carbs") or nutrition_data.get("carbs", 0)
                    meal_fats = nutrition_data.get("per_serving_fats") or nutrition_data.get("fats", 0)
                    
                    meal = MealPlanMeal(
                        meal_plan_id=meal_plan.id,
                        meal_date=plan_request.start_date,
                        meal_type=sanitized_meal_type,
                        meal_name=meal_data.get("meal_name", recipe_data.get("title", "Meal")),
                        calories=meal_calories,  # PER-SERVING
                        protein=meal_protein,
                        carbs=meal_carbs,
                        fats=meal_fats
                    )
                    db.add(meal)
                    db.flush()
                    if recipe_data:
                        # CRITICAL: Ensure ai_generated flag is explicitly set
                        ai_flag = bool(recipe_data.get("ai_generated", False))
                        meal.recipe_details = {
                            "title": recipe_data.get("title", meal_data.get("meal_name", "Meal")),
                            "cuisine": recipe_data.get("cuisine", ""),
                            "prep_time": recipe_data.get("prep_time", 0),
                            "cook_time": recipe_data.get("cook_time", 0),
                            "servings": servings,
                            "difficulty": recipe_data.get("difficulty", "easy"),
                            "ingredients": recipe_data.get("ingredients", []),
                            "instructions": recipe_data.get("instructions", []),
                            "dietary_tags": recipe_data.get("dietary_tags", []),
                            "nutrition": nutrition_data,
                            "ai_generated": ai_flag,  # Explicitly set AI flag
                            "database_source": not ai_flag  # Explicitly set database flag
                        }
                        meal.cuisine = recipe_data.get("cuisine", "")
            
            # CRITICAL: Commit all meals to database
            db.commit()
            db.refresh(meal_plan)
            
            # CRITICAL: Verify meals were saved
            saved_meals_count = db.query(MealPlanMeal).filter(
                MealPlanMeal.meal_plan_id == meal_plan.id
            ).count()
            
            # ROOT CAUSE FIX: Don't validate meal count for progressive meal plans (empty structure)
            # Progressive generation starts empty and is filled one slot at a time
            is_progressive_plan = False
            generation_strategy = getattr(meal_plan, 'generation_strategy', None) or {}
            if isinstance(generation_strategy, dict):
                is_progressive_plan = generation_strategy.get('strategy') == 'progressive' or generation_strategy.get('mode') == 'empty_structure'
            
            # Only validate meal count for bulk-generated meal plans (not progressive)
            if meal_plan.plan_type == 'weekly' and not is_progressive_plan:
                # ROOT CAUSE FIX: Calculate expected count based on actual meals_per_day, not hardcoded 4
                # Get meals_per_day from preferences or default to 4
                meals_per_day = 4  # Default
                if hasattr(meal_plan, 'generation_strategy') and isinstance(meal_plan.generation_strategy, dict):
                    prefs_override = meal_plan.generation_strategy.get('preferences_override', {})
                    if isinstance(prefs_override, dict):
                        meals_per_day = prefs_override.get('meals_per_day', 4)
                
                expected_count = 7 * meals_per_day  # 7 days × meals_per_day
                if saved_meals_count < expected_count:
                    logger.warning(f"Only saved {saved_meals_count}/{expected_count} meals for weekly meal plan {meal_plan.id} (expected {meals_per_day} meals/day)")
                    # Try to count by meal_date to see distribution
                    from sqlalchemy import func
                    date_counts = db.query(
                        MealPlanMeal.meal_date,
                        func.count(MealPlanMeal.id).label('count')
                    ).filter(
                        MealPlanMeal.meal_plan_id == meal_plan.id
                    ).group_by(MealPlanMeal.meal_date).all()
                    logger.warning(f"   Date distribution: {dict(date_counts)}")
                    
                    # CRITICAL: Check for afternoon snacks specifically
                    afternoon_snacks = db.query(MealPlanMeal).filter(
                        MealPlanMeal.meal_plan_id == meal_plan.id,
                        MealPlanMeal.meal_type == 'afternoon snack'
                    ).count()
                    logger.warning(f"   Afternoon snacks saved: {afternoon_snacks} (expected: {7 if meals_per_day >= 5 else 0})")
                    
                    # Determine base meal types for validation (same logic as generation)
                    def build_meal_types(meals_per_day: int) -> list:
                        if meals_per_day <= 3:
                            return ['breakfast','lunch','dinner']
                        if meals_per_day == 4:
                            return ['breakfast','lunch','dinner','snack']
                        return ['breakfast','snack','lunch','snack','dinner']
                    
                    # Get meals_per_day from plan request or defaults
                    _override = getattr(plan_request, 'preferences_override', None)
                    meals_per_day = (_override.get('meals_per_day', 4) if isinstance(_override, dict) else 4) if _override else 4
                    base_types = build_meal_types(meals_per_day)
                    
                    # Calculate target calories for fallback generation
                    daily_target = (_override.get('daily_calorie_target', 2000) if isinstance(_override, dict) else 2000) if _override else 2000
                    target_calories = int(daily_target / max(1, len(base_types)))
                    
                    # CRITICAL: Check which days/meal types are missing and fill them
                    # CRITICAL FIX: Always check for breakfast first (most important meal)
                    for day_idx in range(7):
                        day_date = meal_plan.start_date + timedelta(days=day_idx)
                        # CRITICAL: Always check breakfast first
                        breakfast_exists = db.query(MealPlanMeal).filter(
                            MealPlanMeal.meal_plan_id == meal_plan.id,
                            MealPlanMeal.meal_date == day_date,
                            MealPlanMeal.meal_type == 'breakfast'
                        ).first()
                        if not breakfast_exists:
                            logger.error(f"🔴 CRITICAL: MISSING BREAKFAST for Day {day_idx+1} ({day_date}) - generating emergency fallback")
                            try:
                                from ai.fallback_recipes import fallback_generator
                                all_used = [m.meal_name for m in db.query(MealPlanMeal).filter(MealPlanMeal.meal_plan_id == meal_plan.id).all()]
                                fallback = fallback_generator.generate_unique_recipe('breakfast', target_calories, 'International', all_used, db=db)
                                if 'recipe' not in fallback:
                                    fallback['recipe'] = {}
                                fallback['meal_type'] = 'breakfast'
                                
                                # Create missing breakfast
                                fallback_cal = fallback.get('calories') or 400
                                missing_meal = MealPlanMeal(
                                    meal_plan_id=meal_plan.id,
                                    meal_date=day_date,
                                    meal_type='breakfast',
                                    meal_name=fallback.get('meal_name', 'Breakfast Meal'),
                                    calories=fallback_cal,
                                    protein=fallback.get('protein', 0),
                                    carbs=fallback.get('carbs', 0),
                                    fats=fallback.get('fats', 0)
                                )
                                db.add(missing_meal)
                                db.flush()
                                if fallback.get('recipe'):
                                    missing_meal.recipe_details = fallback['recipe']
                                logger.info(f"✅ Created emergency breakfast for day {day_idx+1} ({day_date})")
                            except Exception as fill_err:
                                logger.error(f"❌ FATAL: Failed to create emergency breakfast for day {day_idx+1}: {fill_err}", exc_info=True)
                        
                        # Check other meal types
                        for meal_type in base_types:
                            if meal_type == 'breakfast':
                                continue  # Already checked above
                            existing = db.query(MealPlanMeal).filter(
                                MealPlanMeal.meal_plan_id == meal_plan.id,
                                MealPlanMeal.meal_date == day_date,
                                MealPlanMeal.meal_type == meal_type
                            ).first()
                            if not existing:
                                logger.error(f"MISSING MEAL: Day {day_idx+1} ({day_date}), type {meal_type} - generating emergency fallback")
                                try:
                                    from ai.fallback_recipes import fallback_generator
                                    all_used = [m.meal_name for m in db.query(MealPlanMeal).filter(MealPlanMeal.meal_plan_id == meal_plan.id).all()]
                                    fallback = fallback_generator.generate_unique_recipe(meal_type, target_calories, 'International', all_used)
                                    if 'recipe' not in fallback:
                                        fallback['recipe'] = {}
                                    fallback['meal_type'] = meal_type
                                    
                                    # Create missing meal
                                    # Use fallback calories, or estimate from meal type if missing
                                    fallback_cal = fallback.get('calories')
                                    if not fallback_cal or fallback_cal <= 0:
                                        default_cal_by_type = {'breakfast': 400, 'lunch': 500, 'dinner': 600, 'snack': 200}
                                        fallback_cal = default_cal_by_type.get(meal_type, 500)
                                    missing_meal = MealPlanMeal(
                                        meal_plan_id=meal_plan.id,
                                        meal_date=day_date,
                                        meal_type=meal_type,
                                        meal_name=fallback.get('meal_name', f'{meal_type.title()} Meal'),
                                        calories=fallback_cal,
                                        protein=fallback.get('protein', 0),
                                        carbs=fallback.get('carbs', 0),
                                        fats=fallback.get('fats', 0)
                                    )
                                    db.add(missing_meal)
                                    db.flush()
                                    if fallback.get('recipe'):
                                        missing_meal.recipe_details = fallback['recipe']
                                    logger.info(f"Created emergency fallback meal for day {day_idx+1}, {meal_type}")
                                except Exception as fill_err:
                                    logger.error(f"Failed to create emergency fallback: {fill_err}")
                    
                    # Commit any emergency fixes
                    db.commit()
                    
                    # Recheck count
                    saved_meals_count = db.query(MealPlanMeal).filter(
                        MealPlanMeal.meal_plan_id == meal_plan.id
                    ).count()
                    if saved_meals_count >= expected_count:
                        logger.info(f"After emergency fixes: {saved_meals_count} meals saved (expected {expected_count})")
                    else:
                        logger.error(f"Still missing meals after emergency fixes: {saved_meals_count}/{expected_count}")
                else:
                    logger.info(f"Saved {saved_meals_count} meals to database for meal plan {meal_plan.id} (expected {expected_count})")
            else:
                logger.info(f"Saved {saved_meals_count} meals to database for meal plan {meal_plan.id}")
            
            # Reload meal plan with meals relationship using explicit query
            # CRITICAL: Use joinedload to ensure all meals are loaded
            from sqlalchemy.orm import joinedload
            meal_plan = db.query(MealPlan).options(
                joinedload(MealPlan.meals)
            ).filter(MealPlan.id == meal_plan.id).first()
            
            # Verify meals are loaded
            if meal_plan:
                meals_loaded = len(list(meal_plan.meals)) if hasattr(meal_plan, 'meals') else 0
                logger.info(f"Reloaded meal plan {meal_plan.id} with {meals_loaded} meals in memory")
            
            return meal_plan
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating meal plan: {str(e)}")
            raise
    
    def _create_recipe_from_ai(self, db: Session, recipe_data: Dict[str, Any]) -> Optional[Recipe]:
        """Create recipe from AI-generated data"""
        try:
            # CRITICAL FIX: Ensure recipe_data is a dict, not a string
            if isinstance(recipe_data, str):
                import json
                try:
                    recipe_data = json.loads(recipe_data)
                except:
                    logger.error(f"Failed to parse recipe_data as JSON: {recipe_data[:100] if len(str(recipe_data)) > 100 else recipe_data}")
                    return None
            if not isinstance(recipe_data, dict):
                logger.error(f"recipe_data is not a dict, got {type(recipe_data)}: {recipe_data}")
                return None
            
            # CRITICAL FIX: Generate unique recipe ID with more entropy
            # Include timestamp (with microseconds), meal name hash, and random component
            import time
            import random
            title_hash = hash(recipe_data.get('title', '') or '') % 10000
            meal_type_hash = hash(recipe_data.get('meal_type', '') or '') % 1000
            random_component = random.randint(1000, 9999)
            unique_id = f"r_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}_{title_hash}_{meal_type_hash}_{random_component}"
            
            recipe = Recipe(
                id=unique_id,
                title=recipe_data.get("title", "Generated Recipe"),
                cuisine=recipe_data.get("cuisine", "International"),
                meal_type=recipe_data.get("meal_type", "dinner"),
                servings=recipe_data.get("servings", 2),
                summary=recipe_data.get("summary", ""),
                prep_time=recipe_data.get("prep_time", 15),
                cook_time=recipe_data.get("cook_time", 30),
                difficulty_level=recipe_data.get("difficulty_level", "easy"),
                dietary_tags=recipe_data.get("dietary_tags", []),
                source="ai-generated"
            )
            db.add(recipe)
            db.flush()
            
            # CRITICAL: Always add ingredients and instructions - these are required for complete recipes
            ingredients_data = recipe_data.get("ingredients", [])
            instructions_data = recipe_data.get("instructions", [])
            
            logger.info(f"Creating recipe {recipe.id} with {len(ingredients_data)} ingredients and {len(instructions_data)} instructions")
            
            # Add ingredients and instructions (with error handling)
            try:
                self._add_recipe_ingredients(db, recipe.id, ingredients_data)
                self._add_recipe_instructions(db, recipe.id, instructions_data)
                
                # Commit to ensure ingredients/instructions are saved
                db.commit()
                db.refresh(recipe)
                
                # Verify ingredients/instructions were saved
                from models.recipe import RecipeIngredient, RecipeInstruction
                saved_ingredients = db.query(RecipeIngredient).filter(RecipeIngredient.recipe_id == recipe.id).count()
                saved_instructions = db.query(RecipeInstruction).filter(RecipeInstruction.recipe_id == recipe.id).count()
                
                logger.info(f"✅ Recipe {recipe.id} created: {saved_ingredients} ingredients, {saved_instructions} instructions saved")
                
                if saved_ingredients == 0 and len(ingredients_data) > 0:
                    logger.error(f"⚠️ CRITICAL: Recipe {recipe.id} created but NO ingredients were saved despite {len(ingredients_data)} provided!")
                if saved_instructions == 0 and len(instructions_data) > 0:
                    logger.error(f"⚠️ CRITICAL: Recipe {recipe.id} created but NO instructions were saved despite {len(instructions_data)} provided!")
                    
            except Exception as e:
                logger.error(f"CRITICAL: Failed to add ingredients/instructions to recipe {recipe.id}: {str(e)}", exc_info=True)
                db.rollback()
                # Don't raise - allow recipe to be created even if ingredients/instructions fail
                # But log the error so we can fix it
            
            return recipe
            
        except Exception as e:
            logger.error(f"Error creating recipe from AI: {str(e)}")
            return None
    
    def _add_recipe_ingredients(self, db: Session, recipe_id: str, ingredients_data: List[Dict[str, Any]]):
        """Add ingredients to recipe - CRITICAL: Always saves ingredients"""
        if not ingredients_data:
            logger.warning(f"No ingredients data provided for recipe {recipe_id}")
            return
        
        try:
            ingredients_added = 0
            for ing_data in ingredients_data:
                try:
                    if not isinstance(ing_data, dict):
                        logger.warning(f"Invalid ingredient data format for recipe {recipe_id}: {ing_data}")
                        continue
                    
                    ingredient_name = ing_data.get("name", "").strip()
                    if not ingredient_name:
                        logger.warning(f"Empty ingredient name for recipe {recipe_id}, skipping")
                        continue
                    
                    # Find or create ingredient
                    ingredient = db.query(Ingredient).filter(
                        Ingredient.name.ilike(f"%{ingredient_name}%")
                    ).first()
                    
                    if not ingredient:
                        # Create new ingredient
                        ingredient = Ingredient(
                            id=f"ing_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{abs(hash(ingredient_name)) % 10000}",
                            name=ingredient_name,
                            category=self._categorize_ingredient(ingredient_name),
                            unit=ing_data.get("unit", "g"),
                            default_quantity=100.0
                        )
                        db.add(ingredient)
                        db.flush()
                    
                    # Create recipe-ingredient relationship
                    from models.recipe import RecipeIngredient
                    recipe_ingredient = RecipeIngredient(
                        recipe_id=recipe_id,
                        ingredient_id=ingredient.id,
                        quantity=ing_data.get("quantity", 0),
                        unit=ing_data.get("unit", "g")
                    )
                    db.add(recipe_ingredient)
                    ingredients_added += 1
                except Exception as e:
                    logger.error(f"Error adding ingredient '{ing_data.get('name', 'unknown')}' to recipe {recipe_id}: {str(e)}", exc_info=True)
                    continue
            
            logger.info(f"✅ Added {ingredients_added}/{len(ingredients_data)} ingredients to recipe {recipe_id}")
            if ingredients_added == 0:
                logger.error(f"⚠️ CRITICAL: No ingredients were added to recipe {recipe_id} despite {len(ingredients_data)} provided!")
        except Exception as e:
            logger.error(f"CRITICAL: Failed to add ingredients to recipe {recipe_id}: {str(e)}", exc_info=True)
            raise  # Re-raise to prevent recipe creation without ingredients
    
    def _add_recipe_instructions(self, db: Session, recipe_id: str, instructions_data: List[Dict[str, Any]]):
        """Add instructions to recipe - CRITICAL: Always saves instructions"""
        if not instructions_data:
            logger.warning(f"No instructions data provided for recipe {recipe_id}")
            return
        
        try:
            instructions_added = 0
            for i, inst_data in enumerate(instructions_data, 1):
                try:
                    # Handle both dict and string formats
                    if isinstance(inst_data, str):
                        description = inst_data.strip()
                        step_title = f"Step {i}"
                    elif isinstance(inst_data, dict):
                        description = inst_data.get("description", inst_data.get("text", "")).strip()
                        step_title = inst_data.get("step_title", f"Step {i}")
                    else:
                        logger.warning(f"Invalid instruction data format for recipe {recipe_id} step {i}: {inst_data}")
                        continue
                    
                    if not description:
                        logger.warning(f"Empty instruction description for recipe {recipe_id} step {i}, skipping")
                        continue
                    
                    from models.recipe import RecipeInstruction
                    instruction = RecipeInstruction(
                        recipe_id=recipe_id,
                        step_number=i,
                        step_title=step_title,
                        description=description,
                        ingredients_used=inst_data.get("ingredients_used", []) if isinstance(inst_data, dict) else [],
                        time_required=inst_data.get("time_required") if isinstance(inst_data, dict) else None
                    )
                    db.add(instruction)
                    instructions_added += 1
                except Exception as e:
                    logger.error(f"Error adding instruction step {i} to recipe {recipe_id}: {str(e)}", exc_info=True)
                    continue
            
            logger.info(f"✅ Added {instructions_added}/{len(instructions_data)} instructions to recipe {recipe_id}")
            if instructions_added == 0:
                logger.error(f"⚠️ CRITICAL: No instructions were added to recipe {recipe_id} despite {len(instructions_data)} provided!")
        except Exception as e:
            logger.error(f"CRITICAL: Failed to add instructions to recipe {recipe_id}: {str(e)}", exc_info=True)
            raise  # Re-raise to prevent recipe creation without instructions
    
    def _categorize_ingredient(self, ingredient_name: str) -> str:
        """Categorize ingredient based on name"""
        name_lower = ingredient_name.lower()
        
        if any(word in name_lower for word in ["meat", "chicken", "beef", "pork", "fish", "salmon", "tuna"]):
            return "protein"
        elif any(word in name_lower for word in ["milk", "cheese", "yogurt", "butter", "cream"]):
            return "dairy"
        elif any(word in name_lower for word in ["rice", "pasta", "bread", "flour", "oats", "quinoa"]):
            return "grains"
        elif any(word in name_lower for word in ["tomato", "onion", "carrot", "broccoli", "spinach", "lettuce"]):
            return "vegetables"
        elif any(word in name_lower for word in ["apple", "banana", "orange", "berry", "fruit"]):
            return "fruits"
        elif any(word in name_lower for word in ["oil", "olive", "coconut", "avocado"]):
            return "fats"
        else:
            return "other"
    
    def _vector_similarity_search(self, query_text: str, db: Session, limit: int = 50) -> List[Dict[str, Any]]:
        """Fallback implementation when embedding service is unavailable.
        Performs a simple text search over title/summary and returns top results.
        """
        try:
            if not query_text:
                return []
            q = query_text.strip()
            # Basic ranking heuristic: prefer title matches over summary
            title_hits = db.query(Recipe).filter(
                and_(Recipe.is_active == True, Recipe.title.ilike(f"%{q}%"))
            ).limit(limit).all()
            remaining = max(0, limit - len(title_hits))
            summary_hits = []
            if remaining > 0:
                summary_hits = db.query(Recipe).filter(
                    and_(Recipe.is_active == True, Recipe.summary.ilike(f"%{q}%"))
                ).limit(remaining).all()
            results = []
            for r in title_hits + summary_hits:
                results.append({
                    "id": r.id,
                    "title": r.title,
                    "score": 1.0  # placeholder score
                })
            return results[:limit]
        except Exception:
            return []

    def _calculate_recipe_nutrition(self, recipe: Recipe) -> None:
        """Populate calculated_* fields on a Recipe for search sorting.
        Uses per-serving macros when available; otherwise leaves zeros.
        """
        try:
            # Prefer explicit per-serving fields if present
            cal = getattr(recipe, 'per_serving_calories', None)
            pro = getattr(recipe, 'per_serving_protein', None)
            car = getattr(recipe, 'per_serving_carbs', None)
            fat = getattr(recipe, 'per_serving_fat', None)

            recipe.calculated_calories = float(cal or 0)
            recipe.calculated_protein = float(pro or 0)
            recipe.calculated_carbs = float(car or 0)
            recipe.calculated_fats = float(fat or 0)
        except Exception:
            recipe.calculated_calories = 0.0
            recipe.calculated_protein = 0.0
            recipe.calculated_carbs = 0.0
            recipe.calculated_fats = 0.0
    
    def search_recipes(self, db: Session, search_request: RecipeSearchRequest) -> Dict[str, Any]:
        """Search recipes with filters"""
        try:
            # ROOT CAUSE FIX: Detect database type for JSON array queries
            db_url = str(db.bind.url) if hasattr(db, 'bind') and db.bind else ''
            is_postgresql = 'postgresql' in db_url.lower() or 'postgres' in db_url.lower()
            
            query = db.query(Recipe).filter(Recipe.is_active == True)
            
            # Handle recipe_id if provided (for direct recipe lookup)
            recipe_id = getattr(search_request, 'recipe_id', None)
            if recipe_id:
                query = query.filter(Recipe.id == recipe_id)
            
            if search_request.query:
                # Use database-level full-text search for better performance
                search_term = search_request.query.strip()
                
                # Handle special search patterns for reviewers
                if search_term.startswith('#') and search_term[1:].isdigit():
                    # Search for exact recipe number (e.g., "#1" -> "recipe_001")
                    recipe_number = search_term[1:].zfill(3)  # Convert "1" to "001"
                    recipe_id_pattern = f"recipe_{recipe_number}"
                    query = query.filter(Recipe.id == recipe_id_pattern)
                elif search_term.startswith('r') and search_term[1:].isdigit():
                    # Search for recipe ID pattern (e.g., "r1" -> "recipe_001")
                    recipe_number = search_term[1:].zfill(3)  # Convert "1" to "001"
                    recipe_id_pattern = f"recipe_{recipe_number}"
                    query = query.filter(Recipe.id == recipe_id_pattern)
                elif search_term.isdigit():
                    # Search for recipe number without prefix (e.g., "1" -> "recipe_001")
                    recipe_number = search_term.zfill(3)  # Convert "1" to "001"
                    recipe_id_pattern = f"recipe_{recipe_number}"
                    query = query.filter(Recipe.id == recipe_id_pattern)
                elif search_term.startswith('range:'):
                    # Range search for reviewers (e.g., "range:1-10", "range:50-100")
                    try:
                        range_part = search_term.replace('range:', '').strip()
                        if '-' in range_part:
                            start_num, end_num = range_part.split('-')
                            start_num = int(start_num.strip())
                            end_num = int(end_num.strip())
                            
                            # Create list of recipe IDs in range
                            recipe_ids = [f"recipe_{str(i).zfill(3)}" for i in range(start_num, end_num + 1)]
                            query = query.filter(Recipe.id.in_(recipe_ids))
                        else:
                            # Single number range (e.g., "range:5" -> recipes 1-5)
                            end_num = int(range_part.strip())
                            recipe_ids = [f"recipe_{str(i).zfill(3)}" for i in range(1, end_num + 1)]
                            query = query.filter(Recipe.id.in_(recipe_ids))
                    except (ValueError, IndexError):
                        # If range parsing fails, fall back to regular search
                        query = query.filter(
                            or_(
                                Recipe.title.ilike(f"%{search_term}%"),
                                Recipe.summary.ilike(f"%{search_term}%"),
                                Recipe.id.ilike(f"%{search_term}%")
                            )
                        )
                elif search_term.startswith('last:'):
                    # Get last N recipes (e.g., "last:10" -> last 10 recipes)
                    try:
                        count = int(search_term.replace('last:', '').strip())
                        # For last: queries, we need to get the total count of all recipes
                        # and then apply pagination normally
                        query = query.order_by(Recipe.id.desc())
                    except ValueError:
                        # If parsing fails, fall back to regular search
                        query = query.filter(
                            or_(
                                Recipe.title.ilike(f"%{search_term}%"),
                                Recipe.summary.ilike(f"%{search_term}%"),
                                Recipe.id.ilike(f"%{search_term}%")
                            )
                        )
                elif search_term.startswith('first:'):
                    # Get first N recipes (e.g., "first:10" -> first 10 recipes)
                    try:
                        count = int(search_term.replace('first:', '').strip())
                        # For first: queries, we need to get the total count of all recipes
                        # and then apply pagination normally
                        query = query.order_by(Recipe.id.asc())
                    except ValueError:
                        # If parsing fails, fall back to regular search
                        query = query.filter(
                            or_(
                                Recipe.title.ilike(f"%{search_term}%"),
                                Recipe.summary.ilike(f"%{search_term}%"),
                                Recipe.id.ilike(f"%{search_term}%")
                            )
                        )
                else:
                    # Use vector similarity search for semantic search
                    similar_recipes = self._vector_similarity_search(search_term, db, limit=50)
                    if similar_recipes:
                        # Get recipe IDs from similarity search
                        similar_recipe_ids = [recipe['id'] for recipe in similar_recipes]
                        query = query.filter(Recipe.id.in_(similar_recipe_ids))
                    else:
                        # Fallback to regular text search if vector search fails
                        query = query.filter(
                            or_(
                                Recipe.title.ilike(f"%{search_term}%"),
                                Recipe.summary.ilike(f"%{search_term}%"),
                                Recipe.id.ilike(f"%{search_term}%")
                            )
                        )
            
            if search_request.cuisine:
                query = query.filter(Recipe.cuisine.ilike(f"%{search_request.cuisine}%"))
            
            if search_request.meal_type:
                query = query.filter(Recipe.meal_type == search_request.meal_type)
            
            if search_request.dietary_tags:
                # ROOT CAUSE FIX: Use proper JSON array contains check
                def json_array_contains(column, value):
                    """Check if a JSON array column contains a specific string value"""
                    if is_postgresql:
                        # PostgreSQL: use JSONB @> operator
                        return column.op('@>')(text(f"'[\"{value}\"]'::jsonb"))
                    else:
                        # SQLite or other: use LIKE for JSON array strings
                        return func.cast(column, String).like(f'%"{value}"%')
                
                for tag in search_request.dietary_tags:
                    query = query.filter(json_array_contains(Recipe.dietary_tags, tag))
            
            # ROOT CAUSE FIX: Always apply allergy filtering for safety, regardless of query
            # Apply dietary preferences filtering when explicitly set in search filters
            if search_request.user_preferences:
                prefs = search_request.user_preferences
                
                # ROOT CAUSE FIX: Always filter allergies for safety, even without search query
                if prefs.allergies and len(prefs.allergies) > 0:
                    for allergy in prefs.allergies:
                        allergy_lower = allergy.lower()
                        # Check for contains-{allergy} tag (e.g., contains-eggs, contains-tree-nuts)
                        allergen_tag = f"contains-{allergy_lower}"
                        # Also check for contains-{allergy} with underscores (e.g., contains-tree_nuts)
                        allergen_tag_alt = f"contains-{allergy_lower.replace('-', '_')}"
                        # ROOT CAUSE FIX: Use proper JSON array contains check for allergens
                        def json_array_contains(column, value):
                            """Check if a JSON array column contains a specific string value"""
                            if is_postgresql:
                                # PostgreSQL: use JSONB @> operator
                                return column.op('@>')(text(f"'[\"{value}\"]'::jsonb"))
                            else:
                                # SQLite or other: use LIKE for JSON array strings
                                return func.cast(column, String).like(f'%"{value}"%')
                        
                        # Filter out recipes that have the allergen tag
                        query = query.filter(
                            ~json_array_contains(Recipe.dietary_tags, allergen_tag),
                            ~json_array_contains(Recipe.dietary_tags, allergen_tag_alt),
                            ~json_array_contains(Recipe.dietary_tags, allergy_lower)
                        )
                        # ROOT CAUSE FIX: Also check recipe text for allergens (for recipes without proper tags)
                        # Use case-insensitive matching to catch allergens in title/summary
                        query = query.filter(
                            ~func.lower(Recipe.title).like(f"%{allergy_lower}%"),
                            ~func.lower(Recipe.summary).like(f"%{allergy_lower}%")
                        )
                
                # ROOT CAUSE FIX: Apply dietary preferences filtering when explicitly set
                # Only filter by dietary preferences if they're explicitly set in the search (not just from user prefs)
                # This allows browsing all recipes when no dietary filters are selected
                if prefs.dietary_preferences and len(prefs.dietary_preferences) > 0:
                    dietary_conditions = []
                    
                    # ROOT CAUSE FIX: SQLAlchemy's contains() for JSON arrays doesn't work correctly
                    # We need to use a database-agnostic approach to check if a JSON array contains a string value
                    # For PostgreSQL: use @> operator for JSONB
                    # For SQLite: use LIKE or JSON functions
                    def json_array_contains(column, value):
                        """Check if a JSON array column contains a specific string value"""
                        if is_postgresql:
                            # PostgreSQL: use JSONB @> operator
                            return column.op('@>')(text(f"'[\"{value}\"]'::jsonb"))
                        else:
                            # SQLite or other: use LIKE for JSON array strings
                            # JSON arrays are stored as strings like '["vegetarian", "gluten-free"]'
                            return func.cast(column, String).like(f'%"{value}"%')
                    
                    # Handle hierarchical dietary preferences intelligently
                    if 'vegan' in prefs.dietary_preferences:
                        # If user is vegan, only show vegan recipes (most restrictive)
                        dietary_conditions.append(json_array_contains(Recipe.dietary_tags, 'vegan'))
                    elif 'vegetarian' in prefs.dietary_preferences:
                        # If user is vegetarian (but not vegan), show both vegetarian AND vegan recipes
                        # because vegan recipes are also suitable for vegetarians
                        dietary_conditions.append(
                            or_(
                                json_array_contains(Recipe.dietary_tags, 'vegetarian'),
                                json_array_contains(Recipe.dietary_tags, 'vegan')
                            )
                        )
                    
                    # Handle other dietary preferences intelligently
                    other_prefs = [p for p in prefs.dietary_preferences if p not in ['vegan', 'vegetarian']]
                    
                    # Handle gluten-free hierarchy
                    if 'gluten-free' in other_prefs:
                        dietary_conditions.append(json_array_contains(Recipe.dietary_tags, 'gluten-free'))
                        other_prefs.remove('gluten-free')
                    
                    # Handle dairy-free hierarchy  
                    if 'dairy-free' in other_prefs:
                        dietary_conditions.append(json_array_contains(Recipe.dietary_tags, 'dairy-free'))
                        other_prefs.remove('dairy-free')
                    
                    # Handle nut-free hierarchy
                    if 'nut-free' in other_prefs:
                        dietary_conditions.append(json_array_contains(Recipe.dietary_tags, 'nut-free'))
                        other_prefs.remove('nut-free')
                    
                    # Handle soy-free hierarchy
                    if 'soy-free' in other_prefs:
                        dietary_conditions.append(json_array_contains(Recipe.dietary_tags, 'soy-free'))
                        other_prefs.remove('soy-free')
                    
                    # Handle remaining preferences
                    for pref in other_prefs:
                        dietary_conditions.append(json_array_contains(Recipe.dietary_tags, pref))
                    
                    if dietary_conditions:
                        query = query.filter(or_(*dietary_conditions))
                
                # Filter out recipes with disliked ingredients (only when searching)
                if prefs.disliked_ingredients and len(prefs.disliked_ingredients) > 0 and search_request.query:
                    for ingredient in prefs.disliked_ingredients:
                        # This would require more complex ingredient matching
                        # For now, we'll do a simple title/summary search
                        query = query.filter(
                            and_(
                                ~Recipe.title.ilike(f"%{ingredient}%"),
                                ~Recipe.summary.ilike(f"%{ingredient}%")
                            )
                        )
            
            if search_request.difficulty_level:
                query = query.filter(Recipe.difficulty_level == search_request.difficulty_level)
            
            if search_request.max_prep_time:
                query = query.filter(Recipe.prep_time <= search_request.max_prep_time)
            
            # Apply macronutrient filters (calories, protein, carbs, fats)
            if search_request.min_calories is not None:
                query = query.filter(Recipe.per_serving_calories >= search_request.min_calories)
            
            if search_request.max_calories is not None:
                query = query.filter(Recipe.per_serving_calories <= search_request.max_calories)
            
            if search_request.min_protein is not None:
                query = query.filter(Recipe.per_serving_protein >= search_request.min_protein)
            
            if search_request.max_protein is not None:
                query = query.filter(Recipe.per_serving_protein <= search_request.max_protein)
            
            if search_request.min_carbs is not None:
                query = query.filter(Recipe.per_serving_carbs >= search_request.min_carbs)
            
            if search_request.max_carbs is not None:
                query = query.filter(Recipe.per_serving_carbs <= search_request.max_carbs)
            
            if search_request.min_fats is not None:
                query = query.filter(Recipe.per_serving_fat >= search_request.min_fats)
            
            if search_request.max_fats is not None:
                query = query.filter(Recipe.per_serving_fat <= search_request.max_fats)
            
            # Apply micronutrient filters
            if search_request.micronutrient_filters and search_request.micronutrient_filters.nutrients:
                micronutrient_filters = search_request.micronutrient_filters
                
                # For now, we'll apply basic micronutrient filtering
                # In a full implementation, you'd need to:
                    # 1. Join with RecipeIngredient -> Ingredient tables
                    # 2. Sum up micronutrient values per recipe
                    # 3. Filter based on total micronutrient content
                    
                    # For demonstration, we'll filter by recipe ID patterns
                    # (This is just to show the structure - real implementation would be more complex)
                if micronutrient_filters.nutrients:
                    for nutrient in micronutrient_filters.nutrients:
                        min_value = micronutrient_filters.min_values.get(nutrient, 0)
                        max_value = micronutrient_filters.max_values.get(nutrient, float('inf'))
                        
                    if nutrient == 'vitamin_d' and min_value > 0:
                        # Example: prioritize recipes with "salmon" or "fish" in title
                        query = query.filter(
                            or_(
                                Recipe.title.ilike('%salmon%'),
                                Recipe.title.ilike('%fish%'),
                                Recipe.title.ilike('%tuna%')
                            )
                        )
                    elif nutrient == 'iron' and min_value > 0:
                        # Example: prioritize recipes with "beef" or "spinach" in title
                        query = query.filter(
                            or_(
                                Recipe.title.ilike('%beef%'),
                                Recipe.title.ilike('%spinach%'),
                                Recipe.title.ilike('%lentil%')
                            )
                        )
                    elif nutrient == 'calcium' and min_value > 0:
                        # Example: prioritize recipes with "cheese" or "milk" in title
                        query = query.filter(
                            or_(
                                Recipe.title.ilike('%cheese%'),
                                Recipe.title.ilike('%milk%'),
                                Recipe.title.ilike('%yogurt%')
                            )
                        )
            
            # Apply sorting if specified
            if hasattr(search_request, 'sort_by') and search_request.sort_by:
                sort_field = search_request.sort_by
                sort_order = getattr(search_request, 'sort_order', 'asc')
                
                if sort_field == 'title':
                    query = query.order_by(Recipe.title.asc() if sort_order == 'asc' else Recipe.title.desc())
                elif sort_field == 'calories':
                    # For now, we'll sort by ID since we don't have calculated calories in the database
                    # The nutritional values will be calculated in _calculate_recipe_nutrition
                    query = query.order_by(Recipe.id.asc() if sort_order == 'asc' else Recipe.id.desc())
                elif sort_field == 'protein':
                    # For now, we'll sort by ID since we don't have calculated protein in the database
                    # The nutritional values will be calculated in _calculate_recipe_nutrition
                    query = query.order_by(Recipe.id.asc() if sort_order == 'asc' else Recipe.id.desc())
                elif sort_field == 'prep_time':
                    # prep_time sorting is handled in post-query sorting
                    pass
                elif sort_field == 'difficulty':
                    # Order by difficulty: easy=1, medium=2, hard=3
                    difficulty_order = case(
                        (Recipe.difficulty_level == 'easy', 1),
                        (Recipe.difficulty_level == 'medium', 2),
                        (Recipe.difficulty_level == 'hard', 3),
                        else_=4
                    )
                    query = query.order_by(difficulty_order.asc() if sort_order == 'asc' else difficulty_order.desc())
                elif sort_field == 'id':
                    query = query.order_by(Recipe.id.asc() if sort_order == 'asc' else Recipe.id.desc())
                else:
                    # Default sorting
                    query = query.order_by(Recipe.id.asc())
            else:
                # Default sorting: order by recipe ID ascending (recipe_001, recipe_002, etc.)
                query = query.order_by(Recipe.id.asc())
            
            # Eagerly load ingredients and instructions relationships
            from sqlalchemy.orm import joinedload
            query = query.options(
                joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient),
                joinedload(Recipe.instructions)
            )
            
            # Get ALL recipes first (no pagination yet)
            all_recipes = query.all()
            logger.info(f"Database search found {len(all_recipes)} recipes")
            
            # Calculate nutritional data for each recipe
            for recipe in all_recipes:
                self._calculate_recipe_nutrition(recipe)
            
            # Convert to response format (inline to avoid dependency on missing helpers)
            all_recipe_responses = []
            for recipe in all_recipes:
                # Serialize ingredients and instructions (ensure lists)
                try:
                    recipe_ingredients = getattr(recipe, 'ingredients', [])
                    logger.debug(f"Recipe {recipe.id} has {len(recipe_ingredients)} ingredients")
                    serialized_ingredients = [
                        {
                            "name": ri.ingredient.name if ri.ingredient else "Unknown",
                            "quantity": ri.quantity,
                            "unit": ri.unit
                        }
                        for ri in recipe_ingredients
                        if ri.ingredient  # Only include if ingredient relationship is loaded
                    ]
                    if not serialized_ingredients and recipe_ingredients:
                        logger.warning(f"Recipe {recipe.id} has {len(recipe_ingredients)} ingredient relationships but couldn't serialize them")
                except Exception as e:
                    logger.error(f"Error serializing ingredients for recipe {recipe.id}: {str(e)}", exc_info=True)
                    serialized_ingredients = []
                
                try:
                    recipe_instructions = getattr(recipe, 'instructions', [])
                    logger.debug(f"Recipe {recipe.id} has {len(recipe_instructions)} instructions")
                    # Sort instructions by step_number
                    sorted_instructions = sorted(recipe_instructions, key=lambda x: x.step_number) if recipe_instructions else []
                    serialized_instructions = [
                        {
                            "step": instr.step_number,
                            "description": instr.description
                        }
                        for instr in sorted_instructions
                    ]
                    if not serialized_instructions and recipe_instructions:
                        logger.warning(f"Recipe {recipe.id} has {len(recipe_instructions)} instruction relationships but couldn't serialize them")
                except Exception as e:
                    logger.error(f"Error serializing instructions for recipe {recipe.id}: {str(e)}", exc_info=True)
                    serialized_instructions = []

                # Get servings - this is the source of truth for how many servings the recipe makes
                recipe_servings = getattr(recipe, 'servings', 1) or 1
                
                # Get per-serving nutrition - these are the original values from the recipe
                # These should be the authoritative source as recipes typically store per-serving values
                per_serving_calories = getattr(recipe, 'per_serving_calories', None)
                per_serving_protein = getattr(recipe, 'per_serving_protein', None)
                per_serving_carbs = getattr(recipe, 'per_serving_carbs', None)
                per_serving_fats = getattr(recipe, 'per_serving_fat', None) or getattr(recipe, 'per_serving_fats', None)
                
                # Calculate total recipe nutrition by multiplying per-serving by servings
                # This ensures consistency: total = per_serving * servings
                if per_serving_calories is not None:
                    total_calories = per_serving_calories * recipe_servings
                else:
                    # Fallback to stored total if per-serving is missing
                    total_calories = getattr(recipe, 'total_calories', None)
                    # If we have total but not per-serving, calculate per-serving
                    if total_calories and recipe_servings > 0:
                        per_serving_calories = total_calories / recipe_servings
                
                if per_serving_protein is not None:
                    total_protein = per_serving_protein * recipe_servings
                else:
                    total_protein = getattr(recipe, 'total_protein', None)
                    if total_protein and recipe_servings > 0:
                        per_serving_protein = total_protein / recipe_servings
                
                if per_serving_carbs is not None:
                    total_carbs = per_serving_carbs * recipe_servings
                else:
                    total_carbs = getattr(recipe, 'total_carbs', None)
                    if total_carbs and recipe_servings > 0:
                        per_serving_carbs = total_carbs / recipe_servings
                
                if per_serving_fats is not None:
                    total_fats = per_serving_fats * recipe_servings
                else:
                    total_fats = getattr(recipe, 'total_fat', None) or getattr(recipe, 'total_fats', None)
                    if total_fats and recipe_servings > 0:
                        per_serving_fats = total_fats / recipe_servings
                
                all_recipe_responses.append({
                    "id": recipe.id,
                    "title": recipe.title,
                    "cuisine": recipe.cuisine,
                    "meal_type": recipe.meal_type,
                    "summary": recipe.summary,
                    "servings": recipe_servings,
                    "prep_time": getattr(recipe, 'prep_time', 0),
                    "cook_time": getattr(recipe, 'cook_time', 0),
                    "difficulty_level": getattr(recipe, 'difficulty_level', 'easy'),
                    "dietary_tags": getattr(recipe, 'dietary_tags', []) or [],
                    # Calculated fields (for sorting/search) - use per-serving
                    "calculated_calories": float(per_serving_calories or 0),
                    "calculated_protein": float(per_serving_protein or 0),
                    "calculated_carbs": float(per_serving_carbs or 0),
                    "calculated_fats": float(per_serving_fats or 0),
                    # Total recipe nutrition
                    "total_calories": float(total_calories or 0),
                    "total_protein": float(total_protein or 0),
                    "total_carbs": float(total_carbs or 0),
                    "total_fats": float(total_fats or 0),
                    # Per-serving nutrition
                    "per_serving_calories": float(per_serving_calories or 0),
                    "per_serving_protein": float(per_serving_protein or 0),
                    "per_serving_carbs": float(per_serving_carbs or 0),
                    "per_serving_fats": float(per_serving_fats or 0),
                    "ingredients": serialized_ingredients,
                    "instructions": serialized_instructions,
                })
            
            # Apply sorting to ALL recipes BEFORE pagination
            if hasattr(search_request, 'sort_by') and search_request.sort_by:
                sort_field = search_request.sort_by
                sort_order = getattr(search_request, 'sort_order', 'asc')
                reverse = sort_order.lower() == 'desc'
                
                if sort_field in ['calories', 'protein', 'carbs', 'fats']:
                    # Sort by nutritional values
                    def get_nutritional_value(recipe):
                        if sort_field == 'calories':
                            return recipe.get('calculated_calories', 0)
                        elif sort_field == 'protein':
                            return recipe.get('calculated_protein', 0)
                        elif sort_field == 'carbs':
                            return recipe.get('calculated_carbs', 0)
                        elif sort_field == 'fats':
                            return recipe.get('calculated_fats', 0)
                        return 0
                    all_recipe_responses.sort(key=get_nutritional_value, reverse=reverse)
                    
                elif sort_field == 'prep_time':
                    # Sort by prep_time - ensure it's treated as integer
                    logger.debug(f"Sorting by prep_time: {sort_order}")
                    logger.debug(f"Before sorting: {[r.get('title', 'Unknown') + ': ' + str(r.get('prep_time', 0)) + 'min' for r in all_recipe_responses[:5]]}")
                    def get_prep_time_value(recipe):
                        prep_time = recipe.get('prep_time', 0)
                        # Ensure it's an integer for proper sorting
                        try:
                            return int(prep_time)
                        except (ValueError, TypeError):
                            return 0
                    all_recipe_responses.sort(key=get_prep_time_value, reverse=reverse)
                    logger.debug(f"After sorting: {[r.get('title', 'Unknown') + ': ' + str(r.get('prep_time', 0)) + 'min' for r in all_recipe_responses[:5]]}")
            
            # Now apply pagination to the sorted results
            offset = (search_request.page - 1) * search_request.limit
            end_idx = offset + search_request.limit
            recipe_responses = all_recipe_responses[offset:end_idx]
            
            # Calculate pagination info - use the same query but without limit/offset
            count_query = db.query(Recipe).filter(Recipe.is_active == True)
            
            # Apply the same filters to count query
            if search_request.query:
                search_term = search_request.query.strip()
                if search_term.startswith('#') and search_term[1:].isdigit():
                    recipe_number = search_term[1:].zfill(3)
                    recipe_id_pattern = f"recipe_{recipe_number}"
                    count_query = count_query.filter(Recipe.id == recipe_id_pattern)
                elif search_term.startswith('r') and search_term[1:].isdigit():
                    recipe_number = search_term[1:].zfill(3)
                    recipe_id_pattern = f"recipe_{recipe_number}"
                    count_query = count_query.filter(Recipe.id == recipe_id_pattern)
                elif search_term.isdigit():
                    recipe_number = search_term.zfill(3)
                    recipe_id_pattern = f"recipe_{recipe_number}"
                    count_query = count_query.filter(Recipe.id == recipe_id_pattern)
                elif search_term.startswith('range:'):
                    try:
                        range_part = search_term.replace('range:', '').strip()
                        if '-' in range_part:
                            start_num, end_num = range_part.split('-')
                            start_num = int(start_num.strip())
                            end_num = int(end_num.strip())
                            recipe_ids = [f"recipe_{str(i).zfill(3)}" for i in range(start_num, end_num + 1)]
                            count_query = count_query.filter(Recipe.id.in_(recipe_ids))
                        else:
                            end_num = int(range_part.strip())
                            recipe_ids = [f"recipe_{str(i).zfill(3)}" for i in range(1, end_num + 1)]
                            count_query = count_query.filter(Recipe.id.in_(recipe_ids))
                    except (ValueError, IndexError):
                        count_query = count_query.filter(
                            or_(
                                Recipe.title.ilike(f"%{search_term}%"),
                                Recipe.summary.ilike(f"%{search_term}%"),
                                Recipe.id.ilike(f"%{search_term}%")
                            )
                        )
                elif search_term.startswith('last:'):
                    try:
                        count = int(search_term.replace('last:', '').strip())
                        # For last: queries, we need to get the total count of all recipes
                        count_query = db.query(Recipe).filter(Recipe.is_active == True)
                    except ValueError:
                        count_query = count_query.filter(
                            or_(
                                Recipe.title.ilike(f"%{search_term}%"),
                                Recipe.summary.ilike(f"%{search_term}%"),
                                Recipe.id.ilike(f"%{search_term}%")
                            )
                        )
                elif search_term.startswith('first:'):
                    try:
                        count = int(search_term.replace('first:', '').strip())
                        # For first: queries, we need to get the total count of all recipes
                        count_query = db.query(Recipe).filter(Recipe.is_active == True)
                    except ValueError:
                        count_query = count_query.filter(
                            or_(
                                Recipe.title.ilike(f"%{search_term}%"),
                                Recipe.summary.ilike(f"%{search_term}%"),
                                Recipe.id.ilike(f"%{search_term}%")
                            )
                        )
                else:
                    count_query = count_query.filter(
                        or_(
                            Recipe.title.ilike(f"%{search_term}%"),
                            Recipe.summary.ilike(f"%{search_term}%"),
                            Recipe.id.ilike(f"%{search_term}%")
                        )
                    )
            
            # Apply other filters to count query
            if search_request.cuisine:
                count_query = count_query.filter(Recipe.cuisine.ilike(f"%{search_request.cuisine}%"))
            if search_request.meal_type:
                count_query = count_query.filter(Recipe.meal_type == search_request.meal_type)
            if search_request.dietary_tags:
                for tag in search_request.dietary_tags:
                    count_query = count_query.filter(Recipe.dietary_tags.contains([tag]))
            if search_request.difficulty_level:
                count_query = count_query.filter(Recipe.difficulty_level == search_request.difficulty_level)
            if search_request.max_prep_time:
                count_query = count_query.filter(Recipe.prep_time <= search_request.max_prep_time)
            
            total_count = count_query.count()
            total_pages = (total_count + search_request.limit - 1) // search_request.limit
            
            return {
                "recipes": recipe_responses,
                "total": total_count,
                "pages": total_pages,
                "current_page": search_request.page,
                "sort_by": getattr(search_request, 'sort_by', None),
                "sort_order": getattr(search_request, 'sort_order', 'asc')
            }
        except Exception as e:
            logger.error(f"Error searching recipes: {str(e)}")
            return {
                "recipes": [],
                "total": 0,
                "pages": 0,
                "current_page": getattr(search_request, 'page', 1),
                "sort_by": getattr(search_request, 'sort_by', None),
                "sort_order": getattr(search_request, 'sort_order', 'asc'),
                "error": str(e)
            }
    
    def _convert_meal_plan_to_response(self, meal_plan: MealPlan, db: Session = None) -> Dict[str, Any]:
        """Convert MealPlan ORM to MealPlanResponse-compatible dict."""
        try:
            # CRITICAL: Explicitly access meals relationship - ensure it's loaded
            # Try multiple ways to access meals to ensure we get all of them
            meals_list = []
            try:
                # First try: direct access (if joinedload was used)
                if hasattr(meal_plan, 'meals'):
                    meals_list = list(meal_plan.meals)
                # Second try: getattr
                if not meals_list:
                    meals_list = list(getattr(meal_plan, 'meals', []))
                
                # CRITICAL FIX: If meals still aren't loaded and we have a db session, query directly
                if (not meals_list or len(meals_list) == 0) and db is not None:
                    logger.warning(f"No meals found via relationship for meal plan {meal_plan.id}, querying directly from database")
                    from models.nutrition import MealPlanMeal
                    meals_list = db.query(MealPlanMeal).filter(
                        MealPlanMeal.meal_plan_id == meal_plan.id
                    ).order_by(MealPlanMeal.meal_date, MealPlanMeal.meal_type).all()
                    logger.info(f"Queried {len(meals_list)} meals directly from database for meal plan {meal_plan.id}")
                elif not meals_list or len(meals_list) == 0:
                    # This shouldn't happen if joinedload was used, but safety check
                    logger.warning(f"No meals found via relationship for meal plan {meal_plan.id}, and no db session available to query directly")
            except Exception as e:
                logger.error(f"Error accessing meals relationship: {e}", exc_info=True)
                # Last resort: try to query directly if db session is available
                if db is not None:
                    try:
                        from models.nutrition import MealPlanMeal
                        meals_list = db.query(MealPlanMeal).filter(
                            MealPlanMeal.meal_plan_id == meal_plan.id
                        ).order_by(MealPlanMeal.meal_date, MealPlanMeal.meal_type).all()
                        logger.info(f"Fallback: Queried {len(meals_list)} meals directly from database after exception")
                    except Exception as db_error:
                        logger.error(f"Failed to query meals directly: {db_error}", exc_info=True)
                        meals_list = []
                else:
                    meals_list = []
            
            logger.info(f"Converting meal plan {meal_plan.id} to response: {len(meals_list)} meals found")
            
            # ROOT CAUSE FIX: Don't validate meal count for progressive meal plans (empty structure)
            # Progressive generation starts empty and is filled one slot at a time
            is_progressive_plan = False
            generation_strategy = getattr(meal_plan, 'generation_strategy', None) or {}
            if isinstance(generation_strategy, dict):
                is_progressive_plan = generation_strategy.get('strategy') == 'progressive' or generation_strategy.get('mode') == 'empty_structure'
            
            # Only validate meal count for bulk-generated meal plans (not progressive)
            if meal_plan.plan_type == 'weekly' and not is_progressive_plan:
                # Calculate expected meals based on meals_per_day (default 4)
                # For progressive plans, this validation is skipped
                meals_per_day = 4  # Default, can be calculated from user preferences if needed
                expected_meals = 7 * meals_per_day  # 7 days × meals_per_day
                if len(meals_list) < expected_meals:
                    logger.warning(f"Weekly meal plan {meal_plan.id} has only {len(meals_list)} meals, expected {expected_meals} (7 days × {meals_per_day} meals)")
                    # Log meal distribution by date to debug (only for bulk-generated plans with missing meals)
                    from collections import Counter
                    meal_dates = [str(m.meal_date) for m in meals_list if hasattr(m, 'meal_date') and m.meal_date]
                    date_counts = Counter(meal_dates)
                    logger.warning(f"   Meal distribution by date: {dict(date_counts)}")
                else:
                    logger.info(f"Weekly meal plan {meal_plan.id} has {len(meals_list)} meals (expected {expected_meals})")
            elif meal_plan.plan_type == 'weekly' and is_progressive_plan:
                # Progressive plan - log info only, no validation
                logger.info(f"Progressive meal plan {meal_plan.id} has {len(meals_list)} meals (filling progressively)")
            
            meals_response: List[Dict[str, Any]] = []
            total_cal = 0.0
            total_pro = 0.0
            total_carbs = 0.0
            total_fats = 0.0

            # CRITICAL: Filter out beverages and sauces from meal plans (even if already saved)
            from ai.fallback_recipes import fallback_generator
            
            # CRITICAL: Detect AI-only mode by checking meal flags
            # In AI-only mode, ALL meals should have ai_generated=True
            ai_meals_in_plan = []
            db_meals_in_plan = []
            for m in meals_list:
                rd = m.recipe_details or {}
                if isinstance(rd, dict):
                    # Check both flags - prioritize ai_generated
                    is_ai = rd.get('ai_generated', False) == True
                    is_db = rd.get('database_source', False) == True
                    if is_ai:
                        ai_meals_in_plan.append(m)
                    if is_db:
                        db_meals_in_plan.append(m)
            # AI-only mode = no database meals at all (or 90%+ AI meals)
            # If we have any database meals, it's NOT AI-only
            total_meals = len(meals_list)
            ai_ratio = len(ai_meals_in_plan) / total_meals if total_meals > 0 else 0
            is_ai_only_plan = len(db_meals_in_plan) == 0 and ai_ratio > 0.9
            logger.info(f"AI-only detection: {len(ai_meals_in_plan)} AI, {len(db_meals_in_plan)} DB out of {total_meals} total (ratio: {ai_ratio:.1%}) -> AI-only: {is_ai_only_plan}")

            for meal in meals_list:
                recipe_details = meal.recipe_details or {}
                
                # Log meal_type from recipe_details to diagnose snack slot assignment
                if isinstance(recipe_details, dict):
                    preserved_meal_type = recipe_details.get('meal_type', None)
                    if preserved_meal_type and preserved_meal_type != meal.meal_type:
                        logger.info(f"Meal {meal.id} '{meal.meal_name}': DB meal_type='{meal.meal_type}', recipe_details.meal_type='{preserved_meal_type}'")
                    elif meal.meal_type == 'snack':
                        logger.warning(f"Snack meal {meal.id} '{meal.meal_name}' has no preserved meal_type in recipe_details (DB meal_type='snack')")
                
                # Check if this meal is a beverage/sauce/dessert and should be excluded
                # Only filter if the meal is clearly a beverage/sauce/dessert, not just because a keyword appears in instructions
                meal_name = (meal.meal_name or "").lower()
                meal_type = meal.meal_type or ""
                
                # Only check title and summary for beverage/sauce/dessert keywords (not ingredients/instructions)
                # This prevents false positives from ingredients like "add sauce" or "butter" in cooking instructions
                title_and_summary = meal_name
                if isinstance(recipe_details, dict):
                    title = (recipe_details.get('title') or "").lower()
                    summary = (recipe_details.get('summary') or "").lower()
                    title_and_summary = f"{meal_name} {title} {summary}"
                
                # Strict beverage keywords - only match if meal is clearly a drink
                beverage_keywords = [
                    "sangria", "cocktail", "smoothie", "shake", "juice", "punch", "cider", 
                    "tea", "coffee", "latte", "mojito", "spritzer", "spritz",
                    "amaretto", "vodka", "rum", "gin", "whiskey", "beer", "wine", "liquor",
                    "highball", "drink", "beverage", "mixed drink", "shot",
                    "margarita", "daiquiri", "martini", "cosmopolitan", "boccie ball"
                ]
                # Strict sauce keywords - only match if meal is clearly a sauce/dip
                sauce_keywords = ["sauce only", "dressing only", "marinade only", "dip only", "guacamole only"]
                # Strict dessert keywords - only match if meal is clearly a dessert
                dessert_keywords = ["ice cream", "sorbet", "cookie", "brownie", "cake", "pudding", "mousse", "dessert only"]
                
                # Only check title/summary, and require the keyword to be prominent (not in cooking instructions)
                is_beverage = any(k in title_and_summary for k in beverage_keywords)
                is_sauce = any(k in title_and_summary for k in sauce_keywords)
                is_dessert = any(k in title_and_summary for k in dessert_keywords)
                
                is_beverage_sauce_dessert = is_beverage or is_sauce or is_dessert
                
                # Exclude beverages/sauces/desserts from breakfast, lunch, dinner (but allow snacks)
                # CRITICAL: Only filter if we're CERTAIN it's a beverage/sauce/dessert
                if meal_type in ("breakfast", "lunch", "dinner") and is_beverage_sauce_dessert:
                    logger.warning(f"Filtering out beverage/sauce/dessert meal: {meal.meal_name} (type: {meal_type})")
                    # Replace with a fallback meal
                    try:
                        # Use meal calories or estimate from meal type
                        target_cal_for_fallback = meal.calories
                        if not target_cal_for_fallback or target_cal_for_fallback <= 0:
                            default_cal_by_type = {'breakfast': 400, 'lunch': 500, 'dinner': 600, 'snack': 200}
                            target_cal_for_fallback = default_cal_by_type.get(meal_type, 500)
                        # Collect ALL existing meal names to avoid duplicates (including already processed meals)
                        existing_meal_names = [m.meal_name for m in meals_list if m != meal and m.meal_name]
                        existing_meal_names.extend([m.get('meal_name', '') for m in meals_response if m.get('meal_name')])
                        
                        # Try to generate a unique fallback
                        max_attempts = 5
                        fallback = None
                        for attempt in range(max_attempts):
                            fallback = fallback_generator.generate_unique_recipe(
                                meal_type, 
                                target_cal_for_fallback, 
                                meal.cuisine or 'International', 
                                existing_meal_names
                            )
                            fallback_name = fallback.get('meal_name', '')
                            # Check if fallback is unique
                            if fallback_name and fallback_name not in existing_meal_names:
                                existing_meal_names.append(fallback_name)
                                break
                            # If still duplicate, try with different calories
                            target_cal_for_fallback = int(target_cal_for_fallback * (1.1 if attempt % 2 == 0 else 0.9))
                        
                        if not fallback or not fallback.get('meal_name'):
                            logger.error(f"Failed to generate unique fallback for {meal_type} after {max_attempts} attempts")
                            # Keep the original meal rather than creating empty slot - it's better than nothing
                            logger.warning(f"Keeping original meal '{meal.meal_name}' (could not generate unique fallback)")
                            # Don't replace - keep original meal and continue processing
                        else:
                            # Update meal data with fallback
                            meal.meal_name = fallback.get('meal_name', f'Fallback {meal_type}')
                            fallback_cal = fallback.get('calories')
                            if not fallback_cal or fallback_cal <= 0:
                                default_cal_by_type = {'breakfast': 400, 'lunch': 500, 'dinner': 600, 'snack': 200}
                                fallback_cal = default_cal_by_type.get(meal_type, 500)
                            meal.calories = fallback_cal
                            meal.protein = fallback.get('protein', meal.protein or 0)
                            meal.carbs = fallback.get('carbs', meal.carbs or 0)
                            meal.fats = fallback.get('fats', meal.fats or 0)
                            meal.cuisine = fallback.get('cuisine', meal.cuisine or 'International')
                            recipe_details = fallback.get('recipe', {})
                            if not isinstance(recipe_details, dict):
                                recipe_details = {}
                            # CRITICAL FIX: ALWAYS mark beverage replacements as AI (AI-only generation is default)
                            # Even if the meal plan has database meals (from old plans), new replacements should be AI
                            # This prevents old database meal plans from getting more database meals when beverages are filtered
                            recipe_details['ai_generated'] = True
                            recipe_details['database_source'] = False
                            logger.info(f"Replaced beverage meal with AI fallback: {meal.meal_name} (AI-ONLY MODE - always AI)")
                            meal.recipe_details = recipe_details
                    except Exception as e:
                        logger.error(f"Error replacing beverage meal with fallback: {e}")
                        # Keep the original meal rather than creating empty slot
                        logger.warning(f"Keeping original meal '{meal.meal_name}' (exception during fallback generation)")
                        # Continue processing this meal normally (don't skip it)
                
                # Standardize measurements in recipe details
                if recipe_details and isinstance(recipe_details, dict):
                    recipe_details = self.standardize_recipe_measurements(recipe_details)
                
                # Use PER-SERVING calories for daily intake calculation
                # Extract per-serving calories from recipe_details or calculate from meal.calories
                servings = recipe_details.get('servings', 1) if isinstance(recipe_details, dict) else 1
                per_serving_cal = None
                if isinstance(recipe_details, dict):
                    nutrition = recipe_details.get('nutrition', {})
                    # Priority: per_serving_calories > calculated from total > meal.calories
                    if nutrition.get('per_serving_calories'):
                        per_serving_cal = nutrition.get('per_serving_calories')
                    elif recipe_details.get('per_serving_calories'):
                        per_serving_cal = recipe_details.get('per_serving_calories')
                    elif meal.calories and servings > 1 and meal.calories > 500:
                        # If meal.calories looks like total (> 500 and servings > 1), divide
                        per_serving_cal = int(meal.calories / servings)
                    else:
                        # Otherwise assume meal.calories is per-serving
                        per_serving_cal = meal.calories
                else:
                    per_serving_cal = meal.calories
                
                # CRITICAL FIX: In AI-only generation mode (default), ALL meals should be AI unless explicitly marked as database
                # Default to AI (True) if flag is missing - don't default to database (False)
                ai_flag = None
                if isinstance(recipe_details, dict):
                    ai_flag = recipe_details.get('ai_generated')
                    # Explicitly check for True/False, but default to True (AI) if missing
                    if ai_flag is True:
                        ai_flag = True
                    elif ai_flag is False:
                        ai_flag = False
                    else:
                        # Flag is missing/None - check database_source
                        has_explicit_db = recipe_details.get('database_source', False) == True
                        if has_explicit_db:
                            ai_flag = False  # Explicitly marked as database
                        else:
                            ai_flag = True  # Default to AI (AI-only mode is default)
                            logger.debug(f"🔧 Inferred AI flag=True for meal '{meal.meal_name}' (missing flag, defaulting to AI)")
                # Also check if meal has direct ai_generated attribute
                if ai_flag is None:
                    ai_flag = bool(getattr(meal, 'ai_generated', True))  # Default to True (AI-only mode)
                
                # CRITICAL: If flag is False but database_source is not explicitly True, treat as AI
                # This handles old meal plans that might have incorrect flags
                if ai_flag is False and isinstance(recipe_details, dict):
                    has_explicit_db = recipe_details.get('database_source', False) == True
                    if not has_explicit_db:
                        ai_flag = True  # No explicit DB flag - assume AI (fix old meal plans)
                        logger.warning(f"FIXED: Meal '{meal.meal_name}' had ai_generated=False but no explicit database_source - marking as AI")
                        # Update the recipe_details to fix it
                        recipe_details['ai_generated'] = True
                        recipe_details['database_source'] = False
                
                # Ensure meal_date is properly formatted as ISO 8601 string for frontend
                meal_date_str = meal.meal_date.isoformat() if hasattr(meal.meal_date, 'isoformat') else str(meal.meal_date)
                
                # CRITICAL FIX: Use preserved meal_type from recipe_details if available (for morning snack/afternoon snack)
                # Otherwise fall back to database meal_type
                preserved_meal_type = None
                if isinstance(recipe_details, dict):
                    preserved_meal_type = recipe_details.get('meal_type')
                
                # CRITICAL FIX: If meal_type is generic 'snack' and we have 5 meals per day, try to infer from meal position
                # Check if this is a morning or afternoon snack based on meal order for the day
                if meal.meal_type == 'snack' and not preserved_meal_type and db:
                    try:
                        # Try to infer from meal order - first snack is morning, second is afternoon
                        meals_for_date = db.query(MealPlanMeal).filter(
                            MealPlanMeal.meal_plan_id == meal.meal_plan_id,
                            MealPlanMeal.meal_date == meal.meal_date
                        ).order_by(MealPlanMeal.id).all()
                        
                        snack_meals = [m for m in meals_for_date if m.meal_type == 'snack']
                        if len(snack_meals) >= 2:
                            snack_index = snack_meals.index(meal)
                            if snack_index == 0:
                                preserved_meal_type = 'morning snack'
                            elif snack_index == 1:
                                preserved_meal_type = 'afternoon snack'
                    except Exception as e:
                        logger.debug(f"Could not infer snack type from meal order: {e}")
                        # Fall back to default behavior
                
                # Use preserved meal_type if it's a specific snack type (morning snack, afternoon snack)
                # Otherwise use database meal_type
                final_meal_type = preserved_meal_type if preserved_meal_type in ['morning snack', 'afternoon snack', 'evening snack'] else (meal.meal_type or preserved_meal_type or 'dinner')
                
                # CRITICAL FIX: Update recipe_details with the final meal_type if it was inferred
                if preserved_meal_type and preserved_meal_type != meal.meal_type and isinstance(recipe_details, dict):
                    recipe_details['meal_type'] = preserved_meal_type
                
                meals_response.append({
                    "id": meal.id,  # CRITICAL FIX: Include meal ID for move/delete operations
                    "meal_plan_id": meal.meal_plan_id,
                    "meal_date": meal_date_str,  # String format for frontend
                    "date": meal_date_str,  # Also include as 'date' for frontend compatibility
                    "meal_type": final_meal_type,  # CRITICAL FIX: Use preserved meal_type for specific snack types
                    "type": final_meal_type,  # Also include as 'type' for frontend compatibility
                    "meal_time": getattr(meal, 'meal_time', None),
                "meal_name": meal.meal_name,
                    "recipe": recipe_details if recipe_details else None,
                    "recipes": [recipe_details] if recipe_details else [],
                    "recipe_details": recipe_details if recipe_details else None,  # Also expose as recipe_details for frontend
                    "ai_generated": ai_flag,  # Top-level flag for easy access
                    "calories": float(per_serving_cal or meal.calories or 0),  # Top-level per-serving calories (primary field)
                    "per_serving_calories": float(per_serving_cal or meal.calories or 0),  # Explicit per-serving field
                    # NOTE: All calorie values are per-serving (not total recipe calories)
                    "total_protein": meal.protein,
                    "total_carbs": meal.carbs,
                    "total_fat": meal.fats,
                    "total_fiber": getattr(meal, 'fiber', None),
                    "total_sodium": getattr(meal, 'sodium', None),
                    "created_at": (getattr(meal, 'created_at', datetime.utcnow()).isoformat() if hasattr(getattr(meal, 'created_at', datetime.utcnow()), 'isoformat') else str(getattr(meal, 'created_at', datetime.utcnow()))),
                    "updated_at": (getattr(meal, 'updated_at').isoformat() if getattr(meal, 'updated_at', None) and hasattr(getattr(meal, 'updated_at'), 'isoformat') else (str(getattr(meal, 'updated_at')) if getattr(meal, 'updated_at', None) else None))
                })
                total_cal += float(per_serving_cal or meal.calories or 0)  # Use per-serving calories for total
                total_pro += float(meal.protein or 0)
                total_carbs += float(meal.carbs or 0)
                total_fats += float(meal.fats or 0)

            response = {
                "id": meal_plan.id,
                "user_id": meal_plan.user_id,
                "plan_type": meal_plan.plan_type,
                "start_date": meal_plan.start_date.isoformat() if hasattr(meal_plan.start_date, 'isoformat') else str(meal_plan.start_date),
                "end_date": meal_plan.end_date.isoformat() if meal_plan.end_date and hasattr(meal_plan.end_date, 'isoformat') else (str(meal_plan.end_date) if meal_plan.end_date else None),
                "version": meal_plan.version,
                "is_active": getattr(meal_plan, 'is_active', True),
                "meals": meals_response,
                "total_nutrition": {
                    "calories": round(total_cal, 1),
                    "protein": round(total_pro, 1),
                    "carbs": round(total_carbs, 1),
                    "fats": round(total_fats, 1)
                },
                "created_at": (getattr(meal_plan, 'created_at', datetime.utcnow()).isoformat() if hasattr(getattr(meal_plan, 'created_at', datetime.utcnow()), 'isoformat') else str(getattr(meal_plan, 'created_at', datetime.utcnow()))),
                "updated_at": (getattr(meal_plan, 'updated_at', datetime.utcnow()).isoformat() if getattr(meal_plan, 'updated_at', None) and hasattr(getattr(meal_plan, 'updated_at'), 'isoformat') else (str(getattr(meal_plan, 'updated_at')) if getattr(meal_plan, 'updated_at', None) else None))
            }
            return response
        except Exception as e:
            logger.error(f"Error converting meal plan response: {str(e)}")
        return {
                "id": meal_plan.id,
                "user_id": meal_plan.user_id,
                "plan_type": meal_plan.plan_type,
                "start_date": meal_plan.start_date.isoformat() if hasattr(meal_plan.start_date, 'isoformat') else str(meal_plan.start_date),
                "end_date": meal_plan.end_date.isoformat() if meal_plan.end_date and hasattr(meal_plan.end_date, 'isoformat') else (str(meal_plan.end_date) if meal_plan.end_date else None),
                "version": meal_plan.version,
                "is_active": getattr(meal_plan, 'is_active', True),
                "meals": [],
                "total_nutrition": {"calories": 0, "protein": 0, "carbs": 0, "fats": 0},
                "created_at": (getattr(meal_plan, 'created_at', datetime.utcnow()).isoformat() if hasattr(getattr(meal_plan, 'created_at', datetime.utcnow()), 'isoformat') else str(getattr(meal_plan, 'created_at', datetime.utcnow()))),
                "updated_at": (getattr(meal_plan, 'updated_at', datetime.utcnow()).isoformat() if getattr(meal_plan, 'updated_at', None) and hasattr(getattr(meal_plan, 'updated_at'), 'isoformat') else (str(getattr(meal_plan, 'updated_at')) if getattr(meal_plan, 'updated_at', None) else None))
            }
    
    def _convert_shopping_list_to_response(self, shopping_list: ShoppingList, db: Session = None) -> Dict[str, Any]:
        """Convert ShoppingList ORM to ShoppingListResponse-compatible dict."""
        try:
            # Ensure items are loaded
            items_list = []
            try:
                if hasattr(shopping_list, 'items'):
                    items_list = list(shopping_list.items)
                if not items_list:
                    items_list = list(getattr(shopping_list, 'items', []))
                
                # If items still aren't loaded and we have a db session, query directly
                if (not items_list or len(items_list) == 0) and db is not None:
                    logger.warning(f"No items found via relationship for shopping list {shopping_list.id}, querying directly from database")
                    items_list = db.query(ShoppingListItem).filter(
                        ShoppingListItem.shopping_list_id == shopping_list.id
                    ).all()
            except Exception as e:
                logger.error(f"Error loading shopping list items: {str(e)}")
            
            # Convert items to dict format
            items_response = []
            purchased_count = 0
            for item in items_list:
                # Get ingredient name if available
                ingredient_name = None
                if hasattr(item, 'ingredient') and item.ingredient:
                    ingredient_name = item.ingredient.name
                elif db is not None:
                    # Try to fetch ingredient from database
                    try:
                        ingredient = db.query(Ingredient).filter(Ingredient.id == item.ingredient_id).first()
                        if ingredient:
                            ingredient_name = ingredient.name
                    except Exception as e:
                        logger.warning(f"Could not load ingredient {item.ingredient_id}: {str(e)}")
                
                items_response.append({
                    "id": item.id,
                    "ingredient_id": item.ingredient_id,
                    "ingredient_name": ingredient_name or f"ingredient_{item.ingredient_id}",
                    "quantity": float(item.quantity),
                    "unit": item.unit,
                    "category": item.category,
                    "is_purchased": bool(item.is_purchased),
                    "notes": item.notes or ""
                })
                if item.is_purchased:
                    purchased_count += 1
            
            return {
                "id": shopping_list.id,
                "user_id": shopping_list.user_id,
                "list_name": shopping_list.list_name,
                "meal_plan_id": shopping_list.meal_plan_id,
                "is_active": getattr(shopping_list, 'is_active', True),
                "items": items_response,
                "total_items": len(items_response),
                "purchased_items": purchased_count,
                "created_at": (getattr(shopping_list, 'created_at', datetime.utcnow()).isoformat() if hasattr(getattr(shopping_list, 'created_at', datetime.utcnow()), 'isoformat') else str(getattr(shopping_list, 'created_at', datetime.utcnow()))),
                "updated_at": (getattr(shopping_list, 'updated_at', datetime.utcnow()).isoformat() if getattr(shopping_list, 'updated_at', None) and hasattr(getattr(shopping_list, 'updated_at'), 'isoformat') else (str(getattr(shopping_list, 'updated_at')) if getattr(shopping_list, 'updated_at', None) else None))
            }
        except Exception as e:
            logger.error(f"Error converting shopping list to response: {str(e)}")
            # Return minimal response on error
            return {
                "id": shopping_list.id,
                "user_id": shopping_list.user_id,
                "list_name": shopping_list.list_name,
                "meal_plan_id": shopping_list.meal_plan_id,
                "is_active": getattr(shopping_list, 'is_active', True),
                "items": [],
                "total_items": 0,
                "purchased_items": 0,
                "created_at": (getattr(shopping_list, 'created_at', datetime.utcnow()).isoformat() if hasattr(getattr(shopping_list, 'created_at', datetime.utcnow()), 'isoformat') else str(getattr(shopping_list, 'created_at', datetime.utcnow()))),
                "updated_at": (getattr(shopping_list, 'updated_at', datetime.utcnow()).isoformat() if getattr(shopping_list, 'updated_at', None) and hasattr(getattr(shopping_list, 'updated_at'), 'isoformat') else (str(getattr(shopping_list, 'updated_at')) if getattr(shopping_list, 'updated_at', None) else None))
            }
    
    def get_nutritional_analysis(self, db: Session, user_id: int, start_date: date, end_date: date, analysis_type: str = "daily") -> Dict[str, Any]:
        """Aggregate nutrition from NutritionalLog (consumed meals) between dates for a user.
        Prioritizes NutritionalLog over MealPlanMeal since logs represent actual consumption."""
        try:
            # CRITICAL: Query NutritionalLog first (actual consumed meals)
            # This is what users have actually logged/eaten, not just planned
            logs = db.query(NutritionalLog).filter(
                and_(
                    NutritionalLog.user_id == user_id,
                    NutritionalLog.log_date >= start_date,
                    NutritionalLog.log_date <= end_date
                )
            ).all()
            
            logger.info(f"Found {len(logs)} nutritional log entries for user {user_id} between {start_date} and {end_date}")
            
            totals = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fats": 0.0}
            by_day: Dict[date, Dict[str, float]] = {}
            
            # Aggregate from NutritionalLog (consumed meals)
            for log in logs:
                d = log.log_date
                if d not in by_day:
                    by_day[d] = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fats": 0.0}
                by_day[d]["calories"] += float(log.calories or 0)
                by_day[d]["protein"] += float(log.protein or 0)
                by_day[d]["carbs"] += float(log.carbs or 0)
                by_day[d]["fats"] += float(log.fats or 0)
                totals["calories"] += float(log.calories or 0)
                totals["protein"] += float(log.protein or 0)
                totals["carbs"] += float(log.carbs or 0)
                totals["fats"] += float(log.fats or 0)
            
            # If no logs found, fall back to meal plans (planned meals)
            if not logs:
                logger.info(f"No nutritional logs found, falling back to meal plans")
                plans = db.query(MealPlan).filter(
                    and_(MealPlan.user_id == user_id, MealPlan.start_date >= start_date, MealPlan.start_date <= end_date)
                ).all()
                plan_ids = [p.id for p in plans]
                if plan_ids:
                    meals = db.query(MealPlanMeal).filter(MealPlanMeal.meal_plan_id.in_(plan_ids)).all()
                    logger.info(f"Found {len(meals)} meal plan meals to aggregate")
                    for m in meals:
                        d = m.meal_date
                        if d < start_date or d > end_date:
                            continue
                        if d not in by_day:
                            by_day[d] = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fats": 0.0}
                        by_day[d]["calories"] += float(m.calories or 0)
                        by_day[d]["protein"] += float(m.protein or 0)
                        by_day[d]["carbs"] += float(m.carbs or 0)
                        by_day[d]["fats"] += float(m.fats or 0)
                        totals["calories"] += float(m.calories or 0)
                        totals["protein"] += float(m.protein or 0)
                        totals["carbs"] += float(m.carbs or 0)
                        totals["fats"] += float(m.fats or 0)
            
            days_list = [
                {"date": d, "calories": round(v["calories"], 1), "protein": round(v["protein"], 1), "carbs": round(v["carbs"], 1), "fats": round(v["fats"], 1)}
                for d, v in sorted(by_day.items(), key=lambda x: x[0])
            ]
            
            logger.info(f"Nutritional analysis totals: calories={totals['calories']}, protein={totals['protein']}, carbs={totals['carbs']}, fats={totals['fats']}")
            
            return {"totals": {k: round(v, 1) for k, v in totals.items()}, "days": days_list, "analysis_type": analysis_type}
        except Exception as e:
            logger.error(f"Error computing nutritional analysis: {str(e)}", exc_info=True)
            return {"totals": {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}, "days": [], "error": str(e)}

    def _estimate_nutrition_from_ingredients(self, ingredients: Any) -> Dict[str, int]:
        """Very rough nutrition estimate from ingredient names and quantities.
        Uses per-100g approximations for common items; fallback minimal values."""
        per100g = {
            # name: (cal, protein, carbs, fats)
            "chicken breast": (165, 31, 0, 3.6),
            "chickpea": (364, 19, 61, 6),
            "chickpeas": (364, 19, 61, 6),
            "olive oil": (884, 0, 0, 100),
            "tomato": (18, 0.9, 3.9, 0.2),
            "cucumber": (16, 0.7, 3.6, 0.1),
            "lettuce": (15, 1.4, 2.9, 0.2),
            "bell pepper": (31, 1, 6, 0.3),
            "pepper": (31, 1, 6, 0.3),
            "carrot": (41, 0.9, 10, 0.2),
            "onion": (40, 1.1, 9.3, 0.1),
            "garlic": (149, 6.4, 33, 0.5),
            "feta": (265, 14, 4, 21),
            "rice": (130, 2.4, 28, 0.3),
            "quinoa": (120, 4.4, 21, 1.9),
            "pasta": (131, 5, 25, 1.1),
            "hummus": (166, 8, 14, 9.6),
            "yogurt": (59, 10, 3.6, 0.4),
        }
        total = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fats": 0.0}
        for item in (ingredients or []):
            if isinstance(item, dict):
                name = str(item.get("name", "")).lower()
                qty = float(item.get("quantity", 0) or 0)
                unit = str(item.get("unit", "g")).lower()
            else:
                name = str(item).lower()
                qty = 0.0
                unit = "g"
            # convert to grams heuristic for ml
            grams = qty
            if unit in ["ml"]:
                grams = qty  # assume density ~1
            # find key match
            key = next((k for k in per100g.keys() if k in name), None)
            if not key or grams <= 0:
                continue
            cal, p, c, f = per100g[key]
            factor = grams / 100.0
            total["calories"] += cal * factor
            total["protein"] += p * factor
            total["carbs"] += c * factor
            total["fats"] += f * factor
        return {k: int(round(v)) for k, v in total.items()}
