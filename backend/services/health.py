from sqlalchemy.orm import Session
from models.health_profile import HealthProfile
from models.metrics_history import MetricsHistory
from models.activity_log import ActivityLog
from typing import List, Optional
from datetime import datetime, timedelta

def calculate_bmi(weight: float, height: float) -> float:
    """Calculate BMI from weight (kg) and height (cm)."""
    height_m = height / 100
    return weight / (height_m * height_m)

def calculate_wellness_score(
    activity_level: str,
    weekly_activity_frequency: int,
    endurance_level: int,
    bmi: float
) -> float:
    """Calculate a wellness score based on various health metrics."""
    # Normalize BMI (18.5-24.9 is optimal)
    bmi_score = max(0, 100 - abs(bmi - 21.7) * 10)
    
    # Activity level score (0-100)
    activity_scores = {
        "sedentary": 20,
        "lightly_active": 40,
        "moderately_active": 60,
        "very_active": 80,
        "extremely_active": 100
    }
    activity_score = activity_scores.get(activity_level.lower(), 0)
    
    # Weekly activity frequency score (0-100)
    frequency_score = min(100, weekly_activity_frequency * 10)
    
    # Endurance level score (0-100)
    endurance_score = endurance_level * 10
    
    # Calculate final score (weighted average)
    return (bmi_score * 0.3 + activity_score * 0.3 + frequency_score * 0.2 + endurance_score * 0.2)

def create_health_profile(
    db: Session,
    user_id: int,
    age: Optional[int] = None,
    gender: Optional[str] = None,
    height: Optional[float] = None,
    weight: Optional[float] = None,
    occupation_type: Optional[str] = None,
    activity_level: Optional[str] = None,
    fitness_goal: Optional[str] = None,
    target_weight: Optional[float] = None,
    target_activity_level: Optional[str] = None,
    preferred_exercise_time: Optional[str] = None,
    preferred_exercise_environment: Optional[str] = None,
    weekly_activity_frequency: Optional[int] = None,
    exercise_types: Optional[str] = None,
    average_session_duration: Optional[str] = None,
    fitness_level: Optional[str] = None,
    endurance_level: Optional[int] = None,
    strength_indicators: Optional[str] = None,
    dietary_preferences: Optional[str] = None,
    dietary_restrictions: Optional[str] = None,
    meal_preferences: Optional[str] = None,
    current_endurance_minutes: Optional[int] = None,
    pushup_count: Optional[int] = None,
    squat_count: Optional[int] = None
) -> HealthProfile:
    """Create a new health profile for a user."""
    db_profile = HealthProfile(
        user_id=user_id,
        age=age,
        gender=gender,
        height=height,
        weight=weight,
        occupation_type=occupation_type,
        activity_level=activity_level,
        fitness_goal=fitness_goal,
        target_weight=target_weight,
        target_activity_level=target_activity_level,
        preferred_exercise_time=preferred_exercise_time,
        preferred_exercise_environment=preferred_exercise_environment,
        weekly_activity_frequency=weekly_activity_frequency,
        exercise_types=exercise_types,
        average_session_duration=average_session_duration,
        fitness_level=fitness_level,
        endurance_level=endurance_level,
        strength_indicators=strength_indicators,
        dietary_preferences=dietary_preferences,
        dietary_restrictions=dietary_restrictions,
        meal_preferences=meal_preferences,
        current_endurance_minutes=current_endurance_minutes,
        pushup_count=pushup_count,
        squat_count=squat_count
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    # Create initial metrics history entry if weight and height are provided
    if weight and height:
        bmi = calculate_bmi(weight, height)
        wellness_score = calculate_wellness_score(
            activity_level or "sedentary",
            weekly_activity_frequency or 0,
            endurance_level or 1,
            bmi
        )
        create_metrics_history(db, db_profile.id, weight, bmi, wellness_score)
    
    return db_profile

def update_health_profile(
    db: Session,
    profile_id: int,
    **kwargs
) -> HealthProfile:
    """Update a health profile with new data."""
    db_profile = db.query(HealthProfile).filter(HealthProfile.id == profile_id).first()
    if not db_profile:
        return None
    
    for key, value in kwargs.items():
        if hasattr(db_profile, key):
            setattr(db_profile, key, value)
    
    db.commit()
    db.refresh(db_profile)
    return db_profile

def create_metrics_history(
    db: Session,
    health_profile_id: int,
    weight: float,
    bmi: float,
    wellness_score: float
) -> MetricsHistory:
    """Create a new metrics history entry."""
    db_metrics = MetricsHistory(
        health_profile_id=health_profile_id,
        weight=weight,
        bmi=bmi,
        wellness_score=wellness_score
    )
    db.add(db_metrics)
    db.commit()
    db.refresh(db_metrics)
    return db_metrics

def get_metrics_history(
    db: Session,
    health_profile_id: int,
    days: int = 30
) -> List[MetricsHistory]:
    """Get metrics history for a health profile within the specified time range."""
    start_date = datetime.utcnow() - timedelta(days=days)
    return db.query(MetricsHistory)\
        .filter(
            MetricsHistory.health_profile_id == health_profile_id,
            MetricsHistory.recorded_at >= start_date
        )\
        .order_by(MetricsHistory.recorded_at.desc())\
        .all()

def create_activity_log(
    db: Session,
    user_id: int,
    activity_type: str,
    duration: int,
    intensity: Optional[str] = None,
    notes: Optional[str] = None
) -> ActivityLog:
    """Create a new activity log entry."""
    db_activity = ActivityLog(
        user_id=user_id,
        activity_type=activity_type,
        duration=duration,
        intensity=intensity,
        notes=notes
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

def get_activity_logs(
    db: Session,
    user_id: int,
    days: int = 7
) -> List[ActivityLog]:
    """Get activity logs for a user within the specified time range."""
    start_date = datetime.utcnow() - timedelta(days=days)
    return db.query(ActivityLog)\
        .filter(
            ActivityLog.user_id == user_id,
            ActivityLog.created_at >= start_date
        )\
        .order_by(ActivityLog.created_at.desc())\
        .all() 