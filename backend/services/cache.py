"""
Caching service for AI recommendations and insights
"""
import time
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import os

class RecommendationCache:
    """Cache for AI recommendations with fallback support"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes for fresh insights
        self.fallback_cache_duration = 3600  # 1 hour for fallback insights
        self.ai_insights_grace_period = 86400  # 24 hours for AI insights when internet is down
        self.max_cache_size = 1000  # Maximum number of cached items
    
    def _generate_cache_key(self, user_id: int, profile_updated_at: str, language: str, goal_hash: str = "") -> str:
        """Generate a unique cache key for insights"""
        return f"insights_{user_id}_{profile_updated_at}_{language}_{goal_hash}"
    
    def _get_goal_hash(self, goals: list) -> str:
        """Generate a hash for goals to include in cache key"""
        if not goals:
            return "no_goals"
        
        # Create a simple hash from goal titles and statuses
        goal_strings = [f"{goal.get('title', '')}_{goal.get('status', '')}" for goal in goals]
        return str(hash("_".join(goal_strings)))
    
    def get_cached_insights(self, user_id: int, profile_updated_at: str, language: str, goals: list = None) -> Optional[Dict[str, Any]]:
        """Get cached insights if available and not expired"""
        goal_hash = self._get_goal_hash(goals or [])
        cache_key = self._generate_cache_key(user_id, profile_updated_at, language, goal_hash)
        
        if cache_key in self.cache:
            cached_data, timestamp, is_fallback = self.cache[cache_key]
            current_time = time.time()
            
            # Check if cache is still valid
            cache_duration = self.fallback_cache_duration if is_fallback else self.cache_duration
            if current_time - timestamp < cache_duration:
                return cached_data
        
        return None
    
    def get_any_cached_ai_insights(self, user_id: int, language: str, current_fitness_goal: str = None) -> Optional[Dict[str, Any]]:
        """Get any cached AI insights for user, even if expired (for offline resilience)"""
        best_cached_insights = None
        best_timestamp = 0
        
        for cache_key, (cached_data, timestamp, is_fallback) in self.cache.items():
            if f"insights_{user_id}_" in cache_key and not is_fallback:
                # Find the most recent AI insights
                if timestamp > best_timestamp:
                    best_cached_insights = cached_data
                    best_timestamp = timestamp
        
        # Only return if the insights are not too old (within grace period)
        if best_cached_insights and best_timestamp > 0:
            current_time = time.time()
            if current_time - best_timestamp < self.ai_insights_grace_period:
                # Check if the cached insights are still relevant for the current goal
                if current_fitness_goal and self._is_goal_relevant(best_cached_insights, current_fitness_goal):
                    return best_cached_insights
                elif not current_fitness_goal:
                    # If no current goal specified, return any cached insights
                    return best_cached_insights
        
        return None
    
    def _is_goal_relevant(self, cached_insights: Dict[str, Any], current_fitness_goal: str) -> bool:
        """Check if cached insights are still relevant for the current fitness goal"""
        # Extract goal from cached insights if available
        insights_text = ""
        if isinstance(cached_insights, dict):
            if 'insights' in cached_insights:
                insights_text = " ".join(cached_insights['insights'])
            elif 'status_analysis' in cached_insights:
                insights_text = cached_insights['status_analysis']
        
        # Check if the insights mention the current goal
        goal_keywords = {
            'weight_loss': ['lose', 'weight loss', 'losing', 'slim', 'diet'],
            'muscle_gain': ['muscle', 'gain', 'bulk', 'strength', 'build'],
            'endurance': ['endurance', 'cardio', 'running', 'cycling'],
            'strength': ['strength', 'power', 'lift', 'heavy'],
            'general_fitness': ['fitness', 'health', 'exercise', 'activity']
        }
        
        current_keywords = goal_keywords.get(current_fitness_goal, [])
        insights_lower = insights_text.lower()
        
        # If insights contain keywords for the current goal, they're relevant
        for keyword in current_keywords:
            if keyword in insights_lower:
                return True
        
        # If no specific goal keywords found, assume insights are general and relevant
        return True
    
    def cache_insights(self, user_id: int, profile_updated_at: str, language: str, 
                      insights: Dict[str, Any], goals: list = None, is_fallback: bool = False):
        """Cache insights with appropriate expiration"""
        goal_hash = self._get_goal_hash(goals or [])
        cache_key = self._generate_cache_key(user_id, profile_updated_at, language, goal_hash)
        
        # Clean up old cache entries if we're at the limit
        if len(self.cache) >= self.max_cache_size:
            self._cleanup_old_entries()
        
        self.cache[cache_key] = (insights, time.time(), is_fallback)
    
    def get_fallback_insights(self, user_id: int, language: str, fitness_goal: str = "general_fitness") -> Dict[str, Any]:
        """Get fallback insights when AI service is unavailable"""
        # Check if cached insights are still relevant for the current goal
        cached_ai_insights = self.get_any_cached_ai_insights(user_id, language, fitness_goal)
        
        if cached_ai_insights:
            print(f"🌐 Internet down - Using cached insights for user {user_id} (grace period active)")
            return cached_ai_insights
        
        # If no relevant cached insights, generate mock insights for the current goal
        print(f"🤖 No relevant cached insights found for user {user_id} (goal: {fitness_goal}), generating mock insights")
        from ai.insights import generate_mock_insights
        return generate_mock_insights(language, fitness_goal)
    
    def _cleanup_old_entries(self):
        """Remove old cache entries to prevent memory bloat"""
        current_time = time.time()
        keys_to_remove = []
        
        for cache_key, (data, timestamp, is_fallback) in self.cache.items():
            cache_duration = self.fallback_cache_duration if is_fallback else self.cache_duration
            if current_time - timestamp > cache_duration:
                keys_to_remove.append(cache_key)
        
        for key in keys_to_remove:
            del self.cache[key]
    
    def clear_user_cache(self, user_id: int):
        """Clear all cached insights for a specific user"""
        keys_to_remove = [key for key in self.cache.keys() if f"insights_{user_id}_" in key]
        for key in keys_to_remove:
            del self.cache[key]
    
    def clear_irrelevant_cache(self, user_id: int, new_fitness_goal: str):
        """Clear cached insights that are no longer relevant for the new fitness goal"""
        keys_to_remove = []
        
        for cache_key, (cached_data, timestamp, is_fallback) in self.cache.items():
            if f"insights_{user_id}_" in cache_key and not is_fallback:
                # Check if cached insights are relevant for the new goal
                if not self._is_goal_relevant(cached_data, new_fitness_goal):
                    keys_to_remove.append(cache_key)
        
        for key in keys_to_remove:
            del self.cache[key]
            print(f"🗑️ Cleared irrelevant cached insights for user {user_id} (new goal: {new_fitness_goal})")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        current_time = time.time()
        active_entries = 0
        fallback_entries = 0
        expired_entries = 0
        
        for cache_key, (data, timestamp, is_fallback) in self.cache.items():
            cache_duration = self.fallback_cache_duration if is_fallback else self.cache_duration
            if current_time - timestamp < cache_duration:
                if is_fallback:
                    fallback_entries += 1
                else:
                    active_entries += 1
            else:
                expired_entries += 1
        
        return {
            "total_entries": len(self.cache),
            "active_entries": active_entries,
            "fallback_entries": fallback_entries,
            "expired_entries": expired_entries,
            "cache_duration": self.cache_duration,
            "fallback_cache_duration": self.fallback_cache_duration
        }

# Global cache instance
recommendation_cache = RecommendationCache()

def get_cached_insights(user_id: int, profile_updated_at: str, language: str, goals: list = None) -> Optional[Dict[str, Any]]:
    """Get cached insights if available"""
    return recommendation_cache.get_cached_insights(user_id, profile_updated_at, language, goals)

def cache_insights(user_id: int, profile_updated_at: str, language: str, 
                  insights: Dict[str, Any], goals: list = None, is_fallback: bool = False):
    """Cache insights with appropriate expiration"""
    recommendation_cache.cache_insights(user_id, profile_updated_at, language, insights, goals, is_fallback)

def get_fallback_insights(user_id: int, language: str, fitness_goal: str = "general_fitness") -> Dict[str, Any]:
    """Get fallback insights when AI service is unavailable"""
    return recommendation_cache.get_fallback_insights(user_id, language, fitness_goal)

def get_any_cached_ai_insights(user_id: int, language: str, current_fitness_goal: str = None) -> Optional[Dict[str, Any]]:
    """Get any cached AI insights for user, even if expired (for offline resilience)"""
    return recommendation_cache.get_any_cached_ai_insights(user_id, language, current_fitness_goal)

def clear_user_cache(user_id: int):
    """Clear all cached insights for a specific user"""
    recommendation_cache.clear_user_cache(user_id)

def clear_irrelevant_cache(user_id: int, new_fitness_goal: str):
    """Clear cached insights that are no longer relevant for the new fitness goal"""
    recommendation_cache.clear_irrelevant_cache(user_id, new_fitness_goal)

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics for monitoring"""
    return recommendation_cache.get_cache_stats()
