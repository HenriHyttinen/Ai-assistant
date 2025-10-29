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
        
        print(f"Received calorie_target: {calorie_target}, meals_per_day: {meals_per_day}")
        
        # Generate meals
        meals = []
        meal_types = ["breakfast", "lunch", "dinner"]
        
        # Calculate calorie distribution (breakfast slightly smaller, dinner slightly larger)
        calorie_distribution = [0.3, 0.35, 0.35]  # breakfast, lunch, dinner
        if meals_per_day == 2:
            calorie_distribution = [0.4, 0.6]  # breakfast, dinner
        elif meals_per_day == 4:
            calorie_distribution = [0.25, 0.3, 0.3, 0.15]  # breakfast, lunch, dinner, snack
        
        for i, meal_type in enumerate(meal_types[:meals_per_day]):
            meal_calorie_target = int(calorie_target * calorie_distribution[i])
            meal = self._generate_meal(
                meal_type=meal_type,
                dietary_preferences=dietary_preferences,
                allergies=allergies,
                cuisine_preferences=cuisine_preferences,
                calorie_target=meal_calorie_target
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
                "calculated_calories": 420,
                "calculated_protein": 18,
                "calculated_carbs": 50,
                "calculated_fats": 15,
                "dietary_tags": ["vegetarian", "gluten-free"],
                "prep_time": 15,
                "cook_time": 20,
                "difficulty_level": "easy",
                "rating": 4.5,
                "ingredients": ["quinoa", "cherry tomatoes", "cucumber", "olives", "feta cheese", "olive oil"],
                "instructions": ["Cook quinoa according to package instructions", "Chop vegetables", "Mix all ingredients", "Drizzle with olive oil"]
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
                "calculated_calories": 250,
                "calculated_protein": 35,
                "calculated_carbs": 5,
                "calculated_fats": 12,
                "dietary_tags": ["high-protein", "gluten-free"],
                "prep_time": 10,
                "cook_time": 15,
                "difficulty_level": "easy",
                "rating": 4.2,
                "ingredients": ["chicken breast", "olive oil", "garlic", "herbs", "salt", "pepper"],
                "instructions": ["Season chicken breast", "Heat grill pan", "Cook for 6-7 minutes per side", "Let rest before serving"]
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
                "calculated_calories": 320,
                "calculated_protein": 15,
                "calculated_carbs": 40,
                "calculated_fats": 12,
                "dietary_tags": ["vegetarian", "vegan"],
                "prep_time": 15,
                "cook_time": 10,
                "difficulty_level": "easy",
                "rating": 4.0,
                "ingredients": ["mixed vegetables", "tofu", "soy sauce", "ginger", "garlic", "sesame oil"],
                "instructions": ["Cut vegetables into bite-sized pieces", "Heat oil in wok", "Stir-fry vegetables", "Add sauce and seasonings"]
            },
            {
                "id": "r4",
                "title": "Protein Smoothie Bowl",
                "cuisine": "International",
                "meal_type": "breakfast",
                "calories": 350,
                "protein": 25,
                "carbs": 30,
                "fats": 12,
                "calculated_calories": 350,
                "calculated_protein": 25,
                "calculated_carbs": 30,
                "calculated_fats": 12,
                "dietary_tags": ["high-protein", "vegetarian"],
                "prep_time": 5,
                "cook_time": 0,
                "difficulty_level": "easy",
                "rating": 4.3,
                "ingredients": ["protein powder", "banana", "berries", "almond milk", "granola", "honey"],
                "instructions": ["Blend protein powder with almond milk", "Add banana and berries", "Pour into bowl", "Top with granola and honey"]
            },
            {
                "id": "r5",
                "title": "Baked Salmon with Vegetables",
                "cuisine": "American",
                "meal_type": "dinner",
                "calories": 450,
                "protein": 40,
                "carbs": 25,
                "fats": 20,
                "calculated_calories": 450,
                "calculated_protein": 40,
                "calculated_carbs": 25,
                "calculated_fats": 20,
                "dietary_tags": ["high-protein", "gluten-free"],
                "prep_time": 15,
                "cook_time": 25,
                "difficulty_level": "medium",
                "rating": 4.7,
                "ingredients": ["salmon fillet", "broccoli", "carrots", "lemon", "dill", "olive oil"],
                "instructions": ["Preheat oven to 400°F", "Season salmon and vegetables", "Bake for 20-25 minutes", "Serve with lemon wedges"]
            },
            {
                "id": "r6",
                "title": "Greek Yogurt Parfait",
                "cuisine": "Mediterranean",
                "meal_type": "breakfast",
                "calories": 280,
                "protein": 20,
                "carbs": 35,
                "fats": 8,
                "calculated_calories": 280,
                "calculated_protein": 20,
                "calculated_carbs": 35,
                "calculated_fats": 8,
                "dietary_tags": ["vegetarian", "high-protein"],
                "prep_time": 5,
                "cook_time": 0,
                "difficulty_level": "easy",
                "rating": 4.1,
                "ingredients": ["greek yogurt", "granola", "berries", "honey", "nuts"],
                "instructions": ["Layer yogurt in glass", "Add granola and berries", "Drizzle with honey", "Top with nuts"]
            },
            {
                "id": "r7",
                "title": "Thai Curry with Rice",
                "cuisine": "Asian",
                "meal_type": "dinner",
                "calories": 520,
                "protein": 22,
                "carbs": 65,
                "fats": 18,
                "calculated_calories": 520,
                "calculated_protein": 22,
                "calculated_carbs": 65,
                "calculated_fats": 18,
                "dietary_tags": ["vegetarian", "gluten-free"],
                "prep_time": 20,
                "cook_time": 30,
                "difficulty_level": "medium",
                "rating": 4.4,
                "ingredients": ["coconut milk", "curry paste", "vegetables", "rice", "lime", "basil"],
                "instructions": ["Cook rice according to package", "Sauté vegetables", "Add curry paste and coconut milk", "Simmer until vegetables are tender"]
            },
            {
                "id": "r8",
                "title": "Avocado Toast",
                "cuisine": "International",
                "meal_type": "breakfast",
                "calories": 320,
                "protein": 12,
                "carbs": 35,
                "fats": 18,
                "calculated_calories": 320,
                "calculated_protein": 12,
                "calculated_carbs": 35,
                "calculated_fats": 18,
                "dietary_tags": ["vegetarian", "vegan"],
                "prep_time": 5,
                "cook_time": 5,
                "difficulty_level": "easy",
                "rating": 4.0,
                "ingredients": ["bread", "avocado", "lemon", "salt", "pepper", "red pepper flakes"],
                "instructions": ["Toast bread", "Mash avocado with lemon", "Season with salt and pepper", "Spread on toast and garnish"]
            },
            {
                "id": "r9",
                "title": "Beef Stir-Fry",
                "cuisine": "Asian",
                "meal_type": "dinner",
                "calories": 380,
                "protein": 35,
                "carbs": 25,
                "fats": 15,
                "calculated_calories": 380,
                "calculated_protein": 35,
                "calculated_carbs": 25,
                "calculated_fats": 15,
                "dietary_tags": ["high-protein", "gluten-free"],
                "prep_time": 15,
                "cook_time": 15,
                "difficulty_level": "medium",
                "rating": 4.2,
                "ingredients": ["beef strips", "bell peppers", "onions", "soy sauce", "ginger", "garlic"],
                "instructions": ["Slice beef and vegetables", "Heat oil in wok", "Cook beef first", "Add vegetables and sauce"]
            },
            {
                "id": "r10",
                "title": "Caesar Salad",
                "cuisine": "American",
                "meal_type": "lunch",
                "calories": 290,
                "protein": 15,
                "carbs": 20,
                "fats": 18,
                "calculated_calories": 290,
                "calculated_protein": 15,
                "calculated_carbs": 20,
                "calculated_fats": 18,
                "dietary_tags": ["vegetarian", "gluten-free"],
                "prep_time": 10,
                "cook_time": 0,
                "difficulty_level": "easy",
                "rating": 3.8,
                "ingredients": ["romaine lettuce", "parmesan cheese", "croutons", "caesar dressing", "lemon"],
                "instructions": ["Wash and chop lettuce", "Add parmesan and croutons", "Drizzle with dressing", "Toss and serve"]
            }
        ]
        
        # Filter recipes based on query and filters
        filtered_recipes = []
        for recipe in recipes:
            # Check query match (if query is provided)
            if query and query.lower() not in recipe["title"].lower():
                continue
                
            # Apply filters
            if filters:
                # Apply dietary tags filter
                if "dietary_tags" in filters and filters["dietary_tags"]:
                    if not any(tag in recipe["dietary_tags"] for tag in filters["dietary_tags"]):
                        continue
                
                # Apply cuisine filter
                if "cuisine" in filters and filters["cuisine"]:
                    if recipe["cuisine"].lower() != filters["cuisine"].lower():
                        continue
                
                # Apply meal type filter
                if "meal_type" in filters and filters["meal_type"]:
                    if recipe["meal_type"].lower() != filters["meal_type"].lower():
                        continue
                
                # Apply difficulty filter
                if "difficulty" in filters and filters["difficulty"]:
                    if recipe["difficulty_level"].lower() != filters["difficulty"].lower():
                        continue
                
                # Apply max calories filter
                if "max_calories" in filters and filters["max_calories"]:
                    if recipe["calories"] > filters["max_calories"]:
                        continue
                
                # Apply max prep time filter
                if "max_prep_time" in filters and filters["max_prep_time"]:
                    if recipe["prep_time"] > filters["max_prep_time"]:
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
