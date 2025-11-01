from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc
from models.nutrition import MealPlan, MealPlanMeal, MealPlanRecipe
from models.recipe import Recipe, RecipeIngredient, RecipeInstruction
from schemas.nutrition import MealPlanMealCreate, MealPlanMealResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import json

class MealPlanRecipeService:
    
    def add_recipe_to_meal_plan(
        self, 
        db: Session, 
        meal_plan_id: str, 
        recipe_id: str, 
        meal_date: date,
        meal_type: str,
        servings: float = 1.0,
        meal_time: Optional[datetime] = None,
        custom_meal_name: Optional[str] = None
    ) -> MealPlanMealResponse:
        """
        Add a recipe to a meal plan with proper serving size adjustments
        """
        # Get the meal plan
        meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
        if not meal_plan:
            raise ValueError("Meal plan not found")
        
        # Get the recipe with all related data
        recipe = db.query(Recipe).options(
            joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient),
            joinedload(Recipe.instructions)
        ).filter(Recipe.id == recipe_id).first()
        
        if not recipe:
            raise ValueError("Recipe not found")
        
        # Calculate scaled nutrition values
        scaled_nutrition = self._calculate_scaled_nutrition(recipe, servings)
        
        # Create or get existing meal for this date and type
        existing_meal = db.query(MealPlanMeal).filter(
            and_(
                MealPlanMeal.meal_plan_id == meal_plan_id,
                MealPlanMeal.meal_date == meal_date,
                MealPlanMeal.meal_type == meal_type
            )
        ).first()
        
        if existing_meal:
            # Update existing meal with new recipe
            return self._update_existing_meal_with_recipe(
                db, existing_meal, recipe, servings, scaled_nutrition
            )
        else:
            # Create new meal with recipe
            return self._create_new_meal_with_recipe(
                db, meal_plan_id, recipe, meal_date, meal_type, 
                servings, scaled_nutrition, meal_time, custom_meal_name
            )
    
    def update_recipe_servings(
        self, 
        db: Session, 
        meal_plan_id: str, 
        meal_id: int, 
        recipe_id: str, 
        new_servings: float
    ) -> MealPlanMealResponse:
        """
        Update the serving size of a recipe in a meal plan
        """
        # Get the meal plan recipe relationship
        meal_plan_recipe = db.query(MealPlanRecipe).filter(
            and_(
                MealPlanRecipe.meal_plan_id == meal_plan_id,
                MealPlanRecipe.meal_id == meal_id,
                MealPlanRecipe.recipe_id == recipe_id
            )
        ).first()
        
        if not meal_plan_recipe:
            raise ValueError("Recipe not found in meal plan")
        
        # Get the recipe
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            raise ValueError("Recipe not found")
        
        # Update servings
        meal_plan_recipe.servings = new_servings
        db.add(meal_plan_recipe)
        
        # Recalculate nutrition for the meal
        meal = db.query(MealPlanMeal).filter(MealPlanMeal.id == meal_id).first()
        if meal:
            self._recalculate_meal_nutrition(db, meal)
            db.add(meal)
        
        db.commit()
        db.refresh(meal)
        
        return self._format_meal_response(meal)
    
    def remove_recipe_from_meal_plan(
        self, 
        db: Session, 
        meal_plan_id: str, 
        meal_id: int, 
        recipe_id: str
    ) -> bool:
        """
        Remove a recipe from a meal plan
        """
        # Get the meal plan recipe relationship
        meal_plan_recipe = db.query(MealPlanRecipe).filter(
            and_(
                MealPlanRecipe.meal_plan_id == meal_plan_id,
                MealPlanRecipe.meal_id == meal_id,
                MealPlanRecipe.recipe_id == recipe_id
            )
        ).first()
        
        if not meal_plan_recipe:
            return False
        
        # Remove the relationship
        db.delete(meal_plan_recipe)
        
        # Recalculate nutrition for the meal
        meal = db.query(MealPlanMeal).filter(MealPlanMeal.id == meal_id).first()
        if meal:
            self._recalculate_meal_nutrition(db, meal)
            db.add(meal)
        
        db.commit()
        return True
    
    def get_meal_plan_recipes(
        self, 
        db: Session, 
        meal_plan_id: str, 
        meal_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all recipes in a meal plan with their details
        """
        query = db.query(MealPlanRecipe).filter(MealPlanRecipe.meal_plan_id == meal_plan_id)
        
        if meal_date:
            query = query.join(MealPlanMeal).filter(MealPlanMeal.meal_date == meal_date)
        
        meal_plan_recipes = query.options(
            joinedload(MealPlanRecipe.recipe)
        ).all()
        
        return [
            {
                "id": mpr.id,
                "meal_plan_id": mpr.meal_plan_id,
                "meal_id": mpr.meal_id,
                "recipe_id": mpr.recipe_id,
                "servings": mpr.servings,
                "is_alternative": mpr.is_alternative,
                "recipe": {
                    "id": mpr.recipe.id,
                    "title": mpr.recipe.title,
                    "description": mpr.recipe.description,
                    "cuisine": mpr.recipe.cuisine,
                    "meal_type": mpr.recipe.meal_type,
                    "prep_time": mpr.recipe.prep_time,
                    "cook_time": mpr.recipe.cook_time,
                    "difficulty_level": mpr.recipe.difficulty_level,
                    "servings": mpr.recipe.servings,
                    "image_url": mpr.recipe.image_url,
                    "dietary_tags": mpr.recipe.dietary_tags,
                    "allergens": mpr.recipe.allergens,
                    # Scaled nutrition based on servings
                    "calories": mpr.recipe.per_serving_calories * mpr.servings if mpr.recipe.per_serving_calories else None,
                    "protein": mpr.recipe.per_serving_protein * mpr.servings if mpr.recipe.per_serving_protein else None,
                    "carbs": mpr.recipe.per_serving_carbs * mpr.servings if mpr.recipe.per_serving_carbs else None,
                    "fat": mpr.recipe.per_serving_fat * mpr.servings if mpr.recipe.per_serving_fat else None,
                    "sodium": mpr.recipe.per_serving_sodium * mpr.servings if mpr.recipe.per_serving_sodium else None,
                }
            }
            for mpr in meal_plan_recipes
        ]
    
    def suggest_serving_adjustments(
        self, 
        db: Session, 
        meal_plan_id: str, 
        target_calories: Optional[float] = None,
        target_protein: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Suggest serving size adjustments to meet nutritional targets
        """
        # Get all recipes in the meal plan
        recipes = self.get_meal_plan_recipes(db, meal_plan_id)
        
        suggestions = []
        
        for recipe_data in recipes:
            recipe = recipe_data["recipe"]
            current_servings = recipe_data["servings"]
            
            # Calculate adjustment factors
            adjustments = {}
            
            if target_calories and recipe["calories"]:
                calorie_factor = target_calories / recipe["calories"]
                if 0.5 <= calorie_factor <= 2.0:  # Reasonable adjustment range
                    adjustments["calories"] = {
                        "factor": calorie_factor,
                        "new_servings": current_servings * calorie_factor,
                        "new_calories": recipe["calories"] * calorie_factor
                    }
            
            if target_protein and recipe["protein"]:
                protein_factor = target_protein / recipe["protein"]
                if 0.5 <= protein_factor <= 2.0:  # Reasonable adjustment range
                    adjustments["protein"] = {
                        "factor": protein_factor,
                        "new_servings": current_servings * protein_factor,
                        "new_protein": recipe["protein"] * protein_factor
                    }
            
            if adjustments:
                suggestions.append({
                    "recipe_id": recipe["id"],
                    "recipe_title": recipe["title"],
                    "current_servings": current_servings,
                    "adjustments": adjustments
                })
        
        return suggestions
    
    def _calculate_scaled_nutrition(self, recipe: Recipe, servings: float) -> Dict[str, float]:
        """
        Calculate nutrition values scaled by serving size
        """
        scale_factor = servings / (recipe.servings or 1)
        
        return {
            "calories": (recipe.per_serving_calories or 0) * servings,
            "protein": (recipe.per_serving_protein or 0) * servings,
            "carbs": (recipe.per_serving_carbs or 0) * servings,
            "fat": (recipe.per_serving_fat or 0) * servings,
            "sodium": (recipe.per_serving_sodium or 0) * servings
        }
    
    def _create_new_meal_with_recipe(
        self, 
        db: Session, 
        meal_plan_id: str, 
        recipe: Recipe, 
        meal_date: date, 
        meal_type: str,
        servings: float, 
        scaled_nutrition: Dict[str, float],
        meal_time: Optional[datetime] = None,
        custom_meal_name: Optional[str] = None
    ) -> MealPlanMealResponse:
        """
        Create a new meal with a recipe
        """
        # Create the meal
        meal = MealPlanMeal(
            meal_plan_id=meal_plan_id,
            meal_date=meal_date,
            meal_type=meal_type,
            meal_time=meal_time,
            meal_name=custom_meal_name or recipe.title,
            calories=scaled_nutrition["calories"],
            protein=scaled_nutrition["protein"],
            carbs=scaled_nutrition["carbs"],
            fats=scaled_nutrition["fat"],
            cuisine=recipe.cuisine,
            recipe_details=self._serialize_recipe_details(recipe, servings)
        )
        
        db.add(meal)
        db.flush()  # Get the meal ID
        
        # Create the meal plan recipe relationship
        meal_plan_recipe = MealPlanRecipe(
            meal_plan_id=meal_plan_id,
            meal_id=meal.id,
            recipe_id=recipe.id,
            servings=servings
        )
        
        db.add(meal_plan_recipe)
        db.commit()
        db.refresh(meal)
        
        return self._format_meal_response(meal)
    
    def _update_existing_meal_with_recipe(
        self, 
        db: Session, 
        existing_meal: MealPlanMeal, 
        recipe: Recipe, 
        servings: float, 
        scaled_nutrition: Dict[str, float]
    ) -> MealPlanMealResponse:
        """
        Update an existing meal with a new recipe
        """
        # Add the recipe to the existing meal
        meal_plan_recipe = MealPlanRecipe(
            meal_plan_id=existing_meal.meal_plan_id,
            meal_id=existing_meal.id,
            recipe_id=recipe.id,
            servings=servings
        )
        
        db.add(meal_plan_recipe)
        
        # Update meal nutrition (add to existing values)
        existing_meal.calories += scaled_nutrition["calories"]
        existing_meal.protein += scaled_nutrition["protein"]
        existing_meal.carbs += scaled_nutrition["carbs"]
        existing_meal.fats += scaled_nutrition["fat"]
        
        # Update recipe details (append to existing)
        existing_details = existing_meal.recipe_details or {}
        recipe_details = self._serialize_recipe_details(recipe, servings)
        
        if "recipes" not in existing_details:
            existing_details["recipes"] = []
        
        existing_details["recipes"].append(recipe_details)
        existing_meal.recipe_details = existing_details
        
        db.add(existing_meal)
        db.commit()
        db.refresh(existing_meal)
        
        return self._format_meal_response(existing_meal)
    
    def _recalculate_meal_nutrition(self, db: Session, meal: MealPlanMeal):
        """
        Recalculate nutrition for a meal based on all its recipes
        """
        # Get all recipes for this meal
        meal_recipes = db.query(MealPlanRecipe).filter(
            MealPlanRecipe.meal_id == meal.id
        ).options(joinedload(MealPlanRecipe.recipe)).all()
        
        # Reset nutrition values
        meal.calories = 0
        meal.protein = 0
        meal.carbs = 0
        meal.fats = 0
        
        # Recalculate based on all recipes
        recipe_details = []
        for meal_recipe in meal_recipes:
            recipe = meal_recipe.recipe
            servings = meal_recipe.servings
            
            scaled_nutrition = self._calculate_scaled_nutrition(recipe, servings)
            
            meal.calories += scaled_nutrition["calories"]
            meal.protein += scaled_nutrition["protein"]
            meal.carbs += scaled_nutrition["carbs"]
            meal.fats += scaled_nutrition["fat"]
            
            recipe_details.append(self._serialize_recipe_details(recipe, servings))
        
        # Update recipe details
        meal.recipe_details = {"recipes": recipe_details}
    
    def _serialize_recipe_details(self, recipe: Recipe, servings: float) -> Dict[str, Any]:
        """
        Serialize recipe details for storage in meal
        """
        return {
            "id": recipe.id,
            "title": recipe.title,
            "description": recipe.description,
            "cuisine": recipe.cuisine,
            "meal_type": recipe.meal_type,
            "prep_time": recipe.prep_time,
            "cook_time": recipe.cook_time,
            "difficulty_level": recipe.difficulty_level,
            "servings": servings,
            "image_url": recipe.image_url,
            "dietary_tags": recipe.dietary_tags,
            "allergens": recipe.allergens,
            "ingredients": [
                {
                    "name": ri.ingredient.name if ri.ingredient else "Unknown",
                    "quantity": ri.quantity * servings,
                    "unit": ri.unit,
                    "notes": ri.notes
                }
                for ri in recipe.ingredients
            ],
            "instructions": [
                {
                    "step": inst.step_number,
                    "instruction": inst.instruction,
                    "time_minutes": inst.time_minutes
                }
                for inst in recipe.instructions
            ],
            "nutrition": {
                "calories": (recipe.per_serving_calories or 0) * servings,
                "protein": (recipe.per_serving_protein or 0) * servings,
                "carbs": (recipe.per_serving_carbs or 0) * servings,
                "fat": (recipe.per_serving_fat or 0) * servings,
                "sodium": (recipe.per_serving_sodium or 0) * servings
            }
        }
    
    def _format_meal_response(self, meal: MealPlanMeal) -> MealPlanMealResponse:
        """
        Format meal for API response
        """
        return MealPlanMealResponse(
            id=meal.id,
            meal_plan_id=meal.meal_plan_id,
            meal_date=meal.meal_date,
            meal_type=meal.meal_type,
            meal_time=meal.meal_time,
            meal_name=meal.meal_name,
            calories=meal.calories,
            protein=meal.protein,
            carbs=meal.carbs,
            fats=meal.fats,
            recipe_details=meal.recipe_details,
            cuisine=meal.cuisine,
            created_at=meal.created_at,
            updated_at=meal.updated_at
        )







