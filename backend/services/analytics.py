from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models.user import User
from models.health_profile import HealthProfile
from models.activity_log import ActivityLog
from models.metrics_history import MetricsHistory

def calculate_weekly_summary(user_id: int, db: Session) -> Dict[str, Any]:
    """Calculate weekly summary for a user."""
    # Get user's health profile
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == user_id).first()
    if not profile:
        return None
    
    # Get metrics for the last week
    start_date = datetime.utcnow() - timedelta(days=7)
    metrics = db.query(MetricsHistory)\
        .filter(
            MetricsHistory.health_profile_id == profile.id,
            MetricsHistory.recorded_at >= start_date
        )\
        .order_by(MetricsHistory.recorded_at.desc())\
        .all()
    
    # Get activity logs for the last week
    activities = db.query(ActivityLog)\
        .filter(
            ActivityLog.user_id == user_id,
            ActivityLog.created_at >= start_date
        )\
        .order_by(ActivityLog.created_at.desc())\
        .all()
    
    # Calculate summary
    summary = {
        "period": {
            "start": start_date.isoformat(),
            "end": datetime.utcnow().isoformat()
        },
        "metrics": {
            "current_weight": metrics[0].weight if metrics else None,
            "weight_change": metrics[0].weight - metrics[-1].weight if len(metrics) > 1 else 0,
            "current_bmi": metrics[0].bmi if metrics else None,
            "current_wellness_score": metrics[0].wellness_score if metrics else None
        },
        "activities": {
            "total_duration": sum(a.duration for a in activities),
            "activity_count": len(activities),
            "average_duration": round(sum(a.duration for a in activities) / len(activities), 1) if activities else 0,
            "activity_types": list(set(a.activity_type for a in activities))
        }
    }
    
    return summary

def check_goal_achievements(user_id: int, db: Session) -> List[Dict[str, Any]]:
    """Check if user has achieved any goals."""
    achievements = []
    
    # Get user's health profile
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == user_id).first()
    if not profile:
        return achievements
    
    # Get latest metrics
    latest_metrics = db.query(MetricsHistory)\
        .filter(MetricsHistory.health_profile_id == profile.id)\
        .order_by(MetricsHistory.recorded_at.desc())\
        .first()
    
    if not latest_metrics:
        return achievements
    
    # Check weight goal
    if profile.target_weight and abs(latest_metrics.weight - profile.target_weight) <= 0.5:
        achievements.append({
            "type": "weight_goal",
            "description": f"Reached target weight of {profile.target_weight}kg",
            "achieved_at": datetime.utcnow().isoformat()
        })
    
    # Check activity goal
    if profile.target_activity_level:
        activities = db.query(ActivityLog)\
            .filter(
                ActivityLog.user_id == user_id,
                ActivityLog.created_at >= datetime.utcnow() - timedelta(days=7)
            )\
            .all()
        
        if len(activities) >= profile.weekly_activity_frequency:
            achievements.append({
                "type": "activity_goal",
                "description": f"Achieved weekly activity goal of {profile.weekly_activity_frequency} sessions",
                "achieved_at": datetime.utcnow().isoformat()
            })
    
    return achievements 