"""
Advanced Nutrition Analytics API Routes
Provides endpoints for comprehensive nutrition analytics and insights
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from database import get_db
from models.user import User
from auth.supabase_auth import get_current_user_supabase as get_current_user
from services.nutrition_analytics_service import NutritionAnalyticsService

router = APIRouter(prefix="/nutrition-analytics", tags=["nutrition-analytics"])

@router.get("/trends")
def get_nutrition_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get nutrition trends over specified days"""
    try:
        service = NutritionAnalyticsService()
        return service.get_nutrition_trends(db, current_user.id, days)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get nutrition trends: {str(e)}"
        )

@router.get("/insights")
def get_nutrition_insights(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered nutrition insights and recommendations"""
    try:
        service = NutritionAnalyticsService()
        return service.get_nutrition_insights(db, current_user.id, days)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get nutrition insights: {str(e)}"
        )

@router.get("/meal-patterns")
def get_meal_pattern_analysis(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze meal patterns and timing"""
    try:
        service = NutritionAnalyticsService()
        return service.get_meal_pattern_analysis(db, current_user.id, days)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get meal pattern analysis: {str(e)}"
        )

@router.get("/goals-progress")
def get_nutrition_goals_progress(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get progress toward nutrition goals"""
    try:
        service = NutritionAnalyticsService()
        return service.get_nutrition_goals_progress(db, current_user.id, days)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get nutrition goals progress: {str(e)}"
        )

@router.get("/dashboard")
def get_analytics_dashboard(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive analytics dashboard data"""
    try:
        service = NutritionAnalyticsService()
        
        # Get all analytics data
        trends = service.get_nutrition_trends(db, current_user.id, days)
        insights = service.get_nutrition_insights(db, current_user.id, days)
        meal_patterns = service.get_meal_pattern_analysis(db, current_user.id, days)
        goals_progress = service.get_nutrition_goals_progress(db, current_user.id, days)
        
        return {
            'trends': trends,
            'insights': insights,
            'meal_patterns': meal_patterns,
            'goals_progress': goals_progress,
            'period_days': days,
            'generated_at': datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics dashboard: {str(e)}"
        )

@router.get("/export")
def export_analytics_data(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    format: str = Query("json", regex="^(json|csv)$", description="Export format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export analytics data in specified format"""
    try:
        service = NutritionAnalyticsService()
        
        if format == "json":
            return service.get_analytics_dashboard(db, current_user.id, days)
        elif format == "csv":
            # This would generate CSV data
            # For now, return JSON with CSV structure info
            return {
                "message": "CSV export not yet implemented",
                "suggestion": "Use JSON format for now"
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export analytics data: {str(e)}"
        )
