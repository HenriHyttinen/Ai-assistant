import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
import numpy as np
from sqlalchemy.orm import Session
from models.recipe import Recipe, Ingredient
from models.nutrition import UserNutritionPreferences
from schemas.nutrition import NutritionalInfo, MealPlanRequest, RecipeSearchRequest
from services.ai_recovery_service import execute_with_recovery
from .model_cache import model_cache

logger = logging.getLogger(__name__)

class NutritionAI:
    def __init__(self):
        # Use cached models instead of initializing new ones
        self.openai_client = model_cache.openai_client
        self.embedding_model = model_cache.embedding_model
        self.max_tokens = 3000
        
        self.parameters = {
            "strategy_generation": {"temperature": 0.3, "top_p": 0.9},  # More focused for strategy
            "meal_planning": {"temperature": 0.4, "top_p": 0.8},        # Balanced creativity
            "recipe_generation": {"temperature": 0.6, "top_p": 0.7},    # More creative for recipes
            "nutritional_analysis": {"temperature": 0.5, "top_p": 0.8}, # Balanced for analysis
            "insights": {"temperature": 0.6, "top_p": 0.7}              # Creative insights
        }
        
    def generate_meal_plan_sequential(self, user_preferences: Dict[str, Any], plan_request: MealPlanRequest, db: Session = None) -> Dict[str, Any]:
        """
        Sequential prompting for meal plan generation with 3+ steps and recovery mechanisms
        Enhanced with RAG (Retrieval-Augmented Generation) for better recipe suggestions
        """
        if not self.openai_client:
            logger.warning("OpenAI not available, using fallback meal plan generation")
            return self._fallback_meal_plan(user_preferences, plan_request)
        
        # Handle weekly plans differently
        if plan_request.plan_type == "weekly":
            return self._generate_weekly_meal_plan(user_preferences, plan_request)
        
        try:
            # Step 1: Analyze user profile and define strategy
            strategy_prompt = self._create_strategy_prompt(user_preferences, plan_request)
            # Use slightly higher temperature for more variety
            strategy_temp = min(0.8, self.parameters["strategy_generation"]["temperature"] + 0.1)
            strategy_response = self._call_openai(strategy_prompt, strategy_temp)
            strategy = self._parse_json_response(strategy_response, "strategy")
            
            # Step 2: Design meal structure based on strategy
            structure_prompt = self._create_structure_prompt(strategy, plan_request)
            structure_temp = min(0.8, self.parameters["meal_planning"]["temperature"] + 0.1)
            structure_response = self._call_openai(structure_prompt, structure_temp)
            meal_structure = self._parse_json_response(structure_response, "structure")
            
            # Step 3: Generate specific recipes for each meal (with RAG enhancement)
            if db:
                # Retrieve relevant recipes from database using RAG
                retrieved_recipes = self._retrieve_relevant_recipes_for_meal_plan(meal_structure, user_preferences, db)
                recipes_prompt = self._create_rag_enhanced_recipes_prompt(meal_structure, user_preferences, retrieved_recipes)
            else:
                recipes_prompt = self._create_recipes_prompt(meal_structure, user_preferences)
            
            recipes_temp = min(0.9, self.parameters["recipe_generation"]["temperature"] + 0.2)
            recipes_response = self._call_openai(recipes_prompt, recipes_temp)
            meal_plan = self._parse_json_response(recipes_response, "meal_plan")
            
            # Add snacks if calorie target isn't met
            meal_plan = self._add_snacks_if_needed(meal_plan, user_preferences)
            
            return {
                "strategy": strategy,
                "structure": meal_structure,
                "meal_plan": meal_plan,
                "generation_metadata": {
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.7,
                    "steps": 3,
                    "timestamp": datetime.utcnow().isoformat(),
                    "recovery_used": False
                }
            }
            
        except Exception as e:
            logger.error(f"Error in sequential meal plan generation: {str(e)}")
            return self._fallback_meal_plan(user_preferences, plan_request)
    
    async def generate_meal_plan_sequential_with_recovery(self, user_preferences: Dict[str, Any], plan_request: MealPlanRequest) -> Dict[str, Any]:
        """
        Sequential prompting for meal plan generation with comprehensive recovery mechanisms
        """
        request_data = {
            "user_preferences": user_preferences,
            "plan_request": plan_request.__dict__ if hasattr(plan_request, '__dict__') else str(plan_request)
        }
        
        try:
            return await execute_with_recovery(
                self.generate_meal_plan_sequential,
                "meal_plan_generation",
                request_data,
                cache_ttl=1800,  # Cache for 30 minutes
                user_preferences=user_preferences,
                plan_request=plan_request
            )
        except Exception as e:
            logger.error(f"All recovery mechanisms failed for meal plan generation: {str(e)}")
            # Final fallback
            return self._fallback_meal_plan(user_preferences, plan_request)
    
    def _generate_weekly_meal_plan(self, user_preferences: Dict[str, Any], plan_request: MealPlanRequest) -> Dict[str, Any]:
        """Generate a complete weekly meal plan with variety across days"""
        try:
            # Step 1: Create weekly strategy
            weekly_strategy_prompt = self._create_weekly_strategy_prompt(user_preferences, plan_request)
            strategy_response = self._call_openai(weekly_strategy_prompt, self.parameters["strategy_generation"]["temperature"])
            weekly_strategy = self._parse_json_response(strategy_response, "weekly_strategy")
            
            # Step 2: Generate meal structure for the week
            weekly_structure_prompt = self._create_weekly_structure_prompt(weekly_strategy, user_preferences)
            structure_response = self._call_openai(weekly_structure_prompt, self.parameters["meal_planning"]["temperature"])
            weekly_structure = self._parse_json_response(structure_response, "weekly_structure")
            
            # Step 3: Generate specific recipes for each day
            weekly_recipes_prompt = self._create_weekly_recipes_prompt(weekly_structure, user_preferences)
            recipes_response = self._call_openai(weekly_recipes_prompt, self.parameters["recipe_generation"]["temperature"])
            weekly_meal_plan = self._parse_json_response(recipes_response, "weekly_meal_plan")
            
            # Add snacks to each day if needed
            if "weekly_plan" in weekly_meal_plan:
                for i, day_plan in enumerate(weekly_meal_plan["weekly_plan"]):
                    weekly_meal_plan["weekly_plan"][i] = self._add_snacks_if_needed(day_plan, user_preferences)
            
            return {
                "weekly_strategy": weekly_strategy,
                "weekly_structure": weekly_structure,
                "weekly_meal_plan": weekly_meal_plan,
                "generation_metadata": {
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.7,
                    "steps": 3,
                    "plan_type": "weekly",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in weekly meal plan generation: {str(e)}")
            return self._fallback_weekly_meal_plan(user_preferences, plan_request)
    
    def _format_personalization_context(self, context: Dict[str, Any]) -> str:
        """Format personalization context for AI prompts"""
        if not context:
            return "- No personalization data available"
        
        lines = []
        if context.get('bmi'):
            bmi = context['bmi']
            if bmi < 18.5:
                bmi_status = "underweight"
            elif bmi < 25:
                bmi_status = "normal weight"
            elif bmi < 30:
                bmi_status = "overweight"
            else:
                bmi_status = "obese"
            lines.append(f"- BMI: {bmi} ({bmi_status})")
        
        if context.get('activity_level'):
            activity = context['activity_level'].replace('_', ' ').title()
            lines.append(f"- Activity Level: {activity}")
        
        if context.get('fitness_goal'):
            goal = context['fitness_goal'].replace('_', ' ').title()
            lines.append(f"- Fitness Goal: {goal}")
        
        if context.get('wellness_score'):
            score = context['wellness_score']
            if score >= 80:
                wellness_status = "excellent"
            elif score >= 60:
                wellness_status = "good"
            else:
                wellness_status = "needs improvement"
            lines.append(f"- Wellness Score: {score}/100 ({wellness_status})")
        
        if context.get('is_personalized'):
            lines.append("- Targets are personalized based on health profile")
        else:
            lines.append("- Using default targets (health profile not available)")
        
        return '\n'.join(lines) if lines else "- No personalization data available"
    
    def _get_personalization_recommendations(self, context: Dict[str, Any]) -> str:
        """Get personalized recommendations based on user context"""
        if not context:
            return "- Use general healthy eating principles"
        
        recommendations = []
        
        # BMI-based recommendations
        if context.get('bmi'):
            bmi = context['bmi']
            if bmi < 18.5:
                recommendations.append("- Focus on nutrient-dense, calorie-rich foods for healthy weight gain")
            elif bmi > 30:
                recommendations.append("- Emphasize portion control and high-fiber, low-calorie foods")
            elif bmi > 25:
                recommendations.append("- Include more vegetables and lean proteins, moderate portions")
        
        # Activity level recommendations
        if context.get('activity_level'):
            activity = context['activity_level'].lower()
            if activity in ['very_active', 'extremely_active']:
                recommendations.append("- Include more complex carbohydrates for sustained energy")
                recommendations.append("- Add post-workout recovery foods with protein and carbs")
            elif activity in ['sedentary', 'lightly_active']:
                recommendations.append("- Focus on nutrient density over calorie density")
                recommendations.append("- Include metabolism-boosting foods like green tea, spices")
        
        # Fitness goal recommendations
        if context.get('fitness_goal'):
            goal = context['fitness_goal'].lower()
            if 'weight_loss' in goal:
                recommendations.append("- Prioritize high-protein, high-fiber meals for satiety")
                recommendations.append("- Include metabolism-boosting ingredients like chili, ginger")
            elif 'muscle' in goal or 'strength' in goal:
                recommendations.append("- Emphasize complete proteins and amino acid-rich foods")
                recommendations.append("- Include anti-inflammatory foods for recovery")
            elif 'endurance' in goal:
                recommendations.append("- Focus on complex carbohydrates for sustained energy")
                recommendations.append("- Include electrolyte-rich foods")
        
        # Wellness score recommendations
        if context.get('wellness_score'):
            score = context['wellness_score']
            if score < 60:
                recommendations.append("- Include more whole, unprocessed foods")
                recommendations.append("- Focus on immune-boosting nutrients (vitamin C, zinc)")
            elif score >= 80:
                recommendations.append("- Maintain current healthy eating patterns")
                recommendations.append("- Consider advanced nutrition strategies like meal timing")
        
        return '\n'.join(recommendations) if recommendations else "- Use general healthy eating principles"
    
    def _create_strategy_prompt(self, preferences: Dict[str, Any], plan_request: MealPlanRequest) -> str:
        """Create strategy prompt with few-shot examples"""
        return f"""
        You are an expert nutritionist and meal planning specialist. Analyze this user profile and recommend a personalized meal strategy.

        FEW-SHOT EXAMPLES:

        Example 1 - Vegetarian High-Protein:
        User: {{"dietary_preferences": ["vegetarian", "high-protein"], "calorie_target": 2200, "protein_target": 120}}
        Response: {{
            "strategy_name": "Plant-Powered Protein Strategy",
            "macro_distribution": {{"protein": 0.30, "carbs": 0.45, "fats": 0.25}},
            "meal_timing": {{"breakfast": "08:00", "lunch": "12:30", "dinner": "19:00"}},
            "focus_areas": ["legume_protein", "quinoa_meals", "nut_butters", "greek_yogurt"],
            "avoid_ingredients": ["meat", "fish", "poultry"],
            "preferred_cooking_methods": ["roasting", "steaming", "blending"]
        }}

        Example 2 - Keto Weight Loss:
        User: {{"dietary_preferences": ["keto", "low-carb"], "calorie_target": 1600, "protein_target": 100}}
        Response: {{
            "strategy_name": "Keto Fat-Burning Strategy",
            "macro_distribution": {{"protein": 0.25, "carbs": 0.05, "fats": 0.70}},
            "meal_timing": {{"breakfast": "09:00", "lunch": "13:00", "dinner": "18:00"}},
            "focus_areas": ["healthy_fats", "leafy_greens", "avocado", "olive_oil"],
            "avoid_ingredients": ["grains", "sugar", "starchy_vegetables"],
            "preferred_cooking_methods": ["sautéing", "baking", "grilling"]
        }}

        CURRENT USER PROFILE:
        - Dietary Preferences: {preferences.get('dietary_preferences', [])}
        - Allergies: {preferences.get('allergies', [])}
        - Disliked Ingredients: {preferences.get('disliked_ingredients', [])}
        - Cuisine Preferences: {preferences.get('cuisine_preferences', [])}
        - Calorie Target: {preferences.get('daily_calorie_target', 2000)}
        - Protein Target: {preferences.get('protein_target', 100)}g
        - Meals per Day: {preferences.get('meals_per_day', 3)}
        
        PERSONALIZATION CONTEXT:
        {self._format_personalization_context(preferences.get('personalization_context', {}))}
        
        CALORIE TARGET REQUIREMENT: The total daily calories MUST be close to {preferences.get('daily_calorie_target', 2000)} calories (±100). This is CRITICAL.
        
        DIETARY RESTRICTIONS: STRICTLY follow these preferences: {preferences.get('dietary_preferences', [])}
        - If vegetarian: NO meat, fish, or poultry
        - If vegan: NO animal products at all
        - If keto: LOW carbs, HIGH fats
        - If gluten-free: NO wheat, barley, rye
        
        ALLERGIES: NEVER include these ingredients: {preferences.get('allergies', [])}
        
        VARIETY REQUEST: Please create a unique and varied meal strategy. Consider different cooking methods, international cuisines, and seasonal ingredients to ensure variety.
        
        CUISINE DIVERSITY REQUIREMENT: Ensure each meal uses a different cuisine:
        - Breakfast: Mediterranean, American, or Asian
        - Lunch: Thai, Mexican, or Middle Eastern  
        - Dinner: Italian, Indian, or French
        - NO two meals should use the same cuisine
        
        PERSONALIZATION-BASED RECOMMENDATIONS:
        {self._get_personalization_recommendations(preferences.get('personalization_context', {}))}
        
        IMPORTANT: Respond with ONLY valid JSON. No explanations, no markdown, no extra text.
        Provide a JSON response following this exact format:
        {{
            "strategy_name": "string",
            "macro_distribution": {{"protein": 0.25, "carbs": 0.45, "fats": 0.30}},
            "meal_timing": {{"breakfast": "08:00", "lunch": "12:30", "dinner": "19:00"}},
            "focus_areas": ["specific_focus_areas"],
            "avoid_ingredients": ["specific_ingredients_to_avoid"],
            "preferred_cooking_methods": ["cooking_methods"]
        }}
        """
    
    def _create_structure_prompt(self, strategy: Dict[str, Any], plan_request: MealPlanRequest) -> str:
        return f"""
        Based on this meal strategy, create a {plan_request.plan_type} meal structure.
        
        Strategy: {json.dumps(strategy, indent=2)}
        Start Date: {plan_request.start_date}
        End Date: {plan_request.end_date}
        
        IMPORTANT: Respond with ONLY valid JSON. No explanations, no markdown, no extra text.
        Provide a JSON response with this exact format:
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
        Generate DELICIOUS, DETAILED, and APPEALING recipes for this meal structure. Create restaurant-quality recipes that people would actually want to cook and eat.
        
        Meal Structure: {json.dumps(structure, indent=2)}
        User Preferences: {json.dumps(preferences, indent=2)}
        
        CUISINE ASSIGNMENT REQUIREMENT: Each meal must use a DIFFERENT cuisine:
        - Breakfast: Use Mediterranean, American, or Asian cuisine
        - Lunch: Use Thai, Mexican, or Middle Eastern cuisine  
        - Dinner: Use Italian, Indian, or French cuisine
        - CRITICAL: NO two meals can use the same cuisine!
        
        CUISINE EXAMPLES:
        - Mediterranean: Greek, Italian, Spanish, Turkish flavors
        - Asian: Chinese, Japanese, Korean, Vietnamese flavors
        - Thai: Coconut milk, curry paste, lemongrass, fish sauce
        - Mexican: Cumin, chili, lime, cilantro, beans, corn
        - Middle Eastern: Sumac, tahini, pomegranate, za'atar
        - Italian: Basil, oregano, tomatoes, parmesan, olive oil
        - Indian: Turmeric, garam masala, ginger, coriander
        - French: Herbs de Provence, butter, wine, shallots
        
        CRITICAL REQUIREMENTS:
        - CALORIE TARGET: Total calories MUST be close to {preferences.get('daily_calorie_target', 2000)} calories (±100)
        - CALORIE DISTRIBUTION: Breakfast ~25%, Lunch ~30%, Dinner ~30%, Snacks ~15% of total calories
        - PORTION SIZES: Use larger portions to hit calorie targets (e.g., 200g protein, 150g carbs per meal)
        - SNACKS: If main meals don't reach calorie target, add 1-2 healthy snacks to fill the gap
        - DIETARY RESTRICTIONS: STRICTLY follow these: {preferences.get('dietary_preferences', [])}
        - ALLERGIES: NEVER include these ingredients: {preferences.get('allergies', [])}
        - DISLIKED INGREDIENTS: Avoid these: {preferences.get('disliked_ingredients', [])}
        - CUISINE PREFERENCES: Use these cuisines: {preferences.get('cuisine_preferences', [])}
        
        RECIPE QUALITY REQUIREMENTS:
        - Create sophisticated, flavorful recipes with proper cooking techniques
        - Use fresh herbs, spices, and seasonings for depth of flavor
        - Include proper cooking methods (sautéing, roasting, braising, etc.)
        - Make recipes that look and taste professional
        - Include proper ingredient preparation (chopping, marinating, etc.)
        - Add finishing touches like garnishes, sauces, or dressings
        
        VARIETY REQUIREMENT: Create unique, diverse recipes with different cuisines, cooking methods, and ingredients. Avoid repeating the same dishes.
        
        IMPORTANT: Respond with ONLY valid JSON. No explanations, no markdown, no extra text.
        For each meal, provide this exact JSON format:
        {{
            "meal_plan": [
                {{
                    "date": "YYYY-MM-DD",
                    "meals": [
                        {{
                            "meal_type": "breakfast/lunch/dinner/snack",
                            "meal_name": "appealing_recipe_name",
                            "recipe": {{
                                "title": "Professional Recipe Title",
                                "cuisine": "Cuisine Type",
                                "prep_time": 15,
                                "cook_time": 30,
                                "servings": 2,
                                "difficulty": "easy/medium/hard",
                                "ingredients": [
                                    {{"name": "main_ingredient", "quantity": 200, "unit": "g"}},
                                    {{"name": "seasoning_herb", "quantity": 5, "unit": "g"}},
                                    {{"name": "cooking_oil", "quantity": 15, "unit": "ml"}},
                                    {{"name": "garnish", "quantity": 10, "unit": "g"}}
                                ],
                                "instructions": [
                                    {{"step": 1, "description": "detailed_cooking_step_with_technique"}},
                                    {{"step": 2, "description": "seasoning_and_finishing_step"}},
                                    {{"step": 3, "description": "plating_and_garnish_step"}}
                                ],
                                "dietary_tags": ["vegetarian/vegan/gluten-free"],
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
        
        CRITICAL: Create recipes that sound delicious and professional. Use proper cooking terminology and techniques.
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
            recipe_response = self._call_openai(rag_prompt, self.parameters["recipe_generation"]["temperature"])
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
        if self.embedding_model is None:
            # Return a dummy embedding if sentence transformers is not available
            return np.zeros(384)  # Default embedding size for all-MiniLM-L6-v2
        return self.embedding_model.encode([preference_text])[0]
    
    def _retrieve_similar_recipes(self, query: str, user_embedding: np.ndarray, db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve similar recipes using vector similarity"""
        try:
            # Get query embedding
            if self.embedding_model is None:
                # Return empty list if sentence transformers is not available
                return []
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
        
        CRITICAL DIETARY REQUIREMENTS:
        - DIETARY RESTRICTIONS: STRICTLY follow these: {', '.join(preferences.get('dietary_preferences', []))}
          * If vegetarian: NO meat, fish, or poultry
          * If vegan: NO animal products at all
          * If keto: LOW carbs, HIGH fats
          * If gluten-free: NO wheat, barley, rye
        - ALLERGIES: NEVER include these ingredients: {', '.join(preferences.get('allergies', []))}
        - DISLIKED INGREDIENTS: Avoid these: {', '.join(preferences.get('disliked_ingredients', []))}
        - CUISINE PREFERENCES: Use these cuisines: {', '.join(preferences.get('cuisine_preferences', []))}
        
        Similar recipes for inspiration:
        {recipe_examples}
        
        Generate a recipe that:
        1. STRICTLY follows all dietary restrictions and allergies
        2. Is inspired by but different from the similar recipes
        3. Includes detailed ingredients with quantities in grams/ml
        4. Has step-by-step instructions
        5. Provides accurate nutritional information
        6. Uses appropriate cuisine style and flavors
        
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
    
    def generate_nutritional_insights(self, nutritional_data: Dict[str, Any], user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered nutritional insights and recommendations"""
        try:
            prompt = f"""
            You are an expert nutritionist. Analyze this user's nutritional data and provide personalized insights.
            
            User's Nutritional Data:
            - Daily Calories: {nutritional_data.get('calories', 0)} (Target: {user_preferences.get('daily_calorie_target', 2000)})
            - Protein: {nutritional_data.get('protein', 0)}g (Target: {user_preferences.get('protein_target', 100)}g)
            - Carbs: {nutritional_data.get('carbs', 0)}g (Target: {user_preferences.get('carbs_target', 200)}g)
            - Fats: {nutritional_data.get('fats', 0)}g (Target: {user_preferences.get('fats_target', 60)}g)
            
            User Preferences:
            - Dietary: {user_preferences.get('dietary_preferences', [])}
            - Allergies: {user_preferences.get('allergies', [])}
            
            Provide a JSON response with:
            {{
                "achievements": ["specific_positive_achievements"],
                "concerns": ["areas_that_need_attention"],
                "suggestions": ["actionable_recommendations"],
                "meal_timing_advice": ["timing_optimization_tips"],
                "ingredient_recommendations": ["specific_foods_to_add"],
                "portion_advice": ["portion_size_recommendations"]
            }}
            """
            
            response = self._call_openai(prompt, self.parameters["insights"]["temperature"])
            return self._parse_json_response(response, "insights")
            
        except Exception as e:
            logger.error(f"Error generating nutritional insights: {str(e)}")
            return {
                "achievements": ["Keep up the good work!"],
                "concerns": ["Continue tracking your nutrition"],
                "suggestions": ["Stay consistent with your meal planning"],
                "meal_timing_advice": ["Maintain regular meal times"],
                "ingredient_recommendations": ["Include more variety in your meals"],
                "portion_advice": ["Monitor portion sizes"]
            }
    
    async def generate_nutritional_insights_with_recovery(self, nutritional_data: Dict[str, Any], user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered nutritional insights with comprehensive recovery mechanisms
        """
        request_data = {
            "nutritional_data": nutritional_data,
            "user_preferences": user_preferences
        }
        
        try:
            return await execute_with_recovery(
                self.generate_nutritional_insights,
                "nutritional_insights",
                request_data,
                cache_ttl=900,  # Cache for 15 minutes
                nutritional_data=nutritional_data,
                user_preferences=user_preferences
            )
        except Exception as e:
            logger.error(f"All recovery mechanisms failed for nutritional insights: {str(e)}")
            # Final fallback
            return {
                "achievements": ["Keep up the good work!"],
                "concerns": ["Continue tracking your nutrition"],
                "suggestions": ["Stay consistent with your meal planning"],
                "meal_timing_advice": ["Maintain regular meal times"],
                "ingredient_recommendations": ["Include more variety in your meals"],
                "portion_advice": ["Monitor portion sizes"],
                "is_fallback": True
            }
    
    def _calculate_recipe_nutrition(self, ingredients: List[Dict[str, Any]]) -> Dict[str, float]:
        """Call the function-calling registry to compute nutrition totals per serving (servings=1)."""
        try:
            from .functions import registry
            args = {"ingredients": ingredients, "servings": 1}
            result = registry.execute("calculate_nutrition", args)
            if isinstance(result, dict) and "error" not in result:
                per = result.get("per_serving") or {}
                return {
                    "calories": float(per.get("calories", 0) or 0),
                    "protein": float(per.get("protein", 0) or 0),
                    "carbs": float(per.get("carbs", 0) or 0),
                    "fats": float(per.get("fats", 0) or 0),
                }
            logger.warning(f"calculate_nutrition returned error: {result}")
            return {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}
        except Exception as e:
            logger.error(f"Error calculating recipe nutrition: {str(e)}")
            return {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}
    
    def _call_openai(self, prompt: str, temperature: float = 0.7) -> str:
        """Call OpenAI API with comprehensive error handling and recovery"""
        if not self.openai_client:
            raise Exception("OpenAI client not available. Please check your API key and settings.")
        
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
    
    async def _call_openai_with_recovery(self, prompt: str, temperature: float = 0.7) -> str:
        """Call OpenAI API with comprehensive recovery mechanisms"""
        request_data = {
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": self.max_tokens
        }
        
        return await execute_with_recovery(
            self._call_openai,
            "openai_api",
            request_data,
            cache_ttl=600,  # Cache for 10 minutes
            prompt=prompt,
            temperature=temperature
        )
    
    def _parse_json_response(self, response: str, response_type: str) -> Dict[str, Any]:
        """Parse JSON response with error handling and cleanup"""
        try:
            # Try to parse as-is first
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            import re
            
            # Look for JSON blocks in the response
            json_pattern = r'```json\s*(\{.*?\})\s*```'
            json_match = re.search(json_pattern, response, re.DOTALL)
            
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # Look for any JSON object in the response
            json_pattern = r'(\{.*\})'
            json_match = re.search(json_pattern, response, re.DOTALL)
            
            if json_match:
                json_text = json_match.group(1)
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    # Try to fix common JSON issues
                    # Remove trailing commas
                    fixed_json = re.sub(r',\s*}', '}', json_text)
                    fixed_json = re.sub(r',\s*]', ']', fixed_json)
                    try:
                        return json.loads(fixed_json)
                    except json.JSONDecodeError:
                        pass
            
            # Try to fix truncated JSON by adding missing closing braces
            if response.count('{') > response.count('}'):
                # Add missing closing braces
                missing_braces = response.count('{') - response.count('}')
                fixed_response = response + '}' * missing_braces
                try:
                    return json.loads(fixed_response)
                except json.JSONDecodeError:
                    pass
            
            # If all else fails, log the response and raise an error
            logger.error(f"Failed to parse {response_type} JSON response: {response[:500]}...")
            raise Exception(f"Invalid JSON response from AI for {response_type}")
    
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
        """Fallback meal plan when AI fails - with better recipes"""
        return {
            "meal_plan": {
                "meals": [
                    {
                        "meal_type": "breakfast",
                        "meal_name": "Mediterranean Avocado Toast",
                        "recipe": {
                            "title": "Mediterranean Avocado Toast",
                            "cuisine": "Mediterranean",
                            "prep_time": 10,
                            "cook_time": 5,
                            "servings": 1,
                            "difficulty": "easy",
                            "ingredients": [
                                {"name": "whole grain bread", "quantity": 2, "unit": "slices"},
                                {"name": "ripe avocado", "quantity": 1, "unit": "medium"},
                                {"name": "cherry tomatoes", "quantity": 100, "unit": "g"},
                                {"name": "feta cheese", "quantity": 30, "unit": "g"},
                                {"name": "olive oil", "quantity": 10, "unit": "ml"},
                                {"name": "fresh basil", "quantity": 5, "unit": "g"}
                            ],
                            "instructions": [
                                {"step": 1, "description": "Toast the bread slices until golden and crispy"},
                                {"step": 2, "description": "Mash the avocado with a pinch of salt and lemon juice"},
                                {"step": 3, "description": "Spread avocado on toast, top with halved tomatoes, crumbled feta, and fresh basil. Drizzle with olive oil"}
                            ],
                            "dietary_tags": ["vegetarian"],
                            "nutrition": {
                                "calories": 600,
                                "protein": 18,
                                "carbs": 50,
                                "fats": 35
                            }
                        }
                    },
                    {
                        "meal_type": "lunch",
                        "meal_name": "Thai Coconut Curry Bowl",
                        "recipe": {
                            "title": "Thai Coconut Curry Bowl",
                            "cuisine": "Thai",
                            "prep_time": 15,
                            "cook_time": 20,
                            "servings": 1,
                            "difficulty": "medium",
                            "ingredients": [
                                {"name": "coconut milk", "quantity": 200, "unit": "ml"},
                                {"name": "red curry paste", "quantity": 15, "unit": "g"},
                                {"name": "chicken breast", "quantity": 150, "unit": "g"},
                                {"name": "bell peppers", "quantity": 100, "unit": "g"},
                                {"name": "bamboo shoots", "quantity": 50, "unit": "g"},
                                {"name": "fresh cilantro", "quantity": 10, "unit": "g"}
                            ],
                            "instructions": [
                                {"step": 1, "description": "Sauté chicken breast until golden, then add curry paste and cook until fragrant"},
                                {"step": 2, "description": "Add coconut milk, bell peppers, and bamboo shoots. Simmer for 15 minutes"},
                                {"step": 3, "description": "Garnish with fresh cilantro and serve over jasmine rice"}
                            ],
                            "dietary_tags": ["gluten-free"],
                            "nutrition": {
                                "calories": 700,
                                "protein": 45,
                                "carbs": 35,
                                "fats": 35
                            }
                        }
                    },
                    {
                        "meal_type": "dinner",
                        "meal_name": "Herb-Crusted Salmon",
                        "recipe": {
                            "title": "Herb-Crusted Salmon with Roasted Vegetables",
                            "cuisine": "Mediterranean",
                            "prep_time": 15,
                            "cook_time": 25,
                            "servings": 1,
                            "difficulty": "medium",
                            "ingredients": [
                                {"name": "salmon fillet", "quantity": 180, "unit": "g"},
                                {"name": "mixed herbs", "quantity": 10, "unit": "g"},
                                {"name": "asparagus", "quantity": 150, "unit": "g"},
                                {"name": "sweet potato", "quantity": 200, "unit": "g"},
                                {"name": "olive oil", "quantity": 15, "unit": "ml"},
                                {"name": "lemon", "quantity": 0.5, "unit": "medium"}
                            ],
                            "instructions": [
                                {"step": 1, "description": "Preheat oven to 200°C. Season salmon with herbs, salt, and pepper"},
                                {"step": 2, "description": "Roast sweet potato and asparagus with olive oil for 20 minutes"},
                                {"step": 3, "description": "Add salmon to the pan and roast for 12-15 minutes until flaky. Serve with lemon wedges"}
                            ],
                            "dietary_tags": ["gluten-free", "dairy-free"],
                            "nutrition": {
                                "calories": 700,
                                "protein": 50,
                                "carbs": 40,
                                "fats": 30
                            }
                        }
                    }
                ]
            },
            "generation_metadata": {"fallback": True, "timestamp": datetime.utcnow().isoformat()}
        }
    
    def _fallback_weekly_meal_plan(self, user_preferences: Dict[str, Any], plan_request: MealPlanRequest) -> Dict[str, Any]:
        """Fallback weekly meal plan when AI is not available"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekly_plan = []
        
        for day in days:
            daily_plan = self._fallback_meal_plan(user_preferences, plan_request)
            daily_plan["day"] = day
            weekly_plan.append(daily_plan)
        
        return {
            "weekly_meal_plan": {
                "weekly_plan": weekly_plan
            }
        }
    
    def _create_weekly_strategy_prompt(self, preferences: Dict[str, Any], plan_request: MealPlanRequest) -> str:
        """Create weekly strategy prompt"""
        return f"""
        You are an expert nutritionist creating a weekly meal strategy. Analyze this user profile and create a comprehensive 7-day nutrition strategy.

        USER PROFILE:
        - Dietary Preferences: {preferences.get('dietary_preferences', [])}
        - Allergies: {preferences.get('allergies', [])}
        - Disliked Ingredients: {preferences.get('disliked_ingredients', [])}
        - Cuisine Preferences: {preferences.get('cuisine_preferences', [])}
        - Daily Calorie Target: {preferences.get('daily_calorie_target', 2000)} kcal
        - Protein Target: {preferences.get('protein_target', 100)}g
        - Meals per Day: {preferences.get('meals_per_day', 3)}

        PLAN DETAILS:
        - Plan Type: {plan_request.plan_type}
        - Start Date: {plan_request.start_date}
        - End Date: {plan_request.end_date}

        Create a weekly strategy that includes:
        1. Weekly nutrition goals and distribution
        2. Cuisine variety across days
        3. Meal complexity variation (easy/medium/hard)
        4. Special considerations for different days
        5. Shopping and prep strategy

        Respond with a JSON object containing:
        {{
            "weekly_strategy": {{
                "nutrition_goals": {{"weekly_calories": number, "weekly_protein": number, "variety_focus": "string"}},
                "cuisine_rotation": ["day1_cuisine", "day2_cuisine", ...],
                "complexity_schedule": {{"monday": "easy", "tuesday": "medium", ...}},
                "special_days": {{"weekend": "special_considerations"}},
                "prep_strategy": "string with meal prep recommendations"
            }}
        }}
        """
    
    def _create_weekly_structure_prompt(self, strategy: Dict[str, Any], preferences: Dict[str, Any]) -> str:
        """Create weekly meal structure prompt"""
        return f"""
        Based on the weekly strategy, create a detailed meal structure for each day of the week.

        WEEKLY STRATEGY: {strategy}

        USER PREFERENCES:
        - Daily Calorie Target: {preferences.get('daily_calorie_target', 2000)} kcal
        - Meals per Day: {preferences.get('meals_per_day', 3)}
        - Dietary Restrictions: {preferences.get('dietary_preferences', [])}

        Create a meal structure that includes:
        1. Meal types for each day (breakfast, lunch, dinner, snacks)
        2. Calorie distribution per meal
        3. Cuisine assignment per day
        4. Complexity level per meal
        5. Prep time considerations

        Respond with a JSON object:
        {{
            "weekly_structure": {{
                "monday": {{"meals": ["breakfast", "lunch", "dinner"], "cuisine": "string", "calorie_distribution": [number, number, number]}},
                "tuesday": {{"meals": ["breakfast", "lunch", "dinner"], "cuisine": "string", "calorie_distribution": [number, number, number]}},
                ...
            }}
        }}
        """
    
    def _create_weekly_recipes_prompt(self, structure: Dict[str, Any], preferences: Dict[str, Any]) -> str:
        """Create weekly recipes prompt"""
        return f"""
        Create specific recipes for each meal in the weekly structure. Ensure variety, nutrition, and adherence to preferences.

        WEEKLY STRUCTURE: {structure}

        USER PREFERENCES:
        - Dietary Preferences: {preferences.get('dietary_preferences', [])}
        - Allergies: {preferences.get('allergies', [])}
        - Disliked Ingredients: {preferences.get('disliked_ingredients', [])}
        - Cuisine Preferences: {preferences.get('cuisine_preferences', [])}
        - Daily Calorie Target: {preferences.get('daily_calorie_target', 2000)} kcal

        CRITICAL REQUIREMENTS:
        - CALORIE TARGET: Each day must total close to {preferences.get('daily_calorie_target', 2000)} calories
        - DIETARY RESTRICTIONS: STRICTLY follow: {preferences.get('dietary_preferences', [])}
        - ALLERGIES: NEVER include: {preferences.get('allergies', [])}
        - VARIETY: Each day should have different cuisines and flavors
        - NUTRITION: Balance macronutrients across the week

        Respond with a JSON object:
        {{
            "weekly_meal_plan": {{
                "weekly_plan": [
                    {{
                        "day": "Monday",
                        "meals": [
                            {{
                                "meal_type": "breakfast",
                                "meal_name": "string",
                                "recipe": {{
                                    "title": "string",
                                    "cuisine": "string",
                                    "prep_time": number,
                                    "cook_time": number,
                                    "servings": number,
                                    "difficulty": "easy|medium|hard",
                                    "summary": "string",
                                    "ingredients": [{{"name": "string", "quantity": number, "unit": "string"}}],
                                    "instructions": [{{"step": number, "description": "string"}}],
                                    "dietary_tags": ["string"],
                                    "nutrition": {{"calories": number, "protein": number, "carbs": number, "fats": number}}
                                }}
                            }}
                        ]
                    }}
                ]
            }}
        }}
        """
    
    def _add_snacks_if_needed(self, meal_plan_data: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Add snacks if calorie target isn't met"""
        try:
            target_calories = preferences.get('daily_calorie_target', 2000)
            
            # Calculate current total calories
            total_calories = 0
            meals = meal_plan_data.get('meal_plan', [{}])[0].get('meals', [])
            
            for meal in meals:
                recipe = meal.get('recipe', {})
                nutrition = recipe.get('nutrition', {})
                total_calories += nutrition.get('calories', 0)
            
            # If we're more than 100 calories short, add snacks
            calorie_gap = target_calories - total_calories
            if calorie_gap > 100:
                snacks_needed = self._generate_snacks(calorie_gap, preferences)
                if snacks_needed:
                    meals.extend(snacks_needed)
                    logger.info(f"Added {len(snacks_needed)} snacks to reach calorie target")
            
            return meal_plan_data
            
        except Exception as e:
            logger.error(f"Error adding snacks: {str(e)}")
            return meal_plan_data
    
    def _generate_snacks(self, calorie_gap: int, preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate healthy snacks to fill calorie gap"""
        snacks = []
        
        # Healthy snack options with approximate calories and trainer tips
        snack_options = [
            {
                "name": "Greek Yogurt with Berries",
                "calories": 150,
                "protein": 15,
                "carbs": 20,
                "fats": 2,
                "dietary_tags": ["vegetarian", "high-protein"],
                "nutritionist_tip": "Excellent source of probiotics and protein! Greek yogurt supports gut health while berries provide vitamin C and antioxidants for immune function."
            },
            {
                "name": "Mixed Nuts",
                "calories": 200,
                "protein": 6,
                "carbs": 8,
                "fats": 18,
                "dietary_tags": ["vegan", "gluten-free"],
                "nutritionist_tip": "Rich in heart-healthy monounsaturated fats and vitamin E! Nuts provide essential minerals like magnesium and zinc, supporting cardiovascular health and brain function."
            },
            {
                "name": "Apple with Almond Butter",
                "calories": 180,
                "protein": 4,
                "carbs": 25,
                "fats": 8,
                "dietary_tags": ["vegetarian", "gluten-free"],
                "nutritionist_tip": "Perfect fiber and healthy fat combination! Apples provide pectin fiber for digestive health, while almond butter offers vitamin E and plant-based protein."
            },
            {
                "name": "Hummus with Vegetables",
                "calories": 120,
                "protein": 4,
                "carbs": 15,
                "fats": 5,
                "dietary_tags": ["vegan", "gluten-free"],
                "nutritionist_tip": "Nutrient-dense plant protein! Chickpeas provide folate and iron, while vegetables add phytonutrients and fiber for optimal digestive health and satiety."
            },
            {
                "name": "Protein Smoothie",
                "calories": 250,
                "protein": 25,
                "carbs": 20,
                "fats": 8,
                "dietary_tags": ["vegetarian", "high-protein"],
                "nutritionist_tip": "Complete amino acid profile! High-quality protein supports tissue repair and immune function. Perfect for meeting daily protein requirements efficiently."
            },
            {
                "name": "Hard-Boiled Eggs",
                "calories": 140,
                "protein": 12,
                "carbs": 1,
                "fats": 10,
                "dietary_tags": ["vegetarian", "high-protein", "low-carb"],
                "nutritionist_tip": "Nature's perfect protein! Eggs provide all essential amino acids plus choline for brain health and lutein for eye health. Excellent bioavailability."
            },
            {
                "name": "Cottage Cheese with Pineapple",
                "calories": 160,
                "protein": 18,
                "carbs": 15,
                "fats": 3,
                "dietary_tags": ["vegetarian", "high-protein"],
                "nutritionist_tip": "Slow-release protein for sustained satiety! Cottage cheese provides casein protein and calcium for bone health, while pineapple adds bromelain for digestion."
            },
            {
                "name": "Avocado Toast",
                "calories": 220,
                "protein": 8,
                "carbs": 25,
                "fats": 12,
                "dietary_tags": ["vegetarian", "gluten-free"],
                "nutritionist_tip": "Heart-healthy monounsaturated fats! Avocados provide potassium for blood pressure regulation and folate for cellular function. Great for nutrient absorption."
            },
            {
                "name": "Dark Chocolate with Almonds",
                "calories": 190,
                "protein": 5,
                "carbs": 18,
                "fats": 14,
                "dietary_tags": ["vegetarian", "gluten-free"],
                "nutritionist_tip": "Antioxidant powerhouse! Dark chocolate contains flavonoids and polyphenols that support cardiovascular health and may improve cognitive function."
            },
            {
                "name": "Tuna Salad with Crackers",
                "calories": 200,
                "protein": 20,
                "carbs": 15,
                "fats": 8,
                "dietary_tags": ["pescatarian", "high-protein"],
                "nutritionist_tip": "Omega-3 fatty acid rich! Tuna provides EPA and DHA for brain health, heart function, and anti-inflammatory benefits. Excellent source of selenium and B vitamins."
            },
            {
                "name": "Banana with Peanut Butter",
                "calories": 210,
                "protein": 8,
                "carbs": 30,
                "fats": 9,
                "dietary_tags": ["vegetarian", "gluten-free"],
                "nutritionist_tip": "Natural energy and healthy fats! Bananas provide potassium for muscle function and vitamin B6, while peanut butter offers plant-based protein and vitamin E."
            },
            {
                "name": "Edamame",
                "calories": 130,
                "protein": 12,
                "carbs": 10,
                "fats": 5,
                "dietary_tags": ["vegan", "high-protein", "gluten-free"],
                "nutritionist_tip": "Complete plant protein with isoflavones! Edamame provides all essential amino acids, iron for oxygen transport, and folate for DNA synthesis and cell division."
            },
            {
                "name": "Cheese and Grapes",
                "calories": 170,
                "protein": 8,
                "carbs": 20,
                "fats": 7,
                "dietary_tags": ["vegetarian", "gluten-free"],
                "nutritionist_tip": "Calcium and antioxidant combination! Cheese provides bone-strengthening calcium and vitamin B12, while grapes offer resveratrol and polyphenols for cardiovascular health."
            },
            {
                "name": "Rice Cakes with Turkey",
                "calories": 140,
                "protein": 12,
                "carbs": 15,
                "fats": 3,
                "dietary_tags": ["high-protein", "low-fat"],
                "nutritionist_tip": "Lean protein with essential nutrients! Turkey provides high-quality protein, B vitamins for energy metabolism, and zinc for immune function and wound healing."
            },
            {
                "name": "Chia Pudding",
                "calories": 180,
                "protein": 6,
                "carbs": 20,
                "fats": 8,
                "dietary_tags": ["vegan", "gluten-free"],
                "nutritionist_tip": "Superfood with soluble fiber! Chia seeds provide omega-3 fatty acids, calcium for bone health, and fiber that supports digestive health and blood sugar regulation."
            }
        ]
        
        # Filter snacks based on dietary preferences
        dietary_prefs = preferences.get('dietary_preferences', [])
        allergies = preferences.get('allergies', [])
        
        filtered_snacks = []
        for snack in snack_options:
            # Check dietary restrictions
            if 'vegan' in dietary_prefs and 'vegetarian' not in snack['dietary_tags'] and 'vegan' not in snack['dietary_tags']:
                continue
            if 'vegetarian' in dietary_prefs and 'vegetarian' not in snack['dietary_tags'] and 'vegan' not in snack['dietary_tags']:
                continue
            
            # Check allergies
            if 'nuts' in allergies and 'nuts' in snack['name'].lower():
                continue
            if 'dairy' in allergies and 'yogurt' in snack['name'].lower():
                continue
                
            filtered_snacks.append(snack)
        
        # Add snacks to fill the calorie gap
        remaining_gap = calorie_gap
        for snack in filtered_snacks:
            if remaining_gap <= 0:
                break
                
            snacks.append({
                "meal_type": "snack",
                "meal_name": snack["name"],
                "recipe": {
                    "title": snack["name"],
                    "cuisine": "Healthy",
                    "prep_time": 5,
                    "cook_time": 0,
                    "servings": 1,
                    "difficulty": "easy",
                    "summary": snack.get("nutritionist_tip", "Healthy snack option"),
                    "ingredients": [
                        {"name": "main_ingredient", "quantity": 100, "unit": "g"}
                    ],
                    "instructions": [
                        {"step": 1, "description": "Prepare and enjoy this nutritious snack"}
                    ],
                    "dietary_tags": snack["dietary_tags"],
                    "nutrition": {
                        "calories": snack["calories"],
                        "protein": snack["protein"],
                        "carbs": snack["carbs"],
                        "fats": snack["fats"]
                    }
                }
            })
            
            remaining_gap -= snack["calories"]
        
        return snacks
    
    def _fallback_recipe_generation(self, query: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback recipe when AI fails"""
        return {
            "title": f"Simple {query.title()}",
            "cuisine": "International",
            "ingredients": [{"name": "basic_ingredient", "quantity": 100, "unit": "g"}],
            "instructions": [{"step": 1, "description": "Prepare ingredients and cook"}],
            "nutrition": {"calories": 300, "protein": 15, "carbs": 25, "fats": 10}
        }
    
    def _retrieve_relevant_recipes_for_meal_plan(self, meal_structure: Dict[str, Any], user_preferences: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
        """Retrieve relevant recipes from database for meal planning using RAG"""
        try:
            from services.nutrition_service import NutritionService
            nutrition_service = NutritionService()
            
            # Extract meal types and cuisines from meal structure
            meal_queries = []
            for day, meals in meal_structure.get('daily_meals', {}).items():
                for meal_type, meal_info in meals.items():
                    if isinstance(meal_info, dict) and 'suggestions' in meal_info:
                        for suggestion in meal_info['suggestions']:
                            # Create search query from meal suggestion
                            query_parts = [suggestion.get('name', ''), meal_type]
                            if 'cuisine' in suggestion:
                                query_parts.append(suggestion['cuisine'])
                            query_text = ' '.join(filter(None, query_parts))
                            if query_text:
                                meal_queries.append(query_text)
            
            # Retrieve recipes for each query
            all_retrieved_recipes = []
            for query in meal_queries[:5]:  # Limit to 5 queries to avoid too many results
                similar_recipes = nutrition_service._vector_similarity_search(query, db, limit=3)
                all_retrieved_recipes.extend(similar_recipes)
            
            # Remove duplicates and sort by similarity
            unique_recipes = {}
            for recipe in all_retrieved_recipes:
                recipe_id = recipe['id']
                if recipe_id not in unique_recipes or recipe['similarity'] > unique_recipes[recipe_id]['similarity']:
                    unique_recipes[recipe_id] = recipe
            
            # Sort by similarity and return top recipes
            sorted_recipes = sorted(unique_recipes.values(), key=lambda x: x['similarity'], reverse=True)
            return sorted_recipes[:10]  # Return top 10 most relevant recipes
            
        except Exception as e:
            logger.error(f"Error retrieving recipes for meal plan: {e}")
            return []
    
    def _create_rag_enhanced_recipes_prompt(self, meal_structure: Dict[str, Any], user_preferences: Dict[str, Any], retrieved_recipes: List[Dict[str, Any]]) -> str:
        """Create enhanced recipe generation prompt with retrieved recipes as context"""
        
        # Format retrieved recipes for context
        recipe_context = ""
        if retrieved_recipes:
            recipe_context = "\n\nRELEVANT RECIPES FROM DATABASE:\n"
            for i, recipe in enumerate(retrieved_recipes[:5], 1):
                recipe_context += f"{i}. {recipe['title']} ({recipe['cuisine']}) - {recipe['meal_type']}\n"
                recipe_context += f"   Similarity: {recipe['similarity']:.3f}\n"
        
        base_prompt = self._create_recipes_prompt(meal_structure, user_preferences)
        
        # Enhance with RAG context
        enhanced_prompt = f"""
{base_prompt}

{recipe_context}

IMPORTANT: Use the above recipes as inspiration and reference. You can:
- Adapt these recipes to fit the meal structure
- Use similar ingredients and cooking methods
- Maintain the cuisine styles and meal types
- Ensure recipes match user dietary preferences and restrictions

Generate specific recipes that are inspired by these database recipes but tailored to the meal plan structure.
"""
        
        return enhanced_prompt
