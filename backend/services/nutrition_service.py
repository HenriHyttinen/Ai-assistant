import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from models.nutrition import (
    MealPlan, MealPlanMeal, MealPlanRecipe, Recipe, Ingredient,
    NutritionalLog, ShoppingList, ShoppingListItem, UserNutritionPreferences
)
from schemas.nutrition import (
    MealPlanRequest, RecipeSearchRequest, ShoppingListCreate,
    NutritionalAnalysisRequest
)
from ai.nutrition_ai import NutritionAI

logger = logging.getLogger(__name__)

class NutritionService:
    def __init__(self):
        self.nutrition_ai = NutritionAI()
    
    def create_meal_plan(self, db: Session, user_id: int, plan_request: MealPlanRequest, ai_meal_plan: Dict[str, Any]) -> MealPlan:
        """Create meal plan from AI generation"""
        try:
            # Create meal plan record
            meal_plan = MealPlan(
                id=f"mp_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                user_id=user_id,
                plan_type=plan_request.plan_type,
                start_date=plan_request.start_date,
                end_date=plan_request.end_date,
                generation_strategy=ai_meal_plan.get("strategy", {}),
                ai_model_used="gpt-3.5-turbo"
            )
            db.add(meal_plan)
            db.flush()
            
            # Create meals and recipes
            for day_data in ai_meal_plan.get("meal_plan", []):
                meal_date = datetime.strptime(day_data["date"], "%Y-%m-%d").date()
                
                for meal_data in day_data.get("meals", []):
                    # Create meal
                    meal = MealPlanMeal(
                        meal_plan_id=meal_plan.id,
                        meal_date=meal_date,
                        meal_type=meal_data["meal_type"],
                        meal_name=meal_data["meal_name"],
                        calories=meal_data.get("recipe", {}).get("nutrition", {}).get("calories", 0),
                        protein=meal_data.get("recipe", {}).get("nutrition", {}).get("protein", 0),
                        carbs=meal_data.get("recipe", {}).get("nutrition", {}).get("carbs", 0),
                        fats=meal_data.get("recipe", {}).get("nutrition", {}).get("fats", 0)
                    )
                    db.add(meal)
                    db.flush()
                    
                    # Create recipe if provided
                    recipe_data = meal_data.get("recipe")
                    if recipe_data:
                        recipe = self._create_recipe_from_ai(db, recipe_data)
                        if recipe:
                            # Link recipe to meal
                            meal_recipe = MealPlanRecipe(
                                meal_plan_id=meal_plan.id,
                                meal_id=meal.id,
                                recipe_id=recipe.id,
                                servings=recipe_data.get("servings", 1)
                            )
                            db.add(meal_recipe)
            
            db.commit()
            db.refresh(meal_plan)
            return meal_plan
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating meal plan: {str(e)}")
            raise
    
    def _create_recipe_from_ai(self, db: Session, recipe_data: Dict[str, Any]) -> Optional[Recipe]:
        """Create recipe from AI-generated data"""
        try:
            recipe = Recipe(
                id=f"r_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(recipe_data.get('title', '')) % 10000}",
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
            
            # Add ingredients and instructions
            self._add_recipe_ingredients(db, recipe.id, recipe_data.get("ingredients", []))
            self._add_recipe_instructions(db, recipe.id, recipe_data.get("instructions", []))
            
            return recipe
            
        except Exception as e:
            logger.error(f"Error creating recipe from AI: {str(e)}")
            return None
    
    def _add_recipe_ingredients(self, db: Session, recipe_id: str, ingredients_data: List[Dict[str, Any]]):
        """Add ingredients to recipe"""
        for ing_data in ingredients_data:
            # Find or create ingredient
            ingredient = db.query(Ingredient).filter(
                Ingredient.name.ilike(f"%{ing_data.get('name', '')}%")
            ).first()
            
            if not ingredient:
                # Create new ingredient
                ingredient = Ingredient(
                    id=f"ing_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(ing_data.get('name', '')) % 10000}",
                    name=ing_data.get("name", "Unknown Ingredient"),
                    category=self._categorize_ingredient(ing_data.get("name", "")),
                    unit=ing_data.get("unit", "g"),
                    default_quantity=100.0
                )
                db.add(ingredient)
                db.flush()
            
            # Create recipe-ingredient relationship
            from models.nutrition import RecipeIngredient
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe_id,
                ingredient_id=ingredient.id,
                quantity=ing_data.get("quantity", 0),
                unit=ing_data.get("unit", "g")
            )
            db.add(recipe_ingredient)
    
    def _add_recipe_instructions(self, db: Session, recipe_id: str, instructions_data: List[Dict[str, Any]]):
        """Add instructions to recipe"""
        for i, inst_data in enumerate(instructions_data, 1):
            from models.nutrition import RecipeInstruction
            instruction = RecipeInstruction(
                recipe_id=recipe_id,
                step_number=i,
                step_title=inst_data.get("step_title", f"Step {i}"),
                description=inst_data.get("description", ""),
                ingredients_used=inst_data.get("ingredients_used", []),
                time_required=inst_data.get("time_required")
            )
            db.add(instruction)
    
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
    
    def search_recipes(self, db: Session, search_request: RecipeSearchRequest) -> List[Recipe]:
        """Search recipes with filters"""
        try:
            query = db.query(Recipe).filter(Recipe.is_active == True)
            
            # Text search
            if search_request.query:
                query = query.filter(
                    or_(
                        Recipe.title.ilike(f"%{search_request.query}%"),
                        Recipe.summary.ilike(f"%{search_request.query}%")
                    )
                )
            
            # Cuisine filter
            if search_request.cuisine:
                query = query.filter(Recipe.cuisine.ilike(f"%{search_request.cuisine}%"))
            
            # Meal type filter
            if search_request.meal_type:
                query = query.filter(Recipe.meal_type == search_request.meal_type)
            
            # Dietary tags filter
            if search_request.dietary_tags:
                for tag in search_request.dietary_tags:
                    query = query.filter(Recipe.dietary_tags.contains([tag]))
            
            # Difficulty filter
            if search_request.difficulty_level:
                query = query.filter(Recipe.difficulty_level == search_request.difficulty_level)
            
            # Time filter
            if search_request.max_prep_time:
                query = query.filter(Recipe.prep_time <= search_request.max_prep_time)
            
            # Limit results
            query = query.limit(search_request.limit)
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error searching recipes: {str(e)}")
            return []
    
    def create_shopping_list(self, db: Session, user_id: int, shopping_list_data: ShoppingListCreate) -> ShoppingList:
        """Create shopping list from meal plan or manual items"""
        try:
            shopping_list = ShoppingList(
                id=f"sl_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                user_id=user_id,
                list_name=shopping_list_data.list_name,
                meal_plan_id=shopping_list_data.meal_plan_id
            )
            db.add(shopping_list)
            db.flush()
            
            # Add items
            for item_data in shopping_list_data.items:
                item = ShoppingListItem(
                    shopping_list_id=shopping_list.id,
                    ingredient_id=item_data.ingredient_id,
                    quantity=item_data.quantity,
                    unit=item_data.unit,
                    category=self._categorize_ingredient_by_id(db, item_data.ingredient_id),
                    notes=item_data.notes
                )
                db.add(item)
            
            db.commit()
            db.refresh(shopping_list)
            return shopping_list
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating shopping list: {str(e)}")
            raise
    
    def _categorize_ingredient_by_id(self, db: Session, ingredient_id: str) -> str:
        """Get ingredient category by ID"""
        ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
        return ingredient.category if ingredient else "other"
    
    def get_nutritional_analysis(self, db: Session, user_id: int, start_date: date, end_date: date, analysis_type: str) -> Dict[str, Any]:
        """Get comprehensive nutritional analysis"""
        try:
            # Get nutritional logs for the period
            logs = db.query(NutritionalLog).filter(
                NutritionalLog.user_id == user_id,
                NutritionalLog.log_date >= start_date,
                NutritionalLog.log_date <= end_date
            ).all()
            
            # Calculate totals
            total_calories = sum(log.calories for log in logs)
            total_protein = sum(log.protein for log in logs)
            total_carbs = sum(log.carbs for log in logs)
            total_fats = sum(log.fats for log in logs)
            
            # Get user targets
            preferences = db.query(UserNutritionPreferences).filter(
                UserNutritionPreferences.user_id == user_id
            ).first()
            
            targets = {
                "calories": preferences.daily_calorie_target if preferences else 2000,
                "protein": preferences.protein_target if preferences else 100,
                "carbs": preferences.carbs_target if preferences else 200,
                "fats": preferences.fats_target if preferences else 60
            }
            
            # Calculate deficits/surpluses
            calorie_deficit = targets["calories"] - total_calories
            protein_deficit = targets["protein"] - total_protein
            carbs_deficit = targets["carbs"] - total_carbs
            fats_deficit = targets["fats"] - total_fats
            
            # Generate AI insights
            ai_insights = self._generate_nutritional_insights(
                total_calories, total_protein, total_carbs, total_fats,
                targets, calorie_deficit, protein_deficit, carbs_deficit, fats_deficit
            )
            
            return {
                "period": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "analysis_type": analysis_type
                },
                "totals": {
                    "calories": total_calories,
                    "protein": total_protein,
                    "carbs": total_carbs,
                    "fats": total_fats
                },
                "targets": targets,
                "deficits": {
                    "calories": calorie_deficit,
                    "protein": protein_deficit,
                    "carbs": carbs_deficit,
                    "fats": fats_deficit
                },
                "percentages": {
                    "calories": (total_calories / targets["calories"]) * 100 if targets["calories"] > 0 else 0,
                    "protein": (total_protein / targets["protein"]) * 100 if targets["protein"] > 0 else 0,
                    "carbs": (total_carbs / targets["carbs"]) * 100 if targets["carbs"] > 0 else 0,
                    "fats": (total_fats / targets["fats"]) * 100 if targets["fats"] > 0 else 0
                },
                "ai_insights": ai_insights,
                "daily_breakdown": self._get_daily_breakdown(logs)
            }
            
        except Exception as e:
            logger.error(f"Error getting nutritional analysis: {str(e)}")
            return {}
    
    def _generate_nutritional_insights(self, calories: float, protein: float, carbs: float, fats: float,
                                      targets: Dict[str, float], calorie_deficit: float, protein_deficit: float,
                                      carbs_deficit: float, fats_deficit: float) -> Dict[str, Any]:
        """Generate AI-powered nutritional insights"""
        insights = {
            "achievements": [],
            "concerns": [],
            "suggestions": []
        }
        
        # Analyze calorie intake
        calorie_percentage = (calories / targets["calories"]) * 100 if targets["calories"] > 0 else 0
        
        if calorie_percentage >= 95 and calorie_percentage <= 105:
            insights["achievements"].append("Excellent calorie target adherence!")
        elif calorie_percentage < 80:
            insights["concerns"].append("Significant calorie deficit - consider increasing portion sizes")
            insights["suggestions"].append("Add healthy snacks between meals")
        elif calorie_percentage > 120:
            insights["concerns"].append("Calorie surplus - consider reducing portion sizes")
            insights["suggestions"].append("Focus on nutrient-dense, lower-calorie foods")
        
        # Analyze protein intake
        protein_percentage = (protein / targets["protein"]) * 100 if targets["protein"] > 0 else 0
        
        if protein_percentage >= 90:
            insights["achievements"].append("Great protein intake for muscle maintenance!")
        elif protein_percentage < 70:
            insights["concerns"].append("Low protein intake")
            insights["suggestions"].append("Include lean proteins like chicken, fish, or legumes in each meal")
        
        # Analyze macro balance
        if protein_percentage > 120 and carbs_percentage < 80:
            insights["suggestions"].append("Consider adding more complex carbohydrates for energy")
        elif carbs_percentage > 120 and protein_percentage < 80:
            insights["suggestions"].append("Balance your meals with more protein sources")
        
        return insights
    
    def _get_daily_breakdown(self, logs: List[NutritionalLog]) -> List[Dict[str, Any]]:
        """Get daily nutritional breakdown"""
        daily_data = {}
        
        for log in logs:
            date_str = log.log_date.isoformat()
            if date_str not in daily_data:
                daily_data[date_str] = {
                    "date": date_str,
                    "calories": 0,
                    "protein": 0,
                    "carbs": 0,
                    "fats": 0,
                    "meals": []
                }
            
            daily_data[date_str]["calories"] += log.calories
            daily_data[date_str]["protein"] += log.protein
            daily_data[date_str]["carbs"] += log.carbs
            daily_data[date_str]["fats"] += log.fats
            daily_data[date_str]["meals"].append({
                "meal_type": log.meal_type,
                "calories": log.calories,
                "protein": log.protein,
                "carbs": log.carbs,
                "fats": log.fats
            })
        
        return list(daily_data.values())
