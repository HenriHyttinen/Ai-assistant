from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import time

from database import get_db
from models.user import User
from models.health_profile import HealthProfile
from models.activity_log import ActivityLog
from models.metrics_history import MetricsHistory
from schemas.user import (
    HealthProfileCreate,
    HealthProfileResponse,
    ActivityLogCreate,
    ActivityLogResponse,
    MetricsHistoryResponse
)
from auth.supabase_auth import get_current_user_supabase as get_current_user
from analytics.health_metrics import (
    calculate_bmi,
    calculate_wellness_score,
    get_bmi_category
)
from ai.insights import generate_health_insights, generate_weekly_summary

router = APIRouter(tags=["health profile"])

@router.post("/profile", response_model=HealthProfileResponse)
async def create_health_profile(
    profile_data: HealthProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if profile already exists
    existing_profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Health profile already exists"
        )
    
    # Create new profile
    db_profile = HealthProfile(
        user_id=current_user.id,
        **profile_data.dict()
    )
    
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    # Calculate initial metrics
    bmi = calculate_bmi(db_profile.weight, db_profile.height)
    wellness_score = calculate_wellness_score(profile_data.dict())
    
    # Store metrics history
    metrics = MetricsHistory(
        health_profile_id=db_profile.id,
        weight=db_profile.weight,
        bmi=bmi,
        wellness_score=wellness_score
    )
    
    db.add(metrics)
    db.commit()
    
    return db_profile

@router.get("/profile", response_model=HealthProfileResponse)
async def get_health_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health profile not found"
        )
    
    return profile

@router.put("/profile", response_model=HealthProfileResponse)
async def update_health_profile(
    profile_data: HealthProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health profile not found"
        )
    
    # Check if fitness goal is changing
    old_fitness_goal = profile.fitness_goal
    new_fitness_goal = profile_data.fitness_goal
    
    # Update profile
    for key, value in profile_data.dict().items():
        setattr(profile, key, value)
    
    db.commit()
    db.refresh(profile)
    
    # Clear irrelevant cached insights if fitness goal changed
    if old_fitness_goal != new_fitness_goal and new_fitness_goal:
        from services.cache import clear_irrelevant_cache
        clear_irrelevant_cache(current_user.id, new_fitness_goal)
    
    # Calculate new metrics
    bmi = calculate_bmi(profile.weight, profile.height)
    wellness_score = calculate_wellness_score(profile_data.dict())
    
    # Store metrics history
    metrics = MetricsHistory(
        health_profile_id=profile.id,
        weight=profile.weight,
        bmi=bmi,
        wellness_score=wellness_score
    )
    
    db.add(metrics)
    db.commit()
    
    return profile

@router.post("/activity", response_model=ActivityLogResponse)
async def log_activity(
    activity_data: ActivityLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    activity = ActivityLog(
        user_id=current_user.id,
        **activity_data.dict()
    )
    
    db.add(activity)
    db.commit()
    db.refresh(activity)
    
    return activity

@router.get("/activity", response_model=List[ActivityLogResponse])
async def get_activity_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    activities = db.query(ActivityLog).filter(
        ActivityLog.user_id == current_user.id
    ).order_by(ActivityLog.created_at.desc()).all()
    
    return activities

@router.get("/metrics", response_model=List[MetricsHistoryResponse])
async def get_metrics_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health profile not found"
        )
    
    metrics = db.query(MetricsHistory).filter(
        MetricsHistory.health_profile_id == profile.id
    ).order_by(MetricsHistory.recorded_at.desc()).all()
    
    return metrics

