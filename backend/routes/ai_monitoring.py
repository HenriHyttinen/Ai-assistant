"""
AI Monitoring and Recovery Management API

Provides endpoints for monitoring AI service health, recovery mechanisms,
and managing circuit breakers and caches.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from services.ai_recovery_service import ai_recovery_service, get_service_stats, clear_service_cache
from services.cache import get_cache_stats
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-monitoring", tags=["AI Monitoring"])

@router.get("/health")
def get_ai_health_status() -> Dict[str, Any]:
    """Get overall AI service health status"""
    try:
        # Get stats for all AI services
        services = ["openai_api", "meal_plan_generation", "nutritional_insights", "health_insights"]
        service_stats = {}
        
        for service in services:
            try:
                service_stats[service] = get_service_stats(service)
            except Exception as e:
                logger.warning(f"Could not get stats for {service}: {e}")
                service_stats[service] = {"error": str(e)}
        
        # Get cache stats
        cache_stats = get_cache_stats()
        
        # Determine overall health
        healthy_services = 0
        total_services = len(services)
        
        for service, stats in service_stats.items():
            if "error" not in stats and stats.get("circuit_state") != "open":
                healthy_services += 1
        
        overall_health = "healthy" if healthy_services == total_services else "degraded" if healthy_services > 0 else "unhealthy"
        
        return {
            "overall_health": overall_health,
            "healthy_services": healthy_services,
            "total_services": total_services,
            "service_stats": service_stats,
            "cache_stats": cache_stats,
            "timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp
        }
        
    except Exception as e:
        logger.error(f"Error getting AI health status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting AI health status: {str(e)}"
        )

@router.get("/services/{service_name}/stats")
def get_service_statistics(service_name: str) -> Dict[str, Any]:
    """Get detailed statistics for a specific AI service"""
    try:
        stats = get_service_stats(service_name)
        return stats
        
    except Exception as e:
        logger.error(f"Error getting stats for service {service_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting stats for service {service_name}: {str(e)}"
        )

@router.post("/services/{service_name}/reset-circuit")
def reset_circuit_breaker(service_name: str) -> Dict[str, Any]:
    """Reset circuit breaker for a specific service"""
    try:
        # Reset circuit breaker state
        if service_name in ai_recovery_service.circuit_breakers:
            cb = ai_recovery_service.circuit_breakers[service_name]
            cb["state"] = "closed"
            cb["failure_count"] = 0
            cb["success_count"] = 0
            cb["last_failure_time"] = None
            
            logger.info(f"Circuit breaker reset for service {service_name}")
            
            return {
                "message": f"Circuit breaker reset for service {service_name}",
                "service_name": service_name,
                "new_state": "closed"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service {service_name} not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting circuit breaker for {service_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting circuit breaker: {str(e)}"
        )

@router.post("/services/{service_name}/clear-cache")
def clear_service_cache_endpoint(service_name: str) -> Dict[str, Any]:
    """Clear cache for a specific service"""
    try:
        clear_service_cache(service_name)
        
        logger.info(f"Cache cleared for service {service_name}")
        
        return {
            "message": f"Cache cleared for service {service_name}",
            "service_name": service_name
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache for {service_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing cache: {str(e)}"
        )

@router.get("/cache/stats")
def get_cache_statistics() -> Dict[str, Any]:
    """Get cache statistics"""
    try:
        stats = get_cache_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting cache stats: {str(e)}"
        )

@router.post("/cache/clear")
def clear_all_cache() -> Dict[str, Any]:
    """Clear all AI service caches"""
    try:
        ai_recovery_service.clear_cache()
        
        logger.info("All AI service caches cleared")
        
        return {
            "message": "All AI service caches cleared"
        }
        
    except Exception as e:
        logger.error(f"Error clearing all caches: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing caches: {str(e)}"
        )

@router.get("/recovery-config")
def get_recovery_configuration() -> Dict[str, Any]:
    """Get current recovery configuration"""
    try:
        return {
            "retry_config": {
                "max_retries": ai_recovery_service.retry_config.max_retries,
                "base_delay": ai_recovery_service.retry_config.base_delay,
                "max_delay": ai_recovery_service.retry_config.max_delay,
                "exponential_base": ai_recovery_service.retry_config.exponential_base,
                "jitter": ai_recovery_service.retry_config.jitter
            },
            "circuit_breaker_config": {
                "failure_threshold": ai_recovery_service.circuit_breaker_config.failure_threshold,
                "recovery_timeout": ai_recovery_service.circuit_breaker_config.recovery_timeout
            },
            "fallback_strategies": ai_recovery_service.fallback_strategies,
            "alternative_models": ai_recovery_service.alternative_models
        }
        
    except Exception as e:
        logger.error(f"Error getting recovery configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting recovery configuration: {str(e)}"
        )



