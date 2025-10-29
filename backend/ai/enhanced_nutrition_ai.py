"""
Enhanced Nutrition AI with Advanced Personalization and Dietary Restrictions

This module extends the existing NutritionAI with:
- Advanced dietary restrictions handling
- Behavioral pattern analysis
- Cultural and seasonal adaptations
- Health goal optimization
- Contextual meal planning
"""

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
from services.enhanced_dietary_service import EnhancedDietaryService, DietaryRestrictionType, DietarySeverity
from services.enhanced_personalization_service import EnhancedPersonalizationService, PersonalizationContext
from .model_cache import model_cache

logger = logging.getLogger(__name__)

class EnhancedNutritionAI:
    """Enhanced Nutrition AI with advanced personalization and dietary restrictions"""
    
    def __init__(self):
        # Use cached models instead of initializing new ones
        self.openai_client = model_cache.openai_client
        
        # Initialize enhanced services
        self.dietary_service = EnhancedDietaryService()
        self.personalization_service = EnhancedPersonalizationService()
        
        # AI parameters optimized for enhanced personalization
        self.parameters = {
            "strategy_generation": {"temperature": 0.4, "top_p": 0.9},
            "meal_planning": {"temperature": 0.5, "top_p": 0.9},
            "recipe_generation": {"temperature": 0.6, "top_p": 0.9},
            "personalization": {"temperature": 0.3, "top_p": 0.8}
        }
        
        self.max_tokens = 4000  # Increased for more detailed responses
    
    def generate_enhanced_meal_plan(self, user_preferences: Dict[str, Any], 
                                  plan_request: MealPlanRequest, 
                                  db: Session = None,
                                  user_behavior_patterns: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate an enhanced meal plan with advanced personalization and dietary restrictions
        
        Args:
            user_preferences: User's dietary preferences and restrictions
            plan_request: Meal plan generation request
            db: Database session for RAG
            user_behavior_patterns: User's behavioral patterns from analysis
            
        Returns:
            Enhanced meal plan with personalization context
        """
        try:
            # Step 1: Analyze dietary restrictions comprehensively
            dietary_analysis = self._analyze_dietary_restrictions(user_preferences)
            
            # Step 2: Generate personalized context
            personalization_context = self._generate_personalization_context(
                user_preferences, user_behavior_patterns
            )
            
            # Step 3: Create enhanced strategy with dietary and personalization insights
            strategy = self._create_enhanced_strategy(
                user_preferences, plan_request, dietary_analysis, personalization_context
            )
            
            # Step 4: Design meal structure with cultural and seasonal considerations
            meal_structure = self._create_enhanced_meal_structure(
                strategy, plan_request, personalization_context
            )
            
            # Step 5: Generate recipes with RAG and dietary compliance
            if db:
                retrieved_recipes = self._retrieve_enhanced_recipes(
                    meal_structure, user_preferences, dietary_analysis, db
                )
                meal_plan = self._generate_enhanced_recipes(
                    meal_structure, user_preferences, dietary_analysis, 
                    personalization_context, retrieved_recipes
                )
            else:
                meal_plan = self._generate_enhanced_recipes(
                    meal_structure, user_preferences, dietary_analysis, 
                    personalization_context, []
                )
            
            # Step 6: Add personalization metadata and compliance verification
            enhanced_meal_plan = self._add_enhancement_metadata(
                meal_plan, dietary_analysis, personalization_context, strategy
            )
            
            return enhanced_meal_plan
            
        except Exception as e:
            logger.error(f"Error in enhanced meal plan generation: {e}")
            # Fallback to basic meal plan generation
            return self._generate_fallback_meal_plan(user_preferences, plan_request)
    
    def _analyze_dietary_restrictions(self, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze dietary restrictions using enhanced dietary service"""
        dietary_restrictions = user_preferences.get('dietary_preferences', [])
        allergies = user_preferences.get('allergies', [])
        disliked_ingredients = user_preferences.get('disliked_ingredients', [])
        
        # Combine all restrictions
        all_restrictions = dietary_restrictions + allergies + disliked_ingredients
        
        # Analyze using enhanced dietary service
        dietary_analysis = self.dietary_service.analyze_dietary_restrictions(all_restrictions)
        
        # Add additional context
        dietary_analysis['user_allergies'] = allergies
        dietary_analysis['user_dislikes'] = disliked_ingredients
        dietary_analysis['restriction_count'] = len(all_restrictions)
        
        return dietary_analysis
    
    def _generate_personalization_context(self, user_preferences: Dict[str, Any], 
                                        behavior_patterns: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate comprehensive personalization context"""
        # Convert behavior patterns to the expected format
        behavior_pattern_objects = []
        if behavior_patterns:
            for pattern in behavior_patterns:
                behavior_pattern_objects.append(
                    self.personalization_service.UserBehaviorPattern(
                        pattern_type=pattern.get('type', 'unknown'),
                        confidence_score=pattern.get('confidence', 0.0),
                        data_points=pattern.get('data_points', 0),
                        last_updated=datetime.now(),
                        pattern_data=pattern.get('data', {})
                    )
                )
        
        # Generate personalized context
        personalization_context = self.personalization_service.generate_personalized_meal_plan_context(
            user_preferences, behavior_pattern_objects
        )
        
        return personalization_context
    
    def _create_enhanced_strategy(self, user_preferences: Dict[str, Any], 
                                plan_request: MealPlanRequest,
                                dietary_analysis: Dict[str, Any],
                                personalization_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create enhanced strategy with dietary and personalization insights"""
        
        if self.openai_client:
            strategy_prompt = self._create_enhanced_strategy_prompt(
                user_preferences, plan_request, dietary_analysis, personalization_context
            )
            
            try:
                response = self._call_openai(strategy_prompt, self.parameters["strategy_generation"]["temperature"])
                strategy = self._parse_json_response(response, "strategy")
                return strategy
            except Exception as e:
                logger.error(f"Error in AI strategy generation: {e}")
                return self._create_fallback_strategy(user_preferences, dietary_analysis)
        else:
            return self._create_fallback_strategy(user_preferences, dietary_analysis)
    
    def _create_enhanced_strategy_prompt(self, user_preferences: Dict[str, Any], 
                                       plan_request: MealPlanRequest,
                                       dietary_analysis: Dict[str, Any],
                                       personalization_context: Dict[str, Any]) -> str:
        """Create enhanced strategy prompt with comprehensive context"""
        
        # Format dietary restrictions
        dietary_restrictions_text = self._format_dietary_restrictions(dietary_analysis)
        
        # Format personalization context
        personalization_text = self._format_personalization_context(personalization_context)
        
        # Format seasonal and cultural context
        seasonal_text = self._format_seasonal_context(personalization_context.get('seasonal_ingredients', []))
        cultural_text = self._format_cultural_context(personalization_context.get('cultural_adaptations', {}))
        
        return f"""
        You are an expert nutritionist and meal planning specialist with advanced knowledge of dietary restrictions, cultural adaptations, and personalized nutrition.

        USER PROFILE:
        - Dietary Preferences: {user_preferences.get('dietary_preferences', [])}
        - Allergies: {user_preferences.get('allergies', [])}
        - Disliked Ingredients: {user_preferences.get('disliked_ingredients', [])}
        - Cuisine Preferences: {user_preferences.get('cuisine_preferences', [])}
        - Calorie Target: {user_preferences.get('daily_calorie_target', 2000)}
        - Protein Target: {user_preferences.get('protein_target', 100)}g
        - Meals per Day: {user_preferences.get('meals_per_day', 3)}

        DIETARY RESTRICTIONS ANALYSIS:
        {dietary_restrictions_text}

        PERSONALIZATION CONTEXT:
        {personalization_text}

        SEASONAL CONSIDERATIONS:
        {seasonal_text}

        CULTURAL ADAPTATIONS:
        {cultural_text}

        HEALTH GOAL OPTIMIZATIONS:
        {self._format_health_goal_context(personalization_context.get('health_goal_optimizations', {}))}

        LIFESTYLE ADAPTATIONS:
        {self._format_lifestyle_context(personalization_context.get('lifestyle_adaptations', {}))}

        BEHAVIORAL INSIGHTS:
        {self._format_behavioral_insights(personalization_context.get('behavioral_insights', {}))}

        REQUIREMENTS:
        1. The total daily calories MUST be close to {user_preferences.get('daily_calorie_target', 2000)} calories (±100)
        2. STRICTLY follow all dietary restrictions and allergies
        3. Incorporate seasonal ingredients when appropriate
        4. Respect cultural meal patterns and preferences
        5. Optimize for the user's health goals and lifestyle
        6. Ensure variety and avoid repetition
        7. Consider cooking method preferences and time constraints

        Respond with ONLY valid JSON following this exact format:
        {{
            "strategy_name": "Descriptive strategy name",
            "macro_distribution": {{"protein": 0.25, "carbs": 0.45, "fats": 0.30}},
            "meal_timing": {{"breakfast": "08:00", "lunch": "12:30", "dinner": "19:00"}},
            "focus_areas": ["area1", "area2", "area3"],
            "avoid_ingredients": ["ingredient1", "ingredient2"],
            "preferred_cooking_methods": ["method1", "method2"],
            "cultural_considerations": ["consideration1", "consideration2"],
            "seasonal_focus": ["ingredient1", "ingredient2"],
            "personalization_notes": ["note1", "note2"],
            "dietary_compliance_score": 95,
            "complexity_level": "medium"
        }}
        """
    
    def _format_dietary_restrictions(self, dietary_analysis: Dict[str, Any]) -> str:
        """Format dietary restrictions for AI prompt"""
        if not dietary_analysis:
            return "No specific dietary restrictions identified."
        
        text = f"Dietary Complexity Score: {dietary_analysis.get('dietary_complexity_score', 0)}/100\n"
        text += f"Overall Severity: {dietary_analysis.get('overall_severity', 'none')}\n"
        
        if dietary_analysis.get('excluded_ingredients'):
            text += f"Excluded Ingredients: {', '.join(dietary_analysis['excluded_ingredients'])}\n"
        
        if dietary_analysis.get('excluded_cooking_methods'):
            text += f"Excluded Cooking Methods: {', '.join(dietary_analysis['excluded_cooking_methods'])}\n"
        
        if dietary_analysis.get('cultural_contexts'):
            text += f"Cultural Contexts: {', '.join(dietary_analysis['cultural_contexts'])}\n"
        
        if dietary_analysis.get('medical_considerations'):
            text += f"Medical Considerations: {', '.join(dietary_analysis['medical_considerations'])}\n"
        
        if dietary_analysis.get('compatibility_recommendations'):
            text += f"Compatibility Recommendations: {', '.join(dietary_analysis['compatibility_recommendations'])}\n"
        
        return text
    
    def _format_personalization_context(self, personalization_context: Dict[str, Any]) -> str:
        """Format personalization context for AI prompt"""
        if not personalization_context:
            return "No specific personalization context available."
        
        text = f"Personalization Score: {personalization_context.get('personalization_score', 0)}/100\n"
        
        if personalization_context.get('behavioral_insights'):
            insights = personalization_context['behavioral_insights']
            if insights.get('cuisine_preferences'):
                text += f"Preferred Cuisines: {', '.join(insights['cuisine_preferences'])}\n"
            if insights.get('ingredient_preferences'):
                text += f"Preferred Ingredients: {', '.join(insights['ingredient_preferences'][:5])}\n"
            if insights.get('cooking_preferences'):
                text += f"Preferred Cooking Methods: {', '.join(insights['cooking_preferences'])}\n"
        
        return text
    
    def _format_seasonal_context(self, seasonal_ingredients: List[str]) -> str:
        """Format seasonal context for AI prompt"""
        if not seasonal_ingredients:
            return "No specific seasonal considerations."
        
        return f"Seasonal Ingredients to Prioritize: {', '.join(seasonal_ingredients[:10])}"
    
    def _format_cultural_context(self, cultural_adaptations: Dict[str, Any]) -> str:
        """Format cultural context for AI prompt"""
        if not cultural_adaptations:
            return "No specific cultural adaptations."
        
        text = "Cultural Meal Patterns:\n"
        if cultural_adaptations.get('breakfast'):
            text += f"- Breakfast: {', '.join(cultural_adaptations['breakfast'])}\n"
        if cultural_adaptations.get('lunch'):
            text += f"- Lunch: {', '.join(cultural_adaptations['lunch'])}\n"
        if cultural_adaptations.get('dinner'):
            text += f"- Dinner: {', '.join(cultural_adaptations['dinner'])}\n"
        if cultural_adaptations.get('cooking_methods'):
            text += f"- Preferred Cooking Methods: {', '.join(cultural_adaptations['cooking_methods'])}\n"
        
        return text
    
    def _format_health_goal_context(self, health_goal_optimizations: Dict[str, Any]) -> str:
        """Format health goal context for AI prompt"""
        if not health_goal_optimizations:
            return "No specific health goal optimizations."
        
        text = "Health Goal Optimizations:\n"
        if health_goal_optimizations.get('nutrient_priorities'):
            text += f"- Nutrient Priorities: {', '.join(health_goal_optimizations['nutrient_priorities'])}\n"
        if health_goal_optimizations.get('focus'):
            text += f"- Focus Areas: {', '.join(health_goal_optimizations['focus'])}\n"
        if health_goal_optimizations.get('avoid'):
            text += f"- Avoid: {', '.join(health_goal_optimizations['avoid'])}\n"
        
        return text
    
    def _format_lifestyle_context(self, lifestyle_adaptations: Dict[str, Any]) -> str:
        """Format lifestyle context for AI prompt"""
        if not lifestyle_adaptations:
            return "No specific lifestyle adaptations."
        
        text = "Lifestyle Adaptations:\n"
        for key, value in lifestyle_adaptations.items():
            if isinstance(value, bool) and value:
                text += f"- {key.replace('_', ' ').title()}\n"
            elif isinstance(value, str):
                text += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        return text
    
    def _format_behavioral_insights(self, behavioral_insights: Dict[str, Any]) -> str:
        """Format behavioral insights for AI prompt"""
        if not behavioral_insights:
            return "No specific behavioral insights available."
        
        text = "Behavioral Insights:\n"
        if behavioral_insights.get('cuisine_preferences'):
            text += f"- Preferred Cuisines: {', '.join(behavioral_insights['cuisine_preferences'])}\n"
        if behavioral_insights.get('ingredient_preferences'):
            text += f"- Preferred Ingredients: {', '.join(behavioral_insights['ingredient_preferences'][:5])}\n"
        if behavioral_insights.get('cooking_preferences'):
            text += f"- Preferred Cooking Methods: {', '.join(behavioral_insights['cooking_preferences'])}\n"
        if behavioral_insights.get('meal_timing_preferences'):
            timing = behavioral_insights['meal_timing_preferences']
            if timing.get('breakfast_time'):
                text += f"- Typical Breakfast Time: {timing['breakfast_time']:.1f}:00\n"
            if timing.get('lunch_time'):
                text += f"- Typical Lunch Time: {timing['lunch_time']:.1f}:00\n"
            if timing.get('dinner_time'):
                text += f"- Typical Dinner Time: {timing['dinner_time']:.1f}:00\n"
        
        return text
    
    def _create_enhanced_meal_structure(self, strategy: Dict[str, Any], 
                                      plan_request: MealPlanRequest,
                                      personalization_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create enhanced meal structure with cultural and seasonal considerations"""
        
        if self.openai_client:
            structure_prompt = self._create_enhanced_structure_prompt(
                strategy, plan_request, personalization_context
            )
            
            try:
                response = self._call_openai(structure_prompt, self.parameters["meal_planning"]["temperature"])
                meal_structure = self._parse_json_response(response, "structure")
                return meal_structure
            except Exception as e:
                logger.error(f"Error in AI meal structure generation: {e}")
                return self._create_fallback_meal_structure(strategy, plan_request)
        else:
            return self._create_fallback_meal_structure(strategy, plan_request)
    
    def _create_enhanced_structure_prompt(self, strategy: Dict[str, Any], 
                                        plan_request: MealPlanRequest,
                                        personalization_context: Dict[str, Any]) -> str:
        """Create enhanced meal structure prompt"""
        
        return f"""
        Based on the strategy and personalization context, design a detailed meal structure for a {plan_request.plan_type} meal plan.

        STRATEGY CONTEXT:
        - Strategy Name: {strategy.get('strategy_name', 'General Strategy')}
        - Macro Distribution: {strategy.get('macro_distribution', {})}
        - Focus Areas: {strategy.get('focus_areas', [])}
        - Avoid Ingredients: {strategy.get('avoid_ingredients', [])}
        - Preferred Cooking Methods: {strategy.get('preferred_cooking_methods', [])}
        - Cultural Considerations: {strategy.get('cultural_considerations', [])}
        - Seasonal Focus: {strategy.get('seasonal_focus', [])}

        PERSONALIZATION CONTEXT:
        - Seasonal Ingredients: {personalization_context.get('seasonal_ingredients', [])}
        - Cultural Adaptations: {personalization_context.get('cultural_adaptations', {})}
        - Health Goal Optimizations: {personalization_context.get('health_goal_optimizations', {})}
        - Lifestyle Adaptations: {personalization_context.get('lifestyle_adaptations', {})}

        REQUIREMENTS:
        1. Create a {plan_request.plan_type} meal plan structure
        2. Incorporate seasonal ingredients where appropriate
        3. Respect cultural meal patterns and preferences
        4. Ensure variety across meals and days
        5. Consider cooking method preferences
        6. Balance macronutrients according to strategy
        7. Include appropriate meal timing

        Respond with ONLY valid JSON following this exact format:
        {{
            "meal_structure": {{
                "breakfast": {{
                    "cuisine_style": "style",
                    "cooking_method": "method",
                    "key_ingredients": ["ingredient1", "ingredient2"],
                    "calorie_target": 500,
                    "macro_focus": "protein"
                }},
                "lunch": {{
                    "cuisine_style": "style",
                    "cooking_method": "method", 
                    "key_ingredients": ["ingredient1", "ingredient2"],
                    "calorie_target": 600,
                    "macro_focus": "balanced"
                }},
                "dinner": {{
                    "cuisine_style": "style",
                    "cooking_method": "method",
                    "key_ingredients": ["ingredient1", "ingredient2"],
                    "calorie_target": 700,
                    "macro_focus": "protein"
                }}
            }},
            "snacks": {{
                "afternoon": {{
                    "type": "healthy_snack",
                    "calorie_target": 200,
                    "key_ingredients": ["ingredient1", "ingredient2"]
                }}
            }},
            "variety_notes": ["note1", "note2"],
            "cultural_adaptations": ["adaptation1", "adaptation2"],
            "seasonal_highlights": ["ingredient1", "ingredient2"]
        }}
        """
    
    def _retrieve_enhanced_recipes(self, meal_structure: Dict[str, Any], 
                                 user_preferences: Dict[str, Any],
                                 dietary_analysis: Dict[str, Any],
                                 db: Session) -> List[Dict[str, Any]]:
        """Retrieve recipes using enhanced RAG with dietary compliance"""
        try:
            # Build enhanced search criteria
            search_criteria = self._build_enhanced_search_criteria(
                meal_structure, user_preferences, dietary_analysis
            )
            
            # Use existing RAG system with enhanced criteria
            retrieved_recipes = self._retrieve_relevant_recipes_for_meal_plan(
                meal_structure, user_preferences, db
            )
            
            # Filter for dietary compliance
            compliant_recipes = self._filter_dietary_compliant_recipes(
                retrieved_recipes, dietary_analysis
            )
            
            return compliant_recipes
            
        except Exception as e:
            logger.error(f"Error in enhanced recipe retrieval: {e}")
            return []
    
    def _retrieve_relevant_recipes_for_meal_plan(self, meal_structure: Dict[str, Any], 
                                               user_preferences: Dict[str, Any], 
                                               db: Session) -> List[Dict[str, Any]]:
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
    
    def _build_enhanced_search_criteria(self, meal_structure: Dict[str, Any],
                                      user_preferences: Dict[str, Any],
                                      dietary_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Build enhanced search criteria for recipe retrieval"""
        criteria = {
            "cuisine_styles": [],
            "cooking_methods": [],
            "key_ingredients": [],
            "excluded_ingredients": dietary_analysis.get('excluded_ingredients', []),
            "dietary_tags": user_preferences.get('dietary_preferences', []),
            "calorie_ranges": {},
            "macro_focus": []
        }
        
        # Extract criteria from meal structure
        for meal_type, meal_info in meal_structure.get('meal_structure', {}).items():
            if 'cuisine_style' in meal_info:
                criteria['cuisine_styles'].append(meal_info['cuisine_style'])
            if 'cooking_method' in meal_info:
                criteria['cooking_methods'].append(meal_info['cooking_method'])
            if 'key_ingredients' in meal_info:
                criteria['key_ingredients'].extend(meal_info['key_ingredients'])
            if 'macro_focus' in meal_info:
                criteria['macro_focus'].append(meal_info['macro_focus'])
            if 'calorie_target' in meal_info:
                calorie_target = meal_info['calorie_target']
                criteria['calorie_ranges'][meal_type] = {
                    'min': int(calorie_target * 0.8),
                    'max': int(calorie_target * 1.2)
                }
        
        return criteria
    
    def _filter_dietary_compliant_recipes(self, recipes: List[Dict[str, Any]], 
                                        dietary_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter recipes for dietary compliance"""
        if not dietary_analysis or not dietary_analysis.get('excluded_ingredients'):
            return recipes
        
        excluded_ingredients = set(dietary_analysis['excluded_ingredients'])
        compliant_recipes = []
        
        for recipe in recipes:
            recipe_ingredients = set(recipe.get('ingredients', []))
            
            # Check if recipe contains any excluded ingredients
            if not recipe_ingredients.intersection(excluded_ingredients):
                compliant_recipes.append(recipe)
        
        return compliant_recipes
    
    def _generate_enhanced_recipes(self, meal_structure: Dict[str, Any], 
                                 user_preferences: Dict[str, Any],
                                 dietary_analysis: Dict[str, Any],
                                 personalization_context: Dict[str, Any],
                                 retrieved_recipes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate enhanced recipes with personalization and dietary compliance"""
        
        if self.openai_client:
            recipes_prompt = self._create_enhanced_recipes_prompt(
                meal_structure, user_preferences, dietary_analysis, 
                personalization_context, retrieved_recipes
            )
            
            try:
                response = self._call_openai(recipes_prompt, self.parameters["recipe_generation"]["temperature"])
                meal_plan = self._parse_json_response(response, "meal_plan")
                return meal_plan
            except Exception as e:
                logger.error(f"Error in AI recipe generation: {e}")
                return self._create_fallback_meal_plan(meal_structure, user_preferences)
        else:
            return self._create_fallback_meal_plan(meal_structure, user_preferences)
    
    def _create_enhanced_recipes_prompt(self, meal_structure: Dict[str, Any],
                                      user_preferences: Dict[str, Any],
                                      dietary_analysis: Dict[str, Any],
                                      personalization_context: Dict[str, Any],
                                      retrieved_recipes: List[Dict[str, Any]]) -> str:
        """Create enhanced recipes prompt with comprehensive context"""
        
        # Format retrieved recipes
        recipes_context = ""
        if retrieved_recipes:
            recipes_context = "AVAILABLE RECIPES FROM DATABASE:\n"
            for i, recipe in enumerate(retrieved_recipes[:10]):  # Limit to top 10
                recipes_context += f"{i+1}. {recipe.get('title', 'Unknown')} - {recipe.get('cuisine', 'Unknown')} - {recipe.get('calories', 0)} cal\n"
                recipes_context += f"   Ingredients: {', '.join(recipe.get('ingredients', [])[:5])}\n"
                recipes_context += f"   Cooking Method: {recipe.get('cooking_method', 'Unknown')}\n\n"
        
        return f"""
        Create a detailed meal plan based on the meal structure, dietary restrictions, and personalization context.

        MEAL STRUCTURE:
        {json.dumps(meal_structure, indent=2)}

        DIETARY RESTRICTIONS:
        - Excluded Ingredients: {dietary_analysis.get('excluded_ingredients', [])}
        - Dietary Complexity Score: {dietary_analysis.get('dietary_complexity_score', 0)}/100
        - Overall Severity: {dietary_analysis.get('overall_severity', 'none')}

        PERSONALIZATION CONTEXT:
        - Seasonal Ingredients: {personalization_context.get('seasonal_ingredients', [])}
        - Cultural Adaptations: {personalization_context.get('cultural_adaptations', {})}
        - Health Goal Optimizations: {personalization_context.get('health_goal_optimizations', {})}

        {recipes_context}

        REQUIREMENTS:
        1. Create specific recipes for each meal following the structure
        2. Ensure all recipes comply with dietary restrictions
        3. Incorporate seasonal ingredients where appropriate
        4. Respect cultural meal patterns and preferences
        5. Include detailed nutritional information
        6. Provide cooking instructions and timing
        7. Ensure variety and avoid repetition
        8. Use available recipes from database when possible

        Respond with ONLY valid JSON following this exact format:
        {{
            "meal_plan": {{
                "breakfast": {{
                    "name": "Recipe Name",
                    "cuisine": "Cuisine Type",
                    "cooking_method": "Method",
                    "prep_time": 15,
                    "cook_time": 20,
                    "servings": 1,
                    "ingredients": [
                        {{"name": "ingredient", "amount": "1 cup", "notes": "optional"}}
                    ],
                    "instructions": ["step1", "step2"],
                    "nutrition": {{
                        "calories": 500,
                        "protein": 25,
                        "carbs": 45,
                        "fat": 20
                    }},
                    "dietary_tags": ["tag1", "tag2"],
                    "seasonal_ingredients": ["ingredient1"],
                    "cultural_notes": "notes"
                }},
                "lunch": {{...}},
                "dinner": {{...}}
            }},
            "snacks": {{
                "afternoon": {{
                    "name": "Snack Name",
                    "nutrition": {{"calories": 200, "protein": 10, "carbs": 20, "fat": 8}}
                }}
            }},
            "meal_plan_metadata": {{
                "total_calories": 2000,
                "dietary_compliance_score": 95,
                "cultural_authenticity_score": 90,
                "seasonal_relevance_score": 85,
                "variety_score": 88,
                "personalization_score": 92
            }},
            "enhancement_notes": ["note1", "note2"]
        }}
        """
    
    def _add_enhancement_metadata(self, meal_plan: Dict[str, Any], 
                                dietary_analysis: Dict[str, Any],
                                personalization_context: Dict[str, Any],
                                strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Add enhancement metadata to the meal plan"""
        
        # Calculate enhancement scores
        dietary_compliance_score = self._calculate_dietary_compliance_score(meal_plan, dietary_analysis)
        personalization_score = personalization_context.get('personalization_score', 0)
        variety_score = self._calculate_variety_score(meal_plan)
        cultural_authenticity_score = self._calculate_cultural_authenticity_score(meal_plan, personalization_context)
        seasonal_relevance_score = self._calculate_seasonal_relevance_score(meal_plan, personalization_context)
        
        # Add metadata to meal plan
        if 'meal_plan_metadata' not in meal_plan:
            meal_plan['meal_plan_metadata'] = {}
        
        meal_plan['meal_plan_metadata'].update({
            'dietary_compliance_score': dietary_compliance_score,
            'personalization_score': personalization_score,
            'variety_score': variety_score,
            'cultural_authenticity_score': cultural_authenticity_score,
            'seasonal_relevance_score': seasonal_relevance_score,
            'overall_enhancement_score': (dietary_compliance_score + personalization_score + variety_score + 
                                        cultural_authenticity_score + seasonal_relevance_score) / 5,
            'dietary_complexity_handled': dietary_analysis.get('dietary_complexity_score', 0),
            'restrictions_count': dietary_analysis.get('restriction_count', 0),
            'enhancement_features_used': [
                'dietary_restrictions_analysis',
                'personalization_context',
                'seasonal_adaptations',
                'cultural_considerations',
                'behavioral_insights'
            ]
        })
        
        return meal_plan
    
    def _calculate_dietary_compliance_score(self, meal_plan: Dict[str, Any], 
                                          dietary_analysis: Dict[str, Any]) -> int:
        """Calculate dietary compliance score (0-100)"""
        if not dietary_analysis or not dietary_analysis.get('excluded_ingredients'):
            return 100
        
        excluded_ingredients = set(dietary_analysis['excluded_ingredients'])
        total_ingredients = 0
        compliant_ingredients = 0
        
        for meal_type, meal in meal_plan.get('meal_plan', {}).items():
            if isinstance(meal, dict) and 'ingredients' in meal:
                for ingredient in meal['ingredients']:
                    if isinstance(ingredient, dict):
                        ingredient_name = ingredient.get('name', '').lower()
                    else:
                        ingredient_name = str(ingredient).lower()
                    
                    total_ingredients += 1
                    if not any(excluded in ingredient_name for excluded in excluded_ingredients):
                        compliant_ingredients += 1
        
        if total_ingredients == 0:
            return 100
        
        return int((compliant_ingredients / total_ingredients) * 100)
    
    def _calculate_variety_score(self, meal_plan: Dict[str, Any]) -> int:
        """Calculate variety score (0-100)"""
        meals = meal_plan.get('meal_plan', {})
        if not meals:
            return 0
        
        # Count unique cuisines, cooking methods, and ingredients
        cuisines = set()
        cooking_methods = set()
        ingredients = set()
        
        for meal_type, meal in meals.items():
            if isinstance(meal, dict):
                if 'cuisine' in meal:
                    cuisines.add(meal['cuisine'])
                if 'cooking_method' in meal:
                    cooking_methods.add(meal['cooking_method'])
                if 'ingredients' in meal:
                    for ingredient in meal['ingredients']:
                        if isinstance(ingredient, dict):
                            ingredients.add(ingredient.get('name', ''))
                        else:
                            ingredients.add(str(ingredient))
        
        # Calculate variety score based on diversity
        cuisine_score = min(len(cuisines) * 20, 100)
        method_score = min(len(cooking_methods) * 25, 100)
        ingredient_score = min(len(ingredients) * 2, 100)
        
        return int((cuisine_score + method_score + ingredient_score) / 3)
    
    def _calculate_cultural_authenticity_score(self, meal_plan: Dict[str, Any], 
                                             personalization_context: Dict[str, Any]) -> int:
        """Calculate cultural authenticity score (0-100)"""
        cultural_adaptations = personalization_context.get('cultural_adaptations', {})
        if not cultural_adaptations:
            return 50  # Neutral score if no cultural context
        
        # This is a simplified calculation - in practice, you'd have more sophisticated cultural matching
        meals = meal_plan.get('meal_plan', {})
        cultural_matches = 0
        total_meals = 0
        
        for meal_type, meal in meals.items():
            if isinstance(meal, dict) and 'cuisine' in meal:
                total_meals += 1
                meal_cuisine = meal['cuisine'].lower()
                # Check if meal cuisine matches cultural preferences
                if any(pref.lower() in meal_cuisine for pref in cultural_adaptations.get('preferred_cuisines', [])):
                    cultural_matches += 1
        
        if total_meals == 0:
            return 50
        
        return int((cultural_matches / total_meals) * 100)
    
    def _calculate_seasonal_relevance_score(self, meal_plan: Dict[str, Any], 
                                          personalization_context: Dict[str, Any]) -> int:
        """Calculate seasonal relevance score (0-100)"""
        seasonal_ingredients = personalization_context.get('seasonal_ingredients', [])
        if not seasonal_ingredients:
            return 50  # Neutral score if no seasonal context
        
        meals = meal_plan.get('meal_plan', {})
        seasonal_matches = 0
        total_ingredients = 0
        
        for meal_type, meal in meals.items():
            if isinstance(meal, dict) and 'ingredients' in meal:
                for ingredient in meal['ingredients']:
                    if isinstance(ingredient, dict):
                        ingredient_name = ingredient.get('name', '').lower()
                    else:
                        ingredient_name = str(ingredient).lower()
                    
                    total_ingredients += 1
                    if any(seasonal in ingredient_name for seasonal in seasonal_ingredients):
                        seasonal_matches += 1
        
        if total_ingredients == 0:
            return 50
        
        return int((seasonal_matches / total_ingredients) * 100)
    
    def _call_openai(self, prompt: str, temperature: float = 0.7) -> str:
        """Call OpenAI API with enhanced error handling"""
        if not self.openai_client:
            raise Exception("OpenAI client not available")
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _parse_json_response(self, response: str, expected_key: str) -> Dict[str, Any]:
        """Parse JSON response with enhanced error handling"""
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[start_idx:end_idx]
            data = json.loads(json_str)
            
            if expected_key in data:
                return data[expected_key]
            else:
                return data
                
        except Exception as e:
            logger.error(f"Error parsing JSON response: {e}")
            logger.error(f"Response: {response}")
            raise ValueError(f"Failed to parse JSON response: {e}")
    
    def _create_fallback_strategy(self, user_preferences: Dict[str, Any], 
                                dietary_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback strategy when AI is not available"""
        return {
            "strategy_name": "Balanced Nutrition Strategy",
            "macro_distribution": {"protein": 0.25, "carbs": 0.45, "fats": 0.30},
            "meal_timing": {"breakfast": "08:00", "lunch": "12:30", "dinner": "19:00"},
            "focus_areas": ["balanced_nutrition", "variety", "fresh_ingredients"],
            "avoid_ingredients": dietary_analysis.get('excluded_ingredients', []),
            "preferred_cooking_methods": ["grilling", "steaming", "baking"],
            "cultural_considerations": [],
            "seasonal_focus": [],
            "personalization_notes": ["Basic strategy - AI not available"],
            "dietary_compliance_score": 85,
            "complexity_level": "basic"
        }
    
    def _create_fallback_meal_structure(self, strategy: Dict[str, Any], 
                                      plan_request: MealPlanRequest) -> Dict[str, Any]:
        """Create fallback meal structure when AI is not available"""
        return {
            "meal_structure": {
                "breakfast": {
                    "cuisine_style": "balanced",
                    "cooking_method": "simple",
                    "key_ingredients": ["eggs", "vegetables", "whole_grain"],
                    "calorie_target": 500,
                    "macro_focus": "protein"
                },
                "lunch": {
                    "cuisine_style": "balanced",
                    "cooking_method": "grilling",
                    "key_ingredients": ["lean_protein", "vegetables", "grains"],
                    "calorie_target": 600,
                    "macro_focus": "balanced"
                },
                "dinner": {
                    "cuisine_style": "balanced",
                    "cooking_method": "baking",
                    "key_ingredients": ["protein", "vegetables", "healthy_fats"],
                    "calorie_target": 700,
                    "macro_focus": "protein"
                }
            },
            "snacks": {
                "afternoon": {
                    "type": "healthy_snack",
                    "calorie_target": 200,
                    "key_ingredients": ["nuts", "fruits"]
                }
            },
            "variety_notes": ["Basic structure - AI not available"],
            "cultural_adaptations": [],
            "seasonal_highlights": []
        }
    
    def _create_fallback_meal_plan(self, meal_structure: Dict[str, Any], 
                                 user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback meal plan when AI is not available"""
        return {
            "meal_plan": {
                "breakfast": {
                    "name": "Balanced Breakfast",
                    "cuisine": "International",
                    "cooking_method": "simple",
                    "prep_time": 10,
                    "cook_time": 15,
                    "servings": 1,
                    "ingredients": [
                        {"name": "eggs", "amount": "2", "notes": "organic"},
                        {"name": "spinach", "amount": "1 cup", "notes": "fresh"},
                        {"name": "whole_grain_bread", "amount": "1 slice", "notes": "toasted"}
                    ],
                    "instructions": [
                        "Heat pan and cook eggs",
                        "Add spinach and cook until wilted",
                        "Serve with toasted bread"
                    ],
                    "nutrition": {
                        "calories": 350,
                        "protein": 20,
                        "carbs": 25,
                        "fat": 15
                    },
                    "dietary_tags": ["high_protein", "balanced"],
                    "seasonal_ingredients": [],
                    "cultural_notes": "Simple, nutritious breakfast"
                }
            },
            "snacks": {
                "afternoon": {
                    "name": "Healthy Snack",
                    "nutrition": {"calories": 150, "protein": 5, "carbs": 15, "fat": 8}
                }
            },
            "meal_plan_metadata": {
                "total_calories": 2000,
                "dietary_compliance_score": 85,
                "cultural_authenticity_score": 50,
                "seasonal_relevance_score": 50,
                "variety_score": 60,
                "personalization_score": 30
            },
            "enhancement_notes": ["Fallback meal plan - AI not available"]
        }
    
    def _generate_fallback_meal_plan(self, user_preferences: Dict[str, Any], 
                                   plan_request: MealPlanRequest) -> Dict[str, Any]:
        """Generate fallback meal plan when enhanced features are not available"""
        return {
            "strategy": self._create_fallback_strategy(user_preferences, {}),
            "meal_plan": self._create_fallback_meal_plan({}, user_preferences),
            "enhancement_metadata": {
                "ai_available": False,
                "fallback_mode": True,
                "enhancement_features_used": []
            }
        }

