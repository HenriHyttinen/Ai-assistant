from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
import csv
import io
from datetime import datetime, timedelta

from database import get_db
from models.user import User, HealthProfile, ActivityLog, MetricsHistory
# DataConsent import removed due to model issues
from routes.auth import get_current_user

router = APIRouter(prefix="/export", tags=["data export"])

@router.get("/health-data")
async def export_health_data(
    format: str = "json",  # json, csv
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all health data for the current user."""
    
    # Get user's health profile
    health_profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    if not health_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No health profile found"
        )
    
    # Get metrics history
    metrics_history = db.query(MetricsHistory).filter(
        MetricsHistory.health_profile_id == health_profile.id
    ).order_by(MetricsHistory.recorded_at.desc()).all()
    
    # Get activity logs
    activity_logs = db.query(ActivityLog).filter(
        ActivityLog.user_id == current_user.id
    ).order_by(ActivityLog.created_at.desc()).all()
    
    # Consent data removed due to DataConsent model issues
    consent_data = None
    
    # Prepare export data
    export_data = {
        "export_info": {
            "exported_at": datetime.utcnow().isoformat(),
            "user_id": current_user.id,
            "user_email": current_user.email,
            "export_format": format,
            "data_version": "1.0"
        },
        "user_profile": {
            "email": current_user.email,
            "is_verified": current_user.is_verified,
            "two_factor_enabled": current_user.two_factor_enabled,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None
        },
        "health_profile": {
            "age": health_profile.age,
            "gender": health_profile.gender,
            "height": health_profile.height,
            "weight": health_profile.weight,
            "activity_level": health_profile.activity_level,
            "fitness_goal": health_profile.fitness_goal,
            "target_weight": health_profile.target_weight,
            "target_activity_level": health_profile.target_activity_level,
            "weekly_activity_frequency": health_profile.weekly_activity_frequency,
            "exercise_types": health_profile.exercise_types,
            "average_session_duration": health_profile.average_session_duration,
            "fitness_level": health_profile.fitness_level,
            "endurance_level": health_profile.endurance_level,
            "current_endurance_minutes": health_profile.current_endurance_minutes,
            "pushup_count": health_profile.pushup_count,
            "squat_count": health_profile.squat_count,
            "dietary_preferences": health_profile.dietary_preferences,
            "dietary_restrictions": health_profile.dietary_restrictions,
            "created_at": health_profile.created_at.isoformat() if health_profile.created_at else None,
            "updated_at": health_profile.updated_at.isoformat() if health_profile.updated_at else None
        },
        "metrics_history": [
            {
                "recorded_at": metric.recorded_at.isoformat(),
                "weight": metric.weight,
                "bmi": metric.bmi,
                "wellness_score": metric.wellness_score,
                "created_at": metric.created_at.isoformat() if metric.created_at else None
            }
            for metric in metrics_history
        ],
        "activity_logs": [
            {
                "activity_type": log.activity_type,
                "duration_minutes": log.duration_minutes,
                "intensity": log.intensity,
                "notes": log.notes,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in activity_logs
        ],
        "consent_data": {
            "consent_given": consent_data.consent_given if consent_data else False,
            "consent_date": consent_data.consent_date.isoformat() if consent_data and consent_data.consent_date else None,
            "privacy_policy_version": consent_data.privacy_policy_version if consent_data else None,
            "data_collection": consent_data.data_collection if consent_data else False,
            "data_processing": consent_data.data_processing if consent_data else False,
            "data_sharing": consent_data.data_sharing if consent_data else False,
            "ai_insights": consent_data.ai_insights if consent_data else False,
            "email_notifications": consent_data.email_notifications if consent_data else False,
            "analytics_tracking": consent_data.analytics_tracking if consent_data else False,
            "health_metrics": consent_data.health_metrics if consent_data else False,
            "activity_data": consent_data.activity_data if consent_data else False,
            "personal_info": consent_data.personal_info if consent_data else False,
            "usage_patterns": consent_data.usage_patterns if consent_data else False
        }
    }
    
    if format.lower() == "json":
        # Return JSON data
        return export_data
    elif format.lower() == "csv":
        # Convert to CSV format
        csv_data = convert_to_csv(export_data)
        
        # Create CSV file in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write CSV data
        for row in csv_data:
            writer.writerow(row)
        
        # Return CSV file
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=health_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format. Supported formats: json, csv"
        )

def convert_to_csv(data: Dict[str, Any]) -> List[List[str]]:
    """Convert export data to CSV format."""
    csv_rows = []
    
    # Add headers
    csv_rows.append(["Data Type", "Field", "Value", "Timestamp"])
    
    # Export info
    for key, value in data["export_info"].items():
        csv_rows.append(["Export Info", key, str(value), ""])
    
    # User profile
    for key, value in data["user_profile"].items():
        csv_rows.append(["User Profile", key, str(value), ""])
    
    # Health profile
    for key, value in data["health_profile"].items():
        csv_rows.append(["Health Profile", key, str(value), ""])
    
    # Metrics history
    for metric in data["metrics_history"]:
        for key, value in metric.items():
            if key != "created_at":
                csv_rows.append(["Metrics History", key, str(value), metric.get("recorded_at", "")])
    
    # Activity logs
    for log in data["activity_logs"]:
        for key, value in log.items():
            if key != "created_at":
                csv_rows.append(["Activity Log", key, str(value), log.get("created_at", "")])
    
    # Consent data
    for key, value in data["consent_data"].items():
        csv_rows.append(["Consent Data", key, str(value), ""])
    
    return csv_rows

@router.get("/metrics-history")
async def export_metrics_history(
    days: int = 30,
    format: str = "json",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export metrics history for the specified number of days."""
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get health profile
    health_profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    if not health_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No health profile found"
        )
    
    # Get metrics history for the date range
    metrics_history = db.query(MetricsHistory).filter(
        MetricsHistory.health_profile_id == health_profile.id,
        MetricsHistory.recorded_at >= start_date,
        MetricsHistory.recorded_at <= end_date
    ).order_by(MetricsHistory.recorded_at.desc()).all()
    
    # Prepare export data
    export_data = {
        "export_info": {
            "exported_at": datetime.utcnow().isoformat(),
            "user_id": current_user.id,
            "date_range": f"{start_date.date()} to {end_date.date()}",
            "days_requested": days,
            "records_found": len(metrics_history)
        },
        "metrics_history": [
            {
                "recorded_at": metric.recorded_at.isoformat(),
                "weight": metric.weight,
                "bmi": metric.bmi,
                "wellness_score": metric.wellness_score,
                "created_at": metric.created_at.isoformat() if metric.created_at else None
            }
            for metric in metrics_history
        ]
    }
    
    if format.lower() == "json":
        return export_data
    elif format.lower() == "csv":
        # Convert to CSV
        csv_data = []
        csv_data.append(["Recorded At", "Weight (kg)", "BMI", "Wellness Score", "Created At"])
        
        for metric in metrics_history:
            csv_data.append([
                metric.recorded_at.isoformat(),
                str(metric.weight),
                str(metric.bmi),
                str(metric.wellness_score),
                metric.created_at.isoformat() if metric.created_at else ""
            ])
        
        # Create CSV file in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        for row in csv_data:
            writer.writerow(row)
        
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=metrics_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format. Supported formats: json, csv"
        )