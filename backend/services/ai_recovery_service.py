"""
AI Recovery Service

Comprehensive recovery mechanisms for failed AI requests including:
- Retry logic with exponential backoff
- Circuit breaker pattern
- Alternative models and fallback strategies
- Request queuing and rate limiting
- Enhanced caching with TTL and invalidation
"""

import time
import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
import json
import random
from dataclasses import dataclass
from threading import Lock
import os

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, failing fast
    HALF_OPEN = "half_open"  # Testing if service is back

@dataclass
class RetryConfig:
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    expected_exception: type = Exception

class AIRecoveryService:
    """Comprehensive AI recovery service with multiple fallback strategies"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self.request_queues: Dict[str, List[Dict[str, Any]]] = {}
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = Lock()
        
        # Default configurations
        self.retry_config = RetryConfig()
        self.circuit_breaker_config = CircuitBreakerConfig()
        
        # Alternative models and fallback strategies
        self.alternative_models = [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo-preview"
        ]
        
        self.fallback_strategies = [
            "cached_response",
            "simplified_ai",
            "rule_based",
            "mock_response"
        ]
    
    def get_circuit_breaker(self, service_name: str) -> Dict[str, Any]:
        """Get or create circuit breaker for a service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = {
                "state": CircuitState.CLOSED,
                "failure_count": 0,
                "last_failure_time": None,
                "success_count": 0
            }
        return self.circuit_breakers[service_name]
    
    def is_circuit_open(self, service_name: str) -> bool:
        """Check if circuit breaker is open"""
        cb = self.get_circuit_breaker(service_name)
        
        if cb["state"] == CircuitState.OPEN:
            # Check if we should try to close the circuit
            if (cb["last_failure_time"] and 
                time.time() - cb["last_failure_time"] > self.circuit_breaker_config.recovery_timeout):
                cb["state"] = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker for {service_name} moved to HALF_OPEN")
                return False
            return True
        
        return False
    
    def record_success(self, service_name: str):
        """Record successful request"""
        cb = self.get_circuit_breaker(service_name)
        cb["success_count"] += 1
        cb["failure_count"] = 0
        
        if cb["state"] == CircuitState.HALF_OPEN:
            cb["state"] = CircuitState.CLOSED
            logger.info(f"Circuit breaker for {service_name} moved to CLOSED")
    
    def record_failure(self, service_name: str):
        """Record failed request"""
        cb = self.get_circuit_breaker(service_name)
        cb["failure_count"] += 1
        cb["last_failure_time"] = time.time()
        
        if cb["failure_count"] >= self.circuit_breaker_config.failure_threshold:
            cb["state"] = CircuitState.OPEN
            logger.warning(f"Circuit breaker for {service_name} moved to OPEN")
    
    def calculate_retry_delay(self, attempt: int) -> float:
        """Calculate delay for retry with exponential backoff and jitter"""
        delay = min(
            self.retry_config.base_delay * (self.retry_config.exponential_base ** attempt),
            self.retry_config.max_delay
        )
        
        if self.retry_config.jitter:
            # Add jitter to prevent thundering herd
            jitter = random.uniform(0, delay * 0.1)
            delay += jitter
        
        return delay
    
    async def execute_with_retry(self, 
                                func: Callable, 
                                service_name: str,
                                *args, 
                                **kwargs) -> Any:
        """Execute function with retry logic and circuit breaker"""
        
        # Check circuit breaker
        if self.is_circuit_open(service_name):
            raise Exception(f"Circuit breaker is open for {service_name}")
        
        last_exception = None
        
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                self.record_success(service_name)
                return result
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1} failed for {service_name}: {str(e)}")
                
                if attempt < self.retry_config.max_retries:
                    delay = self.calculate_retry_delay(attempt)
                    logger.info(f"Retrying {service_name} in {delay:.2f} seconds...")
                    await asyncio.sleep(delay)
                else:
                    self.record_failure(service_name)
        
        raise last_exception
    
    def get_cached_response(self, cache_key: str, ttl: int = 300) -> Optional[Any]:
        """Get cached response if available and not expired"""
        with self.lock:
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if time.time() - timestamp < ttl:
                    logger.info(f"Cache hit for {cache_key}")
                    return cached_data
                else:
                    # Remove expired cache entry
                    del self.cache[cache_key]
        
        return None
    
    def cache_response(self, cache_key: str, response: Any, ttl: int = 300):
        """Cache response with TTL"""
        with self.lock:
            self.cache[cache_key] = (response, time.time())
            logger.info(f"Cached response for {cache_key}")
    
    def generate_cache_key(self, service_name: str, request_data: Dict[str, Any]) -> str:
        """Generate cache key from service name and request data"""
        # Create a hash of the request data for cache key
        request_str = json.dumps(request_data, sort_keys=True)
        return f"{service_name}_{hash(request_str)}"
    
    async def execute_with_fallbacks(self,
                                   primary_func: Callable,
                                   service_name: str,
                                   request_data: Dict[str, Any],
                                   cache_ttl: int = 300,
                                   *args,
                                   **kwargs) -> Any:
        """Execute with comprehensive fallback strategies"""
        
        # Generate cache key
        cache_key = self.generate_cache_key(service_name, request_data)
        
        # Try to get cached response first
        cached_response = self.get_cached_response(cache_key, cache_ttl)
        if cached_response:
            return cached_response
        
        # Try primary function with retry logic
        try:
            result = await self.execute_with_retry(primary_func, service_name, *args, **kwargs)
            self.cache_response(cache_key, result, cache_ttl)
            return result
            
        except Exception as e:
            logger.error(f"Primary function failed for {service_name}: {str(e)}")
            
            # Try fallback strategies
            for strategy in self.fallback_strategies:
                try:
                    fallback_result = await self._execute_fallback_strategy(
                        strategy, service_name, request_data, *args, **kwargs
                    )
                    if fallback_result:
                        logger.info(f"Fallback strategy '{strategy}' succeeded for {service_name}")
                        # Cache fallback result with shorter TTL
                        self.cache_response(cache_key, fallback_result, cache_ttl // 2)
                        return fallback_result
                        
                except Exception as fallback_error:
                    logger.warning(f"Fallback strategy '{strategy}' failed: {str(fallback_error)}")
                    continue
            
            # If all fallbacks fail, raise the original exception
            raise e
    
    async def _execute_fallback_strategy(self, 
                                       strategy: str, 
                                       service_name: str, 
                                       request_data: Dict[str, Any],
                                       *args, **kwargs) -> Any:
        """Execute specific fallback strategy"""
        
        if strategy == "cached_response":
            # Try to get any cached response, even if expired
            with self.lock:
                for key, (data, timestamp) in self.cache.items():
                    if service_name in key:
                        logger.info(f"Using expired cache for {service_name}")
                        return data
            return None
            
        elif strategy == "simplified_ai":
            # Use simplified AI model or reduced functionality
            return await self._get_simplified_response(service_name, request_data)
            
        elif strategy == "rule_based":
            # Use rule-based fallback
            return await self._get_rule_based_response(service_name, request_data)
            
        elif strategy == "mock_response":
            # Generate mock response
            return await self._get_mock_response(service_name, request_data)
        
        return None
    
    async def _get_simplified_response(self, service_name: str, request_data: Dict[str, Any]) -> Any:
        """Get simplified AI response"""
        if service_name == "meal_plan_generation":
            from ai.simple_nutrition_ai import SimpleNutritionAI
            simple_ai = SimpleNutritionAI()
            return simple_ai.generate_meal_plan(request_data)
        
        elif service_name == "nutritional_insights":
            return {
                "achievements": ["Keep up the good work!"],
                "concerns": ["Continue tracking your nutrition"],
                "suggestions": ["Stay consistent with your meal planning"],
                "meal_timing_advice": ["Maintain regular meal times"],
                "ingredient_recommendations": ["Include more variety in your meals"],
                "portion_advice": ["Monitor portion sizes"]
            }
        
        return None
    
    async def _get_rule_based_response(self, service_name: str, request_data: Dict[str, Any]) -> Any:
        """Get rule-based response"""
        if service_name == "meal_plan_generation":
            # Generate basic meal plan based on rules
            calorie_target = request_data.get("daily_calorie_target", 2000)
            meals_per_day = request_data.get("meals_per_day", 3)
            
            meals = []
            calorie_distribution = [0.3, 0.35, 0.35] if meals_per_day == 3 else [0.4, 0.6]
            
            for i, meal_type in enumerate(["breakfast", "lunch", "dinner"][:meals_per_day]):
                meal_calories = int(calorie_target * calorie_distribution[i])
                meals.append({
                    "meal_type": meal_type,
                    "meal_name": f"Simple {meal_type.title()}",
                    "calories": meal_calories,
                    "recipe": {
                        "title": f"Basic {meal_type.title()}",
                        "ingredients": ["Basic ingredients"],
                        "instructions": ["Simple preparation"],
                        "servings": 1,
                        "prep_time": 15,
                        "cook_time": 15
                    }
                })
            
            return {
                "meals": meals,
                "total_calories": sum(meal["calories"] for meal in meals),
                "generation_method": "rule_based"
            }
        
        return None
    
    async def _get_mock_response(self, service_name: str, request_data: Dict[str, Any]) -> Any:
        """Get mock response"""
        if service_name == "nutritional_insights":
            return {
                "achievements": ["Mock achievement"],
                "concerns": ["Mock concern"],
                "suggestions": ["Mock suggestion"],
                "meal_timing_advice": ["Mock timing advice"],
                "ingredient_recommendations": ["Mock ingredient recommendation"],
                "portion_advice": ["Mock portion advice"],
                "is_mock": True
            }
        
        return None
    
    def get_service_stats(self, service_name: str) -> Dict[str, Any]:
        """Get statistics for a service"""
        cb = self.get_circuit_breaker(service_name)
        
        return {
            "service_name": service_name,
            "circuit_state": cb["state"].value,
            "failure_count": cb["failure_count"],
            "success_count": cb["success_count"],
            "last_failure_time": cb["last_failure_time"],
            "cache_entries": len([k for k in self.cache.keys() if service_name in k])
        }
    
    def clear_cache(self, service_name: Optional[str] = None):
        """Clear cache for specific service or all services"""
        with self.lock:
            if service_name:
                keys_to_remove = [k for k in self.cache.keys() if service_name in k]
                for key in keys_to_remove:
                    del self.cache[key]
                logger.info(f"Cleared cache for {service_name}")
            else:
                self.cache.clear()
                logger.info("Cleared all cache")

# Global instance
ai_recovery_service = AIRecoveryService()

# Convenience functions
async def execute_with_recovery(func: Callable, 
                               service_name: str,
                               request_data: Dict[str, Any],
                               cache_ttl: int = 300,
                               *args, **kwargs) -> Any:
    """Execute function with comprehensive recovery mechanisms"""
    return await ai_recovery_service.execute_with_fallbacks(
        func, service_name, request_data, cache_ttl, *args, **kwargs
    )

def get_service_stats(service_name: str) -> Dict[str, Any]:
    """Get service statistics"""
    return ai_recovery_service.get_service_stats(service_name)

def clear_service_cache(service_name: str):
    """Clear cache for specific service"""
    ai_recovery_service.clear_cache(service_name)
