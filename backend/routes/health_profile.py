from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import time

from database import get_db
from models.user import User, HealthProfile, ActivityLog, MetricsHistory
from schemas.user import (
    HealthProfileCreate,
    HealthProfileResponse,
    ActivityLogCreate,
    ActivityLogResponse,
    MetricsHistoryResponse
)
from routes.auth import get_current_user
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
    profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health profile not found"
        )
    
    # Get user settings for data normalization first
    try:
        from services.settings import get_user_settings
        user_settings = get_user_settings(db, current_user.id)
        settings_dict = user_settings.__dict__ if user_settings else {}
    except Exception as e:
        # If settings service fails, use default settings
        print(f"Settings service error: {e}")
        settings_dict = {"language": "en", "measurement_system": "metric"}
    
    # Get user goals for goal-specific recommendations
    from models.goal import Goal
    user_goals = db.query(Goal).filter(Goal.user_id == current_user.id).all()
    goals_data = [{
        'title': goal.title,
        'target': goal.target,
        'type': goal.type,
        'status': goal.status,
        'progress': goal.progress,
        'deadline': goal.deadline.isoformat() if goal.deadline else None
    } for goal in user_goals]
    
    # Check enhanced cache first
    from services.cache import get_cached_insights, cache_insights, get_fallback_insights
    language = settings_dict.get('language', 'en')
    cached_insights = get_cached_insights(
        current_user.id, 
        str(profile.updated_at), 
        language, 
        goals_data
    )
    
    if cached_insights:
        return cached_insights
    
    # Try to generate fresh AI insights
    try:
        insights_data = generate_health_insights(profile.__dict__, settings_dict, goals_data)
        is_fallback = False
    except Exception as e:
        print(f"AI service error: {e}")
        # Use fallback insights when AI service is unavailable
        fitness_goal = profile.fitness_goal or "general_fitness"
        insights_data = get_fallback_insights(current_user.id, language, fitness_goal)
        is_fallback = True
    
    # Format insights as an array of strings for frontend
    insights_array = []
    if insights_data:
        # Add status analysis
        if insights_data.get('status_analysis'):
            insights_array.append(insights_data['status_analysis'])
        
        # Add recommendations
        if insights_data.get('recommendations'):
            insights_array.extend(insights_data['recommendations'])
        
        # Add strengths
        if insights_data.get('strengths'):
            for strength in insights_data['strengths']:
                insights_array.append(f"✅ {strength}")
        
        # Add improvements
        if insights_data.get('improvements'):
            for improvement in insights_data['improvements']:
                insights_array.append(f"💡 {improvement}")
    else:
        # Fallback insights when no data is available
        insights_array = [
            "Welcome to your health journey! Start by logging your weight and activities.",
            "Set up your health profile to get personalized insights.",
            "Track your daily activities to see your progress over time.",
            "✅ You're taking the first step towards better health!",
            "💡 Consider setting specific, achievable health goals"
        ]
    
    # Add calculated metrics
    bmi = calculate_bmi(profile.weight, profile.height)
    bmi_category = get_bmi_category(bmi)
    wellness_score = calculate_wellness_score(profile.__dict__)
    
    result = {
        "insights": insights_array,
        "metrics": {
            "bmi": bmi,
            "bmi_category": bmi_category,
            "wellness_score": wellness_score
        },
        "is_cached": False,
        "is_fallback": is_fallback,
        "cache_timestamp": time.time()
    }
    
    # Cache the result
    cache_insights(
        current_user.id,
        str(profile.updated_at),
        language,
        result,
        goals_data,
        is_fallback
    )
    
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