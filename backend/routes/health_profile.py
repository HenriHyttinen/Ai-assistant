from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

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
    
    # Update profile
    for key, value in profile_data.dict().items():
        setattr(profile, key, value)
    
    db.commit()
    db.refresh(profile)
    
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
    
    # Get user settings for data normalization
    from services.settings import get_user_settings
    user_settings = get_user_settings(db, current_user.id)
    settings_dict = user_settings.__dict__ if user_settings else {}
    
    # Generate AI insights with normalized data
    insights = generate_health_insights(profile.__dict__, settings_dict)
    
    # Add calculated metrics
    bmi = calculate_bmi(profile.weight, profile.height)
    bmi_category = get_bmi_category(bmi)
    wellness_score = calculate_wellness_score(profile.__dict__)
    
    return {
        "insights": insights,
        "metrics": {
            "bmi": bmi,
            "bmi_category": bmi_category,
            "wellness_score": wellness_score
        }
    }

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