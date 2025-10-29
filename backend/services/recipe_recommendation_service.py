"""
AI-Powered Recipe Recommendation Service
Provides personalized recipe recommendations based on user preferences, history, and nutritional needs
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, or_
from models.nutrition import NutritionalLog, UserNutritionPreferences, MealPlan, MealPlanMeal
from models.recipe import Recipe
from models.user import User
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random

logger = logging.getLogger(__name__)

class RecipeRecommendationService:
    def __init__(self):
        self.logger = logger
        self.vectorizer = None
        self.recipe_embeddings = None
        self.recipe_ids = None

    def get_personalized_recommendations(
        self, 
        user_id: str, 
        db: Session,
        limit: int = 10,
        recommendation_type: str = "mixed"
    ) -> List[Dict[str, Any]]:
        """
        Get personalized recipe recommendations based on user preferences and history
        """
        try:
            # Get user preferences
            user_prefs = self._get_user_preferences(user_id, db)
            
            # Get user's recent meal history
            recent_meals = self._get_recent_meals(user_id, db)
            
            # Get user's nutritional gaps
            nutritional_gaps = self._get_nutritional_gaps(user_id, db)
            
            # Get base recommendations based on type
            if recommendation_type == "nutritional":
                recommendations = self._get_nutritional_recommendations(
                    user_prefs, nutritional_gaps, db, limit
                )
            elif recommendation_type == "similar":
                recommendations = self._get_similar_recommendations(
                    recent_meals, user_prefs, db, limit
                )
            elif recommendation_type == "trending":
                recommendations = self._get_trending_recommendations(
                    user_prefs, db, limit
                )
            elif recommendation_type == "diverse":
                recommendations = self._get_diverse_recommendations(
                    user_prefs, recent_meals, db, limit
                )
            else:  # mixed
                recommendations = self._get_mixed_recommendations(
                    user_prefs, recent_meals, nutritional_gaps, db, limit
                )
            
            # Add recommendation metadata
            for i, rec in enumerate(recommendations):
                rec["recommendation_score"] = rec.get("score", 0.0)
                rec["recommendation_reason"] = self._generate_recommendation_reason(rec, user_prefs, nutritional_gaps)
                rec["rank"] = i + 1
            
            return recommendations[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting personalized recommendations: {e}")
            return self._get_fallback_recommendations(db, limit)

    def get_contextual_recommendations(
        self,
        context: str,
        user_id: str,
        db: Session,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations based on specific context (e.g., "breakfast", "high protein", "quick meal")
        """
        try:
            user_prefs = self._get_user_preferences(user_id, db)
            
            # Use vector similarity search for contextual recommendations
            similar_recipes = self._vector_similarity_search(context, db, limit * 2)
            
            # Filter by user preferences
            filtered_recipes = self._filter_by_preferences(similar_recipes, user_prefs)
            
            # Add context-specific scoring
            for recipe in filtered_recipes:
                recipe["context_score"] = self._calculate_context_score(recipe, context)
                recipe["recommendation_reason"] = f"Similar to '{context}'"
            
            # Sort by context score
            filtered_recipes.sort(key=lambda x: x.get("context_score", 0), reverse=True)
            
            return filtered_recipes[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting contextual recommendations: {e}")
            return []

    def get_meal_specific_recommendations(
        self,
        meal_type: str,
        user_id: str,
        db: Session,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations for specific meal types (breakfast, lunch, dinner, snacks)
        """
        try:
            user_prefs = self._get_user_preferences(user_id, db)
            
            # Query recipes for specific meal type
            recipes = db.query(Recipe).filter(
                and_(
                    Recipe.is_active == True,
                    Recipe.meal_type == meal_type
                )
            ).limit(limit * 3).all()
            
            if not recipes:
                return []
            
            # Convert to recommendation format
            recommendations = []
            for recipe in recipes:
                rec = self._recipe_to_recommendation(recipe)
                rec["meal_type_score"] = 1.0  # Perfect match for meal type
                rec["recommendation_reason"] = f"Perfect for {meal_type}"
                recommendations.append(rec)
            
            # Filter by user preferences and score
            filtered_recipes = self._filter_by_preferences(recommendations, user_prefs)
            self._score_recommendations(filtered_recipes, user_prefs, {})
            
            # Sort by total score
            filtered_recipes.sort(key=lambda x: x.get("total_score", 0), reverse=True)
            
            return filtered_recipes[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting meal-specific recommendations: {e}")
            return []

    def _get_user_preferences(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get user nutrition preferences"""
        prefs = db.query(UserNutritionPreferences).filter(
            UserNutritionPreferences.user_id == user_id
        ).first()
        
        if not prefs:
            return {
                "dietary_preferences": [],
                "allergies": [],
                "disliked_ingredients": [],
                "cuisine_preferences": [],
                "calorie_target": 2000,
                "protein_target": 150,
                "carbs_target": 250,
                "fats_target": 65
            }
        
        return {
            "dietary_preferences": prefs.dietary_preferences or [],
            "allergies": prefs.allergies or [],
            "disliked_ingredients": prefs.disliked_ingredients or [],
            "cuisine_preferences": prefs.cuisine_preferences or [],
            "calorie_target": prefs.daily_calorie_target or 2000,
            "protein_target": 150,  # Default value since this field doesn't exist in the model
            "carbs_target": 250,    # Default value since this field doesn't exist in the model
            "fats_target": 65       # Default value since this field doesn't exist in the model
        }

    def _get_recent_meals(self, user_id: str, db: Session, days: int = 7) -> List[Dict[str, Any]]:
        """Get user's recent meal history"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        recent_logs = db.query(NutritionalLog).filter(
            and_(
                NutritionalLog.user_id == user_id,
                NutritionalLog.log_date >= start_date,
                NutritionalLog.log_date <= end_date
            )
        ).order_by(desc(NutritionalLog.log_date)).limit(20).all()
        
        meals = []
        for log in recent_logs:
            if log.recipe_id:
                recipe = db.query(Recipe).filter(Recipe.id == log.recipe_id).first()
                if recipe:
                    meals.append({
                        "recipe_id": recipe.id,
                        "title": recipe.title,
                        "cuisine": recipe.cuisine,
                        "meal_type": recipe.meal_type,
                        "calories": log.calories or 0,
                        "protein": log.protein or 0,
                        "carbs": log.carbs or 0,
                        "fats": log.fats or 0,
                        "log_date": log.log_date
                    })
        
        return meals

    def _get_nutritional_gaps(self, user_id: str, db: Session) -> Dict[str, float]:
        """Calculate user's nutritional gaps from recent intake"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        recent_logs = db.query(NutritionalLog).filter(
            and_(
                NutritionalLog.user_id == user_id,
                NutritionalLog.log_date >= start_date,
                NutritionalLog.log_date <= end_date
            )
        ).all()
        
        if not recent_logs:
            return {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}
        
        # Calculate daily averages
        total_calories = sum(log.calories or 0 for log in recent_logs)
        total_protein = sum(log.protein or 0 for log in recent_logs)
        total_carbs = sum(log.carbs or 0 for log in recent_logs)
        total_fats = sum(log.fats or 0 for log in recent_logs)
        
        days = len(set(log.log_date for log in recent_logs)) or 1
        
        avg_calories = total_calories / days
        avg_protein = total_protein / days
        avg_carbs = total_carbs / days
        avg_fats = total_fats / days
        
        # Get user targets
        user_prefs = self._get_user_preferences(user_id, db)
        
        return {
            "calories": max(0, user_prefs["calorie_target"] - avg_calories),
            "protein": max(0, user_prefs["protein_target"] - avg_protein),
            "carbs": max(0, user_prefs["carbs_target"] - avg_carbs),
            "fats": max(0, user_prefs["fats_target"] - avg_fats)
        }

    def _get_nutritional_recommendations(
        self, 
        user_prefs: Dict[str, Any], 
        nutritional_gaps: Dict[str, float], 
        db: Session, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get recommendations based on nutritional needs"""
        recommendations = []
        
        # Find recipes that help fill nutritional gaps
        recipes = db.query(Recipe).filter(Recipe.is_active == True).limit(200).all()
        
        for recipe in recipes:
            rec = self._recipe_to_recommendation(recipe)
            
            # Calculate nutritional fit score
            nutrition_score = self._calculate_nutrition_score(rec, nutritional_gaps)
            rec["nutrition_score"] = nutrition_score
            
            # Filter by dietary preferences
            if self._matches_dietary_preferences(rec, user_prefs):
                recommendations.append(rec)
        
        # Sort by nutrition score
        recommendations.sort(key=lambda x: x.get("nutrition_score", 0), reverse=True)
        
        return recommendations[:limit]

    def _get_similar_recommendations(
        self, 
        recent_meals: List[Dict[str, Any]], 
        user_prefs: Dict[str, Any], 
        db: Session, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get recommendations similar to recent meals"""
        if not recent_meals:
            return self._get_fallback_recommendations(db, limit)
        
        recommendations = []
        
        # Get similar recipes for each recent meal
        for meal in recent_meals[:3]:  # Limit to 3 most recent meals
            similar_recipes = self._vector_similarity_search(
                f"{meal['title']} {meal['cuisine']}", 
                db, 
                limit // 2
            )
            
            for recipe in similar_recipes:
                rec = self._recipe_to_recommendation(recipe)
                rec["similarity_score"] = recipe.get("similarity", 0)
                rec["based_on"] = meal["title"]
                
                if self._matches_dietary_preferences(rec, user_prefs):
                    recommendations.append(rec)
        
        # Remove duplicates and sort
        unique_recipes = {}
        for rec in recommendations:
            recipe_id = rec["id"]
            if recipe_id not in unique_recipes or rec.get("similarity_score", 0) > unique_recipes[recipe_id].get("similarity_score", 0):
                unique_recipes[recipe_id] = rec
        
        recommendations = list(unique_recipes.values())
        recommendations.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
        
        return recommendations[:limit]

    def _get_trending_recommendations(
        self, 
        user_prefs: Dict[str, Any], 
        db: Session, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get trending/popular recommendations"""
        # For now, return random high-quality recipes
        # In a real system, this would be based on popularity metrics
        recipes = db.query(Recipe).filter(
            and_(
                Recipe.is_active == True,
                Recipe.per_serving_calories >= 100,  # Quality filter
                Recipe.per_serving_calories <= 800
            )
        ).order_by(func.random()).limit(limit * 2).all()
        
        recommendations = []
        for recipe in recipes:
            rec = self._recipe_to_recommendation(recipe)
            rec["trending_score"] = random.uniform(0.7, 1.0)  # Simulate trending score
            
            if self._matches_dietary_preferences(rec, user_prefs):
                recommendations.append(rec)
        
        recommendations.sort(key=lambda x: x.get("trending_score", 0), reverse=True)
        return recommendations[:limit]

    def _get_diverse_recommendations(
        self, 
        user_prefs: Dict[str, Any], 
        recent_meals: List[Dict[str, Any]], 
        db: Session, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get diverse recommendations across cuisines and meal types"""
        recommendations = []
        
        # Get recent cuisines and meal types to avoid
        recent_cuisines = set(meal.get("cuisine") for meal in recent_meals)
        recent_meal_types = set(meal.get("meal_type") for meal in recent_meals)
        
        # Query for diverse recipes
        recipes = db.query(Recipe).filter(Recipe.is_active == True).limit(100).all()
        
        for recipe in recipes:
            rec = self._recipe_to_recommendation(recipe)
            
            # Calculate diversity score
            diversity_score = 0.0
            if recipe.cuisine not in recent_cuisines:
                diversity_score += 0.5
            if recipe.meal_type not in recent_meal_types:
                diversity_score += 0.5
            
            rec["diversity_score"] = diversity_score
            
            if self._matches_dietary_preferences(rec, user_prefs):
                recommendations.append(rec)
        
        # Sort by diversity score
        recommendations.sort(key=lambda x: x.get("diversity_score", 0), reverse=True)
        
        return recommendations[:limit]

    def _get_mixed_recommendations(
        self, 
        user_prefs: Dict[str, Any], 
        recent_meals: List[Dict[str, Any]], 
        nutritional_gaps: Dict[str, float], 
        db: Session, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get mixed recommendations combining different strategies"""
        # Get recommendations from different strategies
        nutritional_recs = self._get_nutritional_recommendations(user_prefs, nutritional_gaps, db, limit // 3)
        similar_recs = self._get_similar_recommendations(recent_meals, user_prefs, db, limit // 3)
        diverse_recs = self._get_diverse_recommendations(user_prefs, recent_meals, db, limit // 3)
        
        # Combine and score
        all_recommendations = nutritional_recs + similar_recs + diverse_recs
        
        # Remove duplicates
        unique_recipes = {}
        for rec in all_recommendations:
            recipe_id = rec["id"]
            if recipe_id not in unique_recipes:
                unique_recipes[recipe_id] = rec
            else:
                # Keep the one with higher score
                current_score = unique_recipes[recipe_id].get("total_score", 0)
                new_score = rec.get("total_score", 0)
                if new_score > current_score:
                    unique_recipes[recipe_id] = rec
        
        recommendations = list(unique_recipes.values())
        
        # Score all recommendations
        self._score_recommendations(recommendations, user_prefs, nutritional_gaps)
        
        # Sort by total score
        recommendations.sort(key=lambda x: x.get("total_score", 0), reverse=True)
        
        return recommendations[:limit]

    def _vector_similarity_search(self, query: str, db: Session, limit: int) -> List[Dict[str, Any]]:
        """Perform vector similarity search for recipes"""
        try:
            # Get all recipes with embeddings
            recipes = db.query(Recipe).filter(
                Recipe.is_active == True,
                Recipe.embedding.isnot(None)
            ).all()
            
            if not recipes:
                return []
            
            # Use TF-IDF for similarity search
            if not self.vectorizer:
                self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            
            # Prepare recipe texts
            recipe_texts = []
            recipe_data = []
            
            for recipe in recipes:
                recipe_text = self._create_recipe_text(recipe)
                recipe_texts.append(recipe_text)
                recipe_data.append({
                    'id': recipe.id,
                    'title': recipe.title,
                    'cuisine': recipe.cuisine,
                    'meal_type': recipe.meal_type,
                    'similarity': 0.0
                })
            
            # Fit vectorizer and transform
            self.vectorizer.fit(recipe_texts)
            query_vector = self.vectorizer.transform([query])
            recipe_vectors = self.vectorizer.transform(recipe_texts)
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, recipe_vectors)[0]
            
            # Add similarity scores
            for i, similarity in enumerate(similarities):
                recipe_data[i]['similarity'] = float(similarity)
            
            # Sort by similarity
            recipe_data.sort(key=lambda x: x['similarity'], reverse=True)
            
            return recipe_data[:limit]
            
        except Exception as e:
            self.logger.error(f"Error in vector similarity search: {e}")
            return []

    def _create_recipe_text(self, recipe: Recipe) -> str:
        """Create text representation of recipe for embedding"""
        text_parts = [
            recipe.title or "",
            recipe.cuisine or "",
            recipe.meal_type or "",
            recipe.summary or "",
            recipe.difficulty_level or ""
        ]
        
        # Add ingredient names
        if hasattr(recipe, 'ingredients') and recipe.ingredients:
            ingredient_names = [ing.ingredient.name for ing in recipe.ingredients if ing.ingredient]
            text_parts.extend(ingredient_names)
        
        return " ".join(filter(None, text_parts))

    def _recipe_to_recommendation(self, recipe: Recipe) -> Dict[str, Any]:
        """Convert Recipe model to recommendation format with FULL recipe details from our database"""
        # Get ingredients with quantities
        ingredients = []
        if hasattr(recipe, 'ingredients') and recipe.ingredients:
            for ing in recipe.ingredients:
                if ing.ingredient:
                    ingredients.append({
                        "name": ing.ingredient.name,
                        "quantity": ing.quantity,
                        "unit": ing.unit,
                        "notes": ing.notes
                    })
        
        # Get step-by-step instructions
        instructions = []
        if hasattr(recipe, 'instructions') and recipe.instructions:
            for inst in sorted(recipe.instructions, key=lambda x: x.step_number):
                instructions.append({
                    "step_number": inst.step_number,
                    "title": inst.step_title,
                    "description": inst.description,
                    "ingredients_used": inst.ingredients_used or [],
                    "time_required": inst.time_required
                })
        
        return {
            "id": recipe.id,
            "title": recipe.title,
            "cuisine": recipe.cuisine,
            "meal_type": recipe.meal_type,
            "prep_time": recipe.prep_time,
            "cook_time": recipe.cook_time,
            "difficulty_level": recipe.difficulty_level,
            "servings": recipe.servings,
            "summary": recipe.summary,
            "image_url": recipe.image_url,
            "dietary_tags": recipe.dietary_tags or [],
            "per_serving_calories": recipe.per_serving_calories or 0,
            "per_serving_protein": recipe.per_serving_protein or 0,
            "per_serving_carbs": recipe.per_serving_carbs or 0,
            "per_serving_fat": recipe.per_serving_fat or 0,
            "per_serving_sodium": recipe.per_serving_sodium or 0,
            "total_calories": recipe.total_calories or 0,
            "total_protein": recipe.total_protein or 0,
            "total_carbs": recipe.total_carbs or 0,
            "total_fat": recipe.total_fat or 0,
            "total_sodium": recipe.total_sodium or 0,
            # FULL RECIPE DETAILS FROM OUR DATABASE
            "ingredients": ingredients,
            "instructions": instructions,
            "is_from_database": True,  # Flag to indicate this is a real recipe
            "score": 0.0,
            "total_score": 0.0
        }

    def _filter_by_preferences(self, recommendations: List[Dict[str, Any]], user_prefs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter recommendations by user preferences"""
        filtered = []
        
        for rec in recommendations:
            if self._matches_dietary_preferences(rec, user_prefs):
                filtered.append(rec)
        
        return filtered

    def _matches_dietary_preferences(self, recipe: Dict[str, Any], user_prefs: Dict[str, Any]) -> bool:
        """Check if recipe matches user dietary preferences"""
        dietary_prefs = user_prefs.get("dietary_preferences", [])
        allergies = user_prefs.get("allergies", [])
        disliked_ingredients = user_prefs.get("disliked_ingredients", [])
        
        recipe_tags = recipe.get("dietary_tags", [])
        
        # Check dietary preferences
        if dietary_prefs:
            for pref in dietary_prefs:
                if pref not in recipe_tags:
                    return False
        
        # Check allergies (recipes should NOT contain allergens)
        if allergies:
            for allergy in allergies:
                if allergy in recipe_tags:
                    return False
        
        # Check disliked ingredients (basic check)
        if disliked_ingredients:
            recipe_text = f"{recipe.get('title', '')} {recipe.get('summary', '')}".lower()
            for ingredient in disliked_ingredients:
                if ingredient.lower() in recipe_text:
                    return False
        
        return True

    def _calculate_nutrition_score(self, recipe: Dict[str, Any], nutritional_gaps: Dict[str, float]) -> float:
        """Calculate how well recipe fills nutritional gaps"""
        score = 0.0
        
        # Check if recipe helps fill gaps
        for nutrient, gap in nutritional_gaps.items():
            if gap > 0:  # Only consider if there's a gap
                recipe_value = recipe.get(f"per_serving_{nutrient}", 0)
                if recipe_value > 0:
                    # Score based on how much it helps fill the gap
                    contribution = min(recipe_value / gap, 1.0)
                    score += contribution * 0.25  # Weight each nutrient equally
        
        return min(score, 1.0)

    def _calculate_context_score(self, recipe: Dict[str, Any], context: str) -> float:
        """Calculate how well recipe matches context"""
        context_lower = context.lower()
        recipe_text = f"{recipe.get('title', '')} {recipe.get('summary', '')} {recipe.get('cuisine', '')} {recipe.get('meal_type', '')}".lower()
        
        # Simple keyword matching
        context_words = set(context_lower.split())
        recipe_words = set(recipe_text.split())
        
        overlap = len(context_words.intersection(recipe_words))
        total_words = len(context_words)
        
        return overlap / total_words if total_words > 0 else 0.0

    def _score_recommendations(self, recommendations: List[Dict[str, Any]], user_prefs: Dict[str, Any], nutritional_gaps: Dict[str, float]):
        """Score recommendations based on multiple factors"""
        for rec in recommendations:
            scores = []
            
            # Nutrition score
            if "nutrition_score" in rec:
                scores.append(rec["nutrition_score"] * 0.3)
            
            # Similarity score
            if "similarity_score" in rec:
                scores.append(rec["similarity_score"] * 0.25)
            
            # Diversity score
            if "diversity_score" in rec:
                scores.append(rec["diversity_score"] * 0.2)
            
            # Trending score
            if "trending_score" in rec:
                scores.append(rec["trending_score"] * 0.15)
            
            # Context score
            if "context_score" in rec:
                scores.append(rec["context_score"] * 0.1)
            
            # Calculate total score
            rec["total_score"] = sum(scores) if scores else 0.0

    def _generate_recommendation_reason(self, recipe: Dict[str, Any], user_prefs: Dict[str, Any], nutritional_gaps: Dict[str, float]) -> str:
        """Generate human-readable reason for recommendation"""
        reasons = []
        
        # Check nutritional fit
        if recipe.get("nutrition_score", 0) > 0.5:
            reasons.append("helps meet your nutritional goals")
        
        # Check similarity
        if recipe.get("similarity_score", 0) > 0.7:
            reasons.append("similar to meals you've enjoyed")
        
        # Check diversity
        if recipe.get("diversity_score", 0) > 0.5:
            reasons.append("adds variety to your diet")
        
        # Check trending
        if recipe.get("trending_score", 0) > 0.8:
            reasons.append("popular choice")
        
        # Check dietary preferences
        dietary_prefs = user_prefs.get("dietary_preferences", [])
        recipe_tags = recipe.get("dietary_tags", [])
        matching_prefs = [pref for pref in dietary_prefs if pref in recipe_tags]
        if matching_prefs:
            reasons.append(f"matches your {', '.join(matching_prefs)} preferences")
        
        if not reasons:
            reasons.append("recommended for you")
        
        return f"Recommended because it {', '.join(reasons)}"

    def _get_fallback_recommendations(self, db: Session, limit: int) -> List[Dict[str, Any]]:
        """Get fallback recommendations when other methods fail"""
        recipes = db.query(Recipe).filter(
            and_(
                Recipe.is_active == True,
                Recipe.per_serving_calories >= 100,
                Recipe.per_serving_calories <= 800
            )
        ).order_by(func.random()).limit(limit).all()
        
        recommendations = []
        for recipe in recipes:
            rec = self._recipe_to_recommendation(recipe)
            rec["recommendation_reason"] = "Popular choice"
            recommendations.append(rec)
        
        return recommendations
