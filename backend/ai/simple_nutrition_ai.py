"""
Simple Nutrition AI Implementation

This is a simplified version that doesn't require heavy ML dependencies.
"""

import json
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class SimpleNutritionAI:
    """Simple nutrition AI without heavy ML dependencies"""
    
    def __init__(self):
        self.model_name = "simple-nutrition-ai"
        self.available_diets = [
            "vegetarian", "vegan", "keto", "paleo", "mediterranean", 
            "low-carb", "high-protein", "gluten-free", "dairy-free",
            "nut-free", "soy-free", "low-sodium", "diabetic-friendly",
            "heart-healthy", "anti-inflammatory"
        ]
        
        self.available_allergies = [
            "nuts", "dairy", "eggs", "soy", "gluten", "shellfish",
            "fish", "sesame", "sulfites", "mustard"
        ]
        
        self.cuisine_types = [
            "Italian", "Mexican", "Asian", "Mediterranean", "American",
            "Indian", "Thai", "French", "Japanese", "Chinese"
        ]
    
    def generate_meal_plan(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a simple meal plan based on preferences"""
        
        # Extract preferences
        dietary_preferences = preferences.get("dietary_preferences", [])
        allergies = preferences.get("allergies", [])
        cuisine_preferences = preferences.get("cuisine_preferences", ["International"])
        calorie_target = preferences.get("daily_calorie_target", 2000)
        meals_per_day = preferences.get("meals_per_day", 3)
        
        # Generate meals
        meals = []
        meal_types = ["breakfast", "lunch", "dinner"]
        
        for i, meal_type in enumerate(meal_types[:meals_per_day]):
            meal = self._generate_meal(
                meal_type=meal_type,
                dietary_preferences=dietary_preferences,
                allergies=allergies,
                cuisine_preferences=cuisine_preferences,
                calorie_target=calorie_target // meals_per_day
            )
            meals.append(meal)
        
        return {
            "meal_plan": {
                "id": f"mp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "user_id": preferences.get("user_id", 1),
                "plan_type": "daily",
                "start_date": datetime.now().date().isoformat(),
                "end_date": datetime.now().date().isoformat(),
                "version": "1.0",
                "meals": meals,
                "total_calories": sum(meal["calories"] for meal in meals),
                "total_protein": sum(meal["protein"] for meal in meals),
                "total_carbs": sum(meal["carbs"] for meal in meals),
                "total_fats": sum(meal["fats"] for meal in meals)
            }
        }
    
    def _generate_meal(self, meal_type: str, dietary_preferences: List[str], 
                      allergies: List[str], cuisine_preferences: List[str], 
                      calorie_target: int) -> Dict[str, Any]:
        """Generate a single meal"""
        
        # Base meal templates
        meal_templates = {
            "breakfast": [
                {"name": "Protein Smoothie Bowl", "calories": 350, "protein": 25, "carbs": 30, "fats": 12},
                {"name": "Mediterranean Omelet", "calories": 400, "protein": 28, "carbs": 15, "fats": 25},
                {"name": "Quinoa Breakfast Bowl", "calories": 380, "protein": 15, "carbs": 45, "fats": 18}
            ],
            "lunch": [
                {"name": "Grilled Chicken Salad", "calories": 450, "protein": 35, "carbs": 20, "fats": 25},
                {"name": "Quinoa Buddha Bowl", "calories": 420, "protein": 18, "carbs": 50, "fats": 15},
                {"name": "Mediterranean Wrap", "calories": 480, "protein": 22, "carbs": 35, "fats": 28}
            ],
            "dinner": [
                {"name": "Baked Salmon with Vegetables", "calories": 550, "protein": 40, "carbs": 25, "fats": 30},
                {"name": "Vegetarian Stir-Fry", "calories": 420, "protein": 20, "carbs": 45, "fats": 18},
                {"name": "Mediterranean Pasta", "calories": 480, "protein": 18, "carbs": 60, "fats": 20}
            ]
        }
        
        # Select appropriate template
        templates = meal_templates.get(meal_type, meal_templates["lunch"])
        selected_meal = random.choice(templates)
        
        # Adjust for dietary preferences
        if "vegetarian" in dietary_preferences:
            selected_meal["name"] = f"Vegetarian {selected_meal['name']}"
            selected_meal["protein"] = max(15, selected_meal["protein"] - 10)
        
        if "vegan" in dietary_preferences:
            selected_meal["name"] = f"Vegan {selected_meal['name']}"
            selected_meal["protein"] = max(12, selected_meal["protein"] - 15)
        
        if "keto" in dietary_preferences:
            selected_meal["carbs"] = max(5, selected_meal["carbs"] - 20)
            selected_meal["fats"] = selected_meal["fats"] + 15
        
        # Adjust calories to target
        calorie_ratio = calorie_target / selected_meal["calories"]
        selected_meal["calories"] = int(selected_meal["calories"] * calorie_ratio)
        selected_meal["protein"] = int(selected_meal["protein"] * calorie_ratio)
        selected_meal["carbs"] = int(selected_meal["carbs"] * calorie_ratio)
        selected_meal["fats"] = int(selected_meal["fats"] * calorie_ratio)
        
        return {
            "meal_type": meal_type,
            "meal_name": selected_meal["name"],
            "calories": selected_meal["calories"],
            "protein": selected_meal["protein"],
            "carbs": selected_meal["carbs"],
            "fats": selected_meal["fats"],
            "dietary_tags": dietary_preferences,
            "allergy_safe": not any(allergy in selected_meal["name"].lower() for allergy in allergies)
        }
    
    def search_recipes(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search for recipes based on query and filters"""
        
        # Simple recipe database
        recipes = [
            {
                "id": "r1",
                "title": "Mediterranean Quinoa Bowl",
                "cuisine": "Mediterranean",
                "meal_type": "lunch",
                "calories": 420,
                "protein": 18,
                "carbs": 50,
                "fats": 15,
                "dietary_tags": ["vegetarian", "gluten-free"],
                "prep_time": 15,
                "cook_time": 20,
                "difficulty": "easy"
            },
            {
                "id": "r2",
                "title": "Grilled Chicken Breast",
                "cuisine": "American",
                "meal_type": "dinner",
                "calories": 250,
                "protein": 35,
                "carbs": 5,
                "fats": 12,
                "dietary_tags": ["high-protein", "gluten-free"],
                "prep_time": 10,
                "cook_time": 15,
                "difficulty": "easy"
            },
            {
                "id": "r3",
                "title": "Vegetarian Stir-Fry",
                "cuisine": "Asian",
                "meal_type": "dinner",
                "calories": 320,
                "protein": 15,
                "carbs": 40,
                "fats": 12,
                "dietary_tags": ["vegetarian", "vegan"],
                "prep_time": 15,
                "cook_time": 10,
                "difficulty": "easy"
            }
        ]
        
        # Filter recipes based on query and filters
        filtered_recipes = []
        for recipe in recipes:
            if query.lower() in recipe["title"].lower():
                if filters:
                    # Apply filters
                    if "dietary_tags" in filters:
                        if not any(tag in recipe["dietary_tags"] for tag in filters["dietary_tags"]):
                            continue
                    if "cuisine" in filters:
                        if recipe["cuisine"] not in filters["cuisine"]:
                            continue
                    if "max_calories" in filters:
                        if recipe["calories"] > filters["max_calories"]:
                            continue
                
                filtered_recipes.append(recipe)
        
        return filtered_recipes
    
    def analyze_nutrition(self, nutritional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze nutritional data and provide insights"""
        
        total_calories = nutritional_data.get("total_calories", 0)
        total_protein = nutritional_data.get("total_protein", 0)
        total_carbs = nutritional_data.get("total_carbs", 0)
        total_fats = nutritional_data.get("total_fats", 0)
        
        # Calculate percentages
        protein_calories = total_protein * 4
        carbs_calories = total_carbs * 4
        fats_calories = total_fats * 9
        
        total_calories_calc = protein_calories + carbs_calories + fats_calories
        
        if total_calories_calc > 0:
            protein_percent = (protein_calories / total_calories_calc) * 100
            carbs_percent = (carbs_calories / total_calories_calc) * 100
            fats_percent = (fats_calories / total_calories_calc) * 100
        else:
            protein_percent = carbs_percent = fats_percent = 0
        
        # Generate insights
        insights = []
        
        if protein_percent < 15:
            insights.append("Consider adding more protein to your meals")
        elif protein_percent > 35:
            insights.append("Your protein intake is quite high - consider balancing with more carbs")
        
        if carbs_percent < 45:
            insights.append("You might benefit from more carbohydrates for energy")
        elif carbs_percent > 65:
            insights.append("Consider reducing carbs and increasing protein or healthy fats")
        
        if fats_percent < 20:
            insights.append("Your fat intake is quite low - consider adding healthy fats")
        elif fats_percent > 40:
            insights.append("Consider reducing fat intake and increasing protein or carbs")
        
        return {
            "analysis": {
                "total_calories": total_calories,
                "macronutrient_breakdown": {
                    "protein": {"grams": total_protein, "percentage": round(protein_percent, 1)},
                    "carbs": {"grams": total_carbs, "percentage": round(carbs_percent, 1)},
                    "fats": {"grams": total_fats, "percentage": round(fats_percent, 1)}
                },
                "insights": insights,
                "recommendations": self._generate_recommendations(nutritional_data)
            }
        }
    
    def _generate_recommendations(self, nutritional_data: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations"""
        
        recommendations = []
        
        # Add general recommendations
        recommendations.append("Try to include a variety of colorful vegetables in your meals")
        recommendations.append("Consider meal prepping to maintain consistency")
        recommendations.append("Stay hydrated throughout the day")
        
        # Add specific recommendations based on data
        if nutritional_data.get("total_protein", 0) < 50:
            recommendations.append("Consider adding more lean protein sources like chicken, fish, or legumes")
        
        if nutritional_data.get("total_carbs", 0) < 100:
            recommendations.append("Include more whole grains and complex carbohydrates")
        
        return recommendations
