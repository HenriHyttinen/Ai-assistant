import openai
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from models.nutrition import Recipe, Ingredient, UserNutritionPreferences
from schemas.nutrition import NutritionalInfo, MealPlanRequest, RecipeSearchRequest
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class NutritionAI:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.max_tokens = 4000
        self.temperature = 0.7
        
    def generate_meal_plan_sequential(self, user_preferences: Dict[str, Any], plan_request: MealPlanRequest) -> Dict[str, Any]:
        """
        Sequential prompting for meal plan generation with 3+ steps
        """
        try:
            # Step 1: Analyze user profile and define strategy
            strategy_prompt = self._create_strategy_prompt(user_preferences, plan_request)
            strategy_response = self._call_openai(strategy_prompt, temperature=0.3)
            strategy = json.loads(strategy_response)
            
            # Step 2: Design meal structure based on strategy
            structure_prompt = self._create_structure_prompt(strategy, plan_request)
            structure_response = self._call_openai(structure_prompt, temperature=0.4)
            meal_structure = json.loads(structure_response)
            
            # Step 3: Generate specific recipes for each meal
            recipes_prompt = self._create_recipes_prompt(meal_structure, user_preferences)
            recipes_response = self._call_openai(recipes_prompt, temperature=0.6)
            meal_plan = json.loads(recipes_response)
            
            return {
                "strategy": strategy,
                "structure": meal_structure,
                "meal_plan": meal_plan,
                "generation_metadata": {
                    "model": "gpt-3.5-turbo",
                    "temperature": self.temperature,
                    "steps": 3,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in sequential meal plan generation: {str(e)}")
            return self._fallback_meal_plan(user_preferences, plan_request)
    
    def _create_strategy_prompt(self, preferences: Dict[str, Any], plan_request: MealPlanRequest) -> str:
        return f"""
        Analyze this user profile and recommend a meal strategy for {plan_request.plan_type} meal planning.
        
        User Profile:
        - Dietary Preferences: {preferences.get('dietary_preferences', [])}
        - Allergies: {preferences.get('allergies', [])}
        - Disliked Ingredients: {preferences.get('disliked_ingredients', [])}
        - Cuisine Preferences: {preferences.get('cuisine_preferences', [])}
        - Calorie Target: {preferences.get('daily_calorie_target', 2000)}
        - Protein Target: {preferences.get('protein_target', 100)}g
        - Meals per Day: {preferences.get('meals_per_day', 3)}
        
        Provide a JSON response with:
        {{
            "strategy_name": "string",
            "macro_distribution": {{"protein": 0.25, "carbs": 0.45, "fats": 0.30}},
            "meal_timing": {{"breakfast": "08:00", "lunch": "12:30", "dinner": "19:00"}},
            "focus_areas": ["high_protein", "fiber_rich", "anti_inflammatory"],
            "avoid_ingredients": ["specific_ingredients_to_avoid"],
            "preferred_cooking_methods": ["baking", "grilling", "steaming"]
        }}
        """
    
    def _create_structure_prompt(self, strategy: Dict[str, Any], plan_request: MealPlanRequest) -> str:
        return f"""
        Based on this meal strategy, create a {plan_request.plan_type} meal structure.
        
        Strategy: {json.dumps(strategy, indent=2)}
        Start Date: {plan_request.start_date}
        End Date: {plan_request.end_date}
        
        Provide a JSON response with:
        {{
            "meal_structure": [
                {{
                    "date": "YYYY-MM-DD",
                    "meals": [
                        {{
                            "meal_type": "breakfast/lunch/dinner/snack",
                            "meal_name": "descriptive_name",
                            "calorie_target": 500,
                            "macro_breakdown": {{"protein": 0.3, "carbs": 0.4, "fats": 0.3}},
                            "cuisine_style": "Mediterranean",
                            "cooking_time": 30,
                            "difficulty": "easy/medium/hard"
                        }}
                    ]
                }}
            ]
        }}
        """
    
    def _create_recipes_prompt(self, structure: Dict[str, Any], preferences: Dict[str, Any]) -> str:
        return f"""
        Generate specific recipes for this meal structure, considering user preferences.
        
        Meal Structure: {json.dumps(structure, indent=2)}
        User Preferences: {json.dumps(preferences, indent=2)}
        
        For each meal, provide:
        {{
            "meal_plan": [
                {{
                    "date": "YYYY-MM-DD",
                    "meals": [
                        {{
                            "meal_type": "breakfast/lunch/dinner/snack",
                            "meal_name": "specific_recipe_name",
                            "recipe": {{
                                "title": "Recipe Title",
                                "cuisine": "Cuisine Type",
                                "prep_time": 15,
                                "cook_time": 30,
                                "servings": 2,
                                "difficulty": "easy/medium/hard",
                                "ingredients": [
                                    {{"name": "ingredient_name", "quantity": 200, "unit": "g"}},
                                    {{"name": "olive_oil", "quantity": 15, "unit": "ml"}}
                                ],
                                "instructions": [
                                    {{"step": 1, "description": "detailed_step"}},
                                    {{"step": 2, "description": "detailed_step"}}
                                ],
                                "dietary_tags": ["vegetarian", "gluten-free"],
                                "nutrition": {{
                                    "calories": 450,
                                    "protein": 25.5,
                                    "carbs": 35.2,
                                    "fats": 18.8
                                }}
                            }}
                        }}
                    ]
                }}
            ]
        }}
        """
    
    def generate_recipe_with_rag(self, query: str, user_preferences: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        RAG-based recipe generation using vector similarity
        """
        try:
            # Get user's embedding for preferences
            user_embedding = self._get_user_embedding(user_preferences)
            
            # Retrieve similar recipes from database
            similar_recipes = self._retrieve_similar_recipes(query, user_embedding, db, limit=5)
            
            # Create augmented prompt with retrieved recipes
            rag_prompt = self._create_rag_prompt(query, similar_recipes, user_preferences)
            
            # Generate recipe using augmented context
            recipe_response = self._call_openai(rag_prompt, temperature=0.6)
            recipe = json.loads(recipe_response)
            
            # Calculate nutrition using function calling
            nutrition = self._calculate_recipe_nutrition(recipe.get('ingredients', []))
            recipe['nutrition'] = nutrition
            
            return recipe
            
        except Exception as e:
            logger.error(f"Error in RAG recipe generation: {str(e)}")
            return self._fallback_recipe_generation(query, user_preferences)
    
    def _get_user_embedding(self, preferences: Dict[str, Any]) -> np.ndarray:
        """Generate embedding for user preferences"""
        preference_text = f"""
        Dietary: {', '.join(preferences.get('dietary_preferences', []))}
        Cuisine: {', '.join(preferences.get('cuisine_preferences', []))}
        Allergies: {', '.join(preferences.get('allergies', []))}
        Disliked: {', '.join(preferences.get('disliked_ingredients', []))}
        """
        return self.embedding_model.encode([preference_text])[0]
    
    def _retrieve_similar_recipes(self, query: str, user_embedding: np.ndarray, db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve similar recipes using vector similarity"""
        try:
            # Get query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            
            # Retrieve recipes from database
            recipes = db.query(Recipe).filter(Recipe.is_active == True).limit(100).all()
            
            similarities = []
            for recipe in recipes:
                if recipe.embedding:
                    recipe_embedding = np.array(recipe.embedding)
                    # Calculate cosine similarity
                    similarity = np.dot(query_embedding, recipe_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(recipe_embedding)
                    )
                    similarities.append((recipe, similarity))
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x[1], reverse=True)
            return [self._recipe_to_dict(recipe) for recipe, _ in similarities[:limit]]
            
        except Exception as e:
            logger.error(f"Error retrieving similar recipes: {str(e)}")
            return []
    
    def _create_rag_prompt(self, query: str, similar_recipes: List[Dict[str, Any]], preferences: Dict[str, Any]) -> str:
        """Create augmented prompt with retrieved recipes"""
        recipe_examples = "\n".join([
            f"Recipe: {r.get('title', '')}\nCuisine: {r.get('cuisine', '')}\nIngredients: {', '.join([ing.get('name', '') for ing in r.get('ingredients', [])])}\n"
            for r in similar_recipes
        ])
        
        return f"""
        Generate a recipe based on this query: "{query}"
        
        User Preferences:
        - Dietary: {', '.join(preferences.get('dietary_preferences', []))}
        - Cuisine: {', '.join(preferences.get('cuisine_preferences', []))}
        - Allergies: {', '.join(preferences.get('allergies', []))}
        - Disliked: {', '.join(preferences.get('disliked_ingredients', []))}
        
        Similar recipes for inspiration:
        {recipe_examples}
        
        Generate a recipe that:
        1. Matches the user's dietary preferences and restrictions
        2. Is inspired by but different from the similar recipes
        3. Includes detailed ingredients with quantities in grams/ml
        4. Has step-by-step instructions
        5. Provides accurate nutritional information
        
        Return JSON format:
        {{
            "title": "Recipe Title",
            "cuisine": "Cuisine Type",
            "meal_type": "breakfast/lunch/dinner/snack",
            "prep_time": 15,
            "cook_time": 30,
            "servings": 2,
            "difficulty_level": "easy/medium/hard",
            "summary": "Brief description",
            "ingredients": [
                {{"name": "ingredient_name", "quantity": 200, "unit": "g"}},
                {{"name": "olive_oil", "quantity": 15, "unit": "ml"}}
            ],
            "instructions": [
                {{"step": 1, "description": "detailed_step"}},
                {{"step": 2, "description": "detailed_step"}}
            ],
            "dietary_tags": ["vegetarian", "gluten-free"],
            "nutrition": {{
                "calories": 450,
                "protein": 25.5,
                "carbs": 35.2,
                "fats": 18.8
            }}
        }}
        """
    
    def _calculate_recipe_nutrition(self, ingredients: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Function calling for nutritional calculations
        """
        try:
            # This would typically call a nutrition API or database
            # For now, using a simplified calculation
            total_calories = 0
            total_protein = 0
            total_carbs = 0
            total_fats = 0
            
            for ingredient in ingredients:
                # Simplified nutrition calculation
                # In a real implementation, this would query a nutrition database
                quantity = ingredient.get('quantity', 0)
                name = ingredient.get('name', '').lower()
                
                # Basic nutrition estimates (per 100g)
                if 'chicken' in name or 'beef' in name:
                    total_calories += quantity * 1.65  # 165 cal per 100g
                    total_protein += quantity * 0.25   # 25g protein per 100g
                    total_carbs += quantity * 0.01    # 1g carbs per 100g
                    total_fats += quantity * 0.08      # 8g fats per 100g
                elif 'rice' in name or 'pasta' in name:
                    total_calories += quantity * 1.3   # 130 cal per 100g
                    total_protein += quantity * 0.03  # 3g protein per 100g
                    total_carbs += quantity * 0.28    # 28g carbs per 100g
                    total_fats += quantity * 0.01     # 1g fats per 100g
                elif 'vegetable' in name or 'tomato' in name:
                    total_calories += quantity * 0.2  # 20 cal per 100g
                    total_protein += quantity * 0.01  # 1g protein per 100g
                    total_carbs += quantity * 0.04    # 4g carbs per 100g
                    total_fats += quantity * 0.001    # 0.1g fats per 100g
                else:
                    # Default estimates
                    total_calories += quantity * 0.5
                    total_protein += quantity * 0.05
                    total_carbs += quantity * 0.1
                    total_fats += quantity * 0.02
            
            return {
                "calories": round(total_calories, 1),
                "protein": round(total_protein, 1),
                "carbs": round(total_carbs, 1),
                "fats": round(total_fats, 1)
            }
            
        except Exception as e:
            logger.error(f"Error calculating recipe nutrition: {str(e)}")
            return {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}
    
    def _call_openai(self, prompt: str, temperature: float = 0.7) -> str:
        """Call OpenAI API with error handling"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"AI service temporarily unavailable: {str(e)}")
    
    def _recipe_to_dict(self, recipe) -> Dict[str, Any]:
        """Convert recipe model to dictionary"""
        return {
            "id": recipe.id,
            "title": recipe.title,
            "cuisine": recipe.cuisine,
            "meal_type": recipe.meal_type,
            "summary": recipe.summary,
            "dietary_tags": recipe.dietary_tags or [],
            "ingredients": [{"name": ing.ingredient.name, "quantity": ing.quantity, "unit": ing.unit} 
                          for ing in recipe.ingredients]
        }
    
    def _fallback_meal_plan(self, preferences: Dict[str, Any], plan_request: MealPlanRequest) -> Dict[str, Any]:
        """Fallback meal plan when AI fails"""
        return {
            "meal_plan": [{
                "date": str(plan_request.start_date),
                "meals": [{
                    "meal_type": "breakfast",
                    "meal_name": "Simple Oatmeal",
                    "recipe": {
                        "title": "Basic Oatmeal",
                        "ingredients": [{"name": "oats", "quantity": 50, "unit": "g"}],
                        "nutrition": {"calories": 200, "protein": 8, "carbs": 35, "fats": 4}
                    }
                }]
            }],
            "generation_metadata": {"fallback": True, "timestamp": datetime.utcnow().isoformat()}
        }
    
    def _fallback_recipe_generation(self, query: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback recipe when AI fails"""
        return {
            "title": f"Simple {query.title()}",
            "cuisine": "International",
            "ingredients": [{"name": "basic_ingredient", "quantity": 100, "unit": "g"}],
            "instructions": [{"step": 1, "description": "Prepare ingredients and cook"}],
            "nutrition": {"calories": 300, "protein": 15, "carbs": 25, "fats": 10}
        }
