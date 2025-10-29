from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from datetime import datetime, timedelta

from database import get_db
from services import health
from auth.supabase_auth import get_current_user_supabase as get_current_user
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
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create a new activity log entry for the current user."""
    try:
        db_activity = health.create_activity_log(
            db=db,
            user_id=current_user.id,
            **activity.dict()
        )
        
        # Check for new achievements after logging activity
        try:
            from services.achievement_service import AchievementService
            achievement_service = AchievementService(db)
            new_achievements = achievement_service.check_and_award_achievements(current_user.id)
            if new_achievements:
                print(f"User {current_user.id} unlocked {len(new_achievements)} new achievements!")
        except Exception as e:
            # Don't fail the activity logging if achievement checking fails
            print(f"Error checking achievements: {e}")
        
        return ActivityLogResponse.model_validate(db_activity)
    
    except ValueError as e:
        # Handle duplicate activity error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/profiles/me/activities", response_model=List[ActivityLogResponse])
def get_my_activity_logs(
    days: int = 7,
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get the current user's activity logs."""
    logs = health.get_activity_logs(db, current_user.id, days, sort_order)
    return [ActivityLogResponse.model_validate(log) for log in logs]

@router.get("/profiles/me/weekly-summary")
def get_weekly_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get weekly health summary for the current user."""
    from services.analytics import calculate_weekly_summary
    summary = calculate_weekly_summary(current_user.id, db)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health profile not found"
        )
    return summary

@router.get("/profiles/me/monthly-summary")
def get_monthly_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get monthly health summary for the current user."""
    from services.analytics import calculate_monthly_summary
    summary = calculate_monthly_summary(current_user.id, db)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health profile not found"
        )
    return summary

