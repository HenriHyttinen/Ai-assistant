from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from datetime import datetime, timedelta

from database import get_db
from services import auth, health
from schemas.health import (
    HealthProfileCreate,
    HealthProfileUpdate,
    HealthProfileResponse,
    MetricsHistoryResponse,
    ActivityLogCreate,
    ActivityLogResponse,
    HealthAnalytics
)
from models.user import User

router = APIRouter()

@router.post("/profiles", response_model=HealthProfileResponse)
def create_health_profile(
    profile: HealthProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
) -> Any:
    """Create a new health profile for the current user."""
    # Check if user already has a health profile
    existing_profile = db.query(health.HealthProfile).filter(
        health.HealthProfile.user_id == current_user.id
    ).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a health profile"
        )
    
    db_profile = health.create_health_profile(db=db, user_id=current_user.id, **profile.dict())
    return HealthProfileResponse.model_validate(db_profile)

@router.get("/profiles/me", response_model=HealthProfileResponse)
def get_my_health_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
) -> Any:
    """Get the current user's health profile."""
    profile = db.query(health.HealthProfile).filter(
        health.HealthProfile.user_id == current_user.id
    ).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health profile not found"
        )
    return HealthProfileResponse.model_validate(profile)

@router.put("/profiles/me", response_model=HealthProfileResponse)
def update_my_health_profile(
    profile_update: HealthProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
) -> Any:
    """Update the current user's health profile."""
    profile = db.query(health.HealthProfile).filter(
        health.HealthProfile.user_id == current_user.id
    ).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health profile not found"
        )
    
    # Update profile
    updated_profile = health.update_health_profile(
        db=db,
        profile_id=profile.id,
        **profile_update.dict(exclude_unset=True)
    )
    
    # If weight or height was updated, create new metrics history entry
    if profile_update.weight or profile_update.height:
        weight = profile_update.weight or profile.weight
        height = profile_update.height or profile.height
        if weight and height:
            bmi = health.calculate_bmi(weight, height)
            wellness_score = health.calculate_wellness_score(
                profile_update.activity_level or profile.activity_level or "sedentary",
                profile_update.weekly_activity_frequency or profile.weekly_activity_frequency or 0,
                profile_update.endurance_level or profile.endurance_level or 1,
                bmi
            )
            health.create_metrics_history(db, profile.id, weight, bmi, wellness_score)
    
    return HealthProfileResponse.model_validate(updated_profile)

@router.get("/profiles/me/metrics", response_model=List[MetricsHistoryResponse])
def get_my_metrics_history(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
) -> Any:
    """Get the current user's metrics history."""
    profile = db.query(health.HealthProfile).filter(
        health.HealthProfile.user_id == current_user.id
    ).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health profile not found"
        )
    
    metrics = health.get_metrics_history(db, profile.id, days)
    return [MetricsHistoryResponse.model_validate(m) for m in metrics]

@router.post("/profiles/me/activities", response_model=ActivityLogResponse)
def create_activity_log(
    activity: ActivityLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
) -> Any:
    """Create a new activity log entry for the current user."""
    db_activity = health.create_activity_log(
        db=db,
        user_id=current_user.id,
        **activity.dict()
    )
    return ActivityLogResponse.model_validate(db_activity)

@router.get("/profiles/me/activities", response_model=List[ActivityLogResponse])
def get_my_activity_logs(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
) -> Any:
    """Get the current user's activity logs."""
    logs = health.get_activity_logs(db, current_user.id, days)
    return [ActivityLogResponse.model_validate(log) for log in logs]

@router.get("/profiles/me/analytics", response_model=HealthAnalytics)
def get_my_health_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
) -> Any:
    """Get comprehensive health analytics for the current user."""
    profile = db.query(health.HealthProfile).filter(
        health.HealthProfile.user_id == current_user.id
    ).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health profile not found"
        )
    
    # Get latest metrics
    latest_metrics = db.query(health.MetricsHistory)\
        .filter(health.MetricsHistory.health_profile_id == profile.id)\
        .order_by(health.MetricsHistory.recorded_at.desc())\
        .first()
    
    if not latest_metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No metrics history found"
        )
    
    # Get metrics trends
    metrics_history = health.get_metrics_history(db, profile.id, days=30)
    weight_trend = [m.weight for m in metrics_history]
    bmi_trend = [m.bmi for m in metrics_history]
    wellness_score_trend = [m.wellness_score for m in metrics_history]
    
    # Get activity summary
    activity_logs = health.get_activity_logs(db, current_user.id, days=7)
    activity_summary = {
        "total_duration": sum(log.duration for log in activity_logs),
        "activity_count": len(activity_logs),
        "average_duration": sum(log.duration for log in activity_logs) / len(activity_logs) if activity_logs else 0,
        "activity_types": list(set(log.activity_type for log in activity_logs))
    }
    
    # Calculate progress towards goal
    if profile.target_weight and profile.weight:
        weight_diff = abs(profile.target_weight - profile.weight)
        initial_diff = abs(profile.target_weight - weight_trend[-1]) if weight_trend else weight_diff
        progress = (1 - (weight_diff / initial_diff)) * 100 if initial_diff > 0 else 100
    else:
        progress = 0
    
    return HealthAnalytics(
        current_bmi=latest_metrics.bmi,
        current_wellness_score=latest_metrics.wellness_score,
        weight_trend=weight_trend,
        bmi_trend=bmi_trend,
        wellness_score_trend=wellness_score_trend,
        activity_summary=activity_summary,
        progress_towards_goal=progress
    ) 