@router.get("/insights")
async def get_health_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get AI-powered health insights based on user data."""
    
    # Get user's health profile
    profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health profile not found"
        )
    
    # Get user settings for language preferences
    from models.user_settings import UserSettings
    user_settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    # Get user goals for context
    from models.goal import Goal
    user_goals = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.status == 'in_progress'
    ).all()
    
    # Prepare data for AI processing
    health_data = {
        "weight": profile.weight,
        "height": profile.height,
        "age": profile.age,
        "fitness_goal": profile.fitness_goal,
        "activity_level": profile.activity_level,
        "dietary_restrictions": profile.dietary_restrictions or [],
        "medical_conditions": [],  # Field not available in current model
        "target_weight": profile.target_weight,
        "target_body_fat": None  # Field not available in current model
    }
    
    # Get user settings for language
    settings_data = {}
    if user_settings:
        settings_data = {
            "language": user_settings.language,
            "units": user_settings.measurement_system
        }
    
    # Get goals data
    goals_data = []
    if user_goals:
        goals_data = [
            {
                "title": goal.title,
                "target": goal.target,
                "progress": goal.progress,
                "status": goal.status
            }
            for goal in user_goals
        ]
    
    # Generate AI insights
    try:
        from ai.insights import generate_health_insights
        ai_insights = generate_health_insights(health_data, settings_data, goals_data)
        
        # Calculate basic metrics
        bmi = calculate_bmi(profile.weight, profile.height)
        bmi_category = get_bmi_category(bmi)
        wellness_score = calculate_wellness_score(profile.__dict__)
        
        # Format insights for frontend
        insights_array = []
        if ai_insights.get("recommendations"):
            insights_array.extend(ai_insights["recommendations"])
        if ai_insights.get("strengths"):
            insights_array.extend([f"✅ {strength}" for strength in ai_insights["strengths"]])
        if ai_insights.get("improvements"):
            insights_array.extend([f"💡 {improvement}" for improvement in ai_insights["improvements"]])
        
        result = {
            "insights": insights_array,
            "status_analysis": ai_insights.get("status_analysis", ""),
            "metrics": {
                "bmi": bmi,
                "bmi_category": bmi_category,
                "wellness_score": wellness_score
            },
            "is_cached": False,
            "is_fallback": False,
            "cache_timestamp": time.time(),
            "ai_enabled": True
        }
        
        return result
        
    except Exception as e:
        # Fallback to basic insights if AI fails
        print(f"AI insights failed: {e}")
        
        # Calculate basic metrics
        bmi = calculate_bmi(profile.weight, profile.height)
        bmi_category = get_bmi_category(bmi)
        wellness_score = calculate_wellness_score(profile.__dict__)
        
        # Return fallback insights
        insights_array = [
            "📊 Track your daily activities to see progress over time",
            "🎯 Set specific, achievable health goals",
            "📈 Monitor your weight and measurements regularly",
            "✅ You're taking the first step towards better health!",
            "💡 Consider logging your meals and exercise for better insights"
        ]
        
        result = {
            "insights": insights_array,
            "status_analysis": "AI insights are temporarily unavailable. Here are some general health tips to get you started.",
            "metrics": {
                "bmi": bmi,
                "bmi_category": bmi_category,
                "wellness_score": wellness_score
            },
            "is_cached": False,
            "is_fallback": True,
            "cache_timestamp": time.time(),
            "ai_enabled": False,
            "error": str(e)
        }
        
        return result

@router.get("/insights/cache-stats")
async def get_cache_stats(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get cache statistics for monitoring"""
    from services.cache import get_cache_stats
    return get_cache_stats()

@router.delete("/insights/cache")
async def clear_user_cache(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Clear cached insights for the current user"""
    from services.cache import clear_user_cache
    clear_user_cache(current_user.id)
    return {"message": "User cache cleared successfully"}

@router.get("/weekly-summary")
async def get_weekly_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health profile not found"
        )
    
    # Get recent activity logs
    activities = db.query(ActivityLog).filter(
        ActivityLog.user_id == current_user.id
    ).order_by(ActivityLog.created_at.desc()).limit(7).all()
    
    # Generate weekly summary
    summary = generate_weekly_summary(
        profile.__dict__,
        [activity.__dict__ for activity in activities]
    )
    
    return summary 