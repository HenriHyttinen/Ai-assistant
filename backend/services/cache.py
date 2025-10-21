"""
Enhanced caching service for AI recommendations and insights
"""
import time
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import os

class RecommendationCache:
    """Enhanced cache for AI recommendations with fallback support"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes for fresh insights
        self.fallback_cache_duration = 3600  # 1 hour for fallback insights
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
        # Check if we have any cached insights for this user
        for cache_key, (cached_data, timestamp, is_fallback) in self.cache.items():
            if f"insights_{user_id}_" in cache_key and not is_fallback:
                # Return the most recent non-fallback insights
                return cached_data
        
        # Generate basic fallback insights
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

def clear_user_cache(user_id: int):
    """Clear all cached insights for a specific user"""
    recommendation_cache.clear_user_cache(user_id)

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics for monitoring"""
    return recommendation_cache.get_cache_stats()