@router.get("/profiles/me/analytics", response_model=HealthAnalytics)
def get_my_health_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
    
    latest_metrics = db.query(health.MetricsHistory)\
        .filter(health.MetricsHistory.health_profile_id == profile.id)\
        .order_by(health.MetricsHistory.recorded_at.desc())\
        .first()
    
    if not latest_metrics:
        # Create initial metrics if none exist
        from analytics.health_metrics import calculate_bmi, calculate_wellness_score
        
        # Only calculate metrics if we have the required data
        bmi = None
        wellness_score = None
        
        if profile.weight and profile.height:
            bmi = calculate_bmi(profile.weight, profile.height)
            wellness_score = calculate_wellness_score({
                'weight': profile.weight,
                'height': profile.height,
                'activity_level': profile.activity_level,
                'weekly_activity_frequency': profile.weekly_activity_frequency,
                'exercise_types': profile.exercise_types,
                'average_session_duration': profile.average_session_duration,
                'fitness_level': profile.fitness_level
            })
        
        # Create metrics history record
        latest_metrics = health.MetricsHistory(
            health_profile_id=profile.id,
            weight=profile.weight,
            bmi=bmi,
            wellness_score=wellness_score
        )
        
        db.add(latest_metrics)
        db.commit()
        db.refresh(latest_metrics)
    
    metrics_history = health.get_metrics_history(db, profile.id, days=30)
    
    # Filter out None values and create trend data with timestamps
    weight_trend = []
    bmi_trend = []
    wellness_score_trend = []
    weight_trend_timestamps = []
    
    for m in metrics_history:
        if m.weight is not None:
            weight_trend.append(m.weight)
            weight_trend_timestamps.append(m.recorded_at.isoformat())
        if m.bmi is not None:
            bmi_trend.append(m.bmi)
        if m.wellness_score is not None:
            wellness_score_trend.append(m.wellness_score)
    
    # Reverse the trends to show chronological order (oldest first)
    # get_metrics_history returns newest first, but graph needs oldest first
    weight_trend = weight_trend[::-1]
    bmi_trend = bmi_trend[::-1]
    wellness_score_trend = wellness_score_trend[::-1]
    weight_trend_timestamps = weight_trend_timestamps[::-1]
    
    # If no history, use current values (only if they exist)
    if not weight_trend:
        weight_trend = [profile.weight] if profile.weight else []
        weight_trend_timestamps = [datetime.utcnow().isoformat()] if profile.weight else []
        bmi_trend = [latest_metrics.bmi] if latest_metrics.bmi else []
        wellness_score_trend = [latest_metrics.wellness_score] if latest_metrics.wellness_score else []
    else:
        # Ensure the latest weight from profile is included in the trend if it's newer
        if profile.weight and (not weight_trend or profile.weight != weight_trend[-1]):
            # Add current profile weight as the latest entry if it's different from the last trend entry
            weight_trend.append(profile.weight)
            weight_trend_timestamps.append(datetime.utcnow().isoformat())
    
    # Get activity summary
    activity_logs = health.get_activity_logs(db, current_user.id, days=7)
    activity_summary = {
        "total_duration": sum(log.duration for log in activity_logs),
        "activity_count": len(activity_logs),
        "average_duration": round(sum(log.duration for log in activity_logs) / len(activity_logs), 1) if activity_logs else 0,
        "activity_types": list(set(log.activity_type for log in activity_logs))
    }
    
    # Calculate progress towards goal
    if profile.target_weight and profile.weight and weight_trend:
        if profile.fitness_goal == "muscle_gain":
            # For weight gain: progress is how much we've gained towards the target
            starting_weight = min(weight_trend)  # Use lowest weight as starting point
            total_to_gain = profile.target_weight - starting_weight
            gained_so_far = profile.weight - starting_weight
            if total_to_gain > 0:
                progress = min(100, max(0, (gained_so_far / total_to_gain) * 100))
            else:
                progress = 0
        elif profile.fitness_goal == "weight_loss":
            # For weight loss: progress is how much we've lost towards the target
            # Use the highest weight in the trend as the true starting point
            starting_weight = max(weight_trend)  # Highest weight as starting point
            total_to_lose = starting_weight - profile.target_weight
            lost_so_far = starting_weight - profile.weight
            if total_to_lose > 0:
                progress = min(100, max(0, (lost_so_far / total_to_lose) * 100))
            else:
                progress = 0
        else:
            # For other goals, use simple distance calculation
            weight_diff = abs(profile.target_weight - profile.weight)
            initial_diff = abs(profile.target_weight - weight_trend[0]) if weight_trend else weight_diff
            if initial_diff > 0:
                progress = min(100, max(0, (1 - (weight_diff / initial_diff)) * 100))
            else:
                progress = 100 if weight_diff == 0 else 0
    elif profile.target_weight and profile.weight:
        # If we have target and current weight but no trend data, show journey progress
        if profile.fitness_goal == "weight_loss":
            # For weight loss: show how much of the journey is left
            total_to_lose = profile.weight - profile.target_weight
            if total_to_lose > 0:
                # Calculate progress as how much of the total journey is completed
                # Since we're at the starting point, show 0% progress
                progress = 0
            else:
                # If we're at or below target, show 100% progress
                progress = 100
        elif profile.fitness_goal == "muscle_gain":
            # For weight gain: show how much of the journey is left
            total_to_gain = profile.target_weight - profile.weight
            if total_to_gain > 0:
                # Calculate progress as how much of the total journey is completed
                # Since we're at the starting point, show 0% progress
                progress = 0
            else:
                # If we're at or above target, show 100% progress
                progress = 100
        else:
            # For other goals, use simple distance calculation
            weight_diff = abs(profile.target_weight - profile.weight)
            if weight_diff == 0:
                progress = 100
            else:
                progress = 0  # Can't calculate progress without trend data
    else:
        progress = 0
    
    return HealthAnalytics(
        current_bmi=latest_metrics.bmi,
        current_wellness_score=latest_metrics.wellness_score,
        weight_trend=weight_trend,
        bmi_trend=bmi_trend,
        wellness_score_trend=wellness_score_trend,
        weight_trend_timestamps=weight_trend_timestamps,
        activity_summary=activity_summary,
        progress_towards_goal=progress
    ) 