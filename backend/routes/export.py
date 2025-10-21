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
                "wellness_score": metric.wellness_score
            }
            for metric in metrics_history
        ],
        "activity_logs": [
            {
                "activity_type": log.activity_type,
                "duration": log.duration,
                "intensity": log.intensity,
                "notes": log.notes,
                "performed_at": log.performed_at.isoformat() if log.performed_at else None,
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
            headers={
                "Content-Disposition": f"attachment; filename=health_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format. Supported formats: json, csv"
        )

@router.get("/activities")
async def export_activities(
    days: int = 30,
    format: str = "csv",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export activity logs for the current user."""
    
    # Get activity logs for the specified time range
    start_date = datetime.utcnow() - timedelta(days=days)
    activity_logs = db.query(ActivityLog).filter(
        ActivityLog.user_id == current_user.id,
        ActivityLog.created_at >= start_date
    ).order_by(ActivityLog.created_at.desc()).all()
    
    if not activity_logs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No activity logs found for the specified time range"
        )
    
    # Prepare export data
    export_data = {
        "export_info": {
            "exported_at": datetime.utcnow().isoformat(),
            "user_id": current_user.id,
            "user_email": current_user.email,
            "export_format": format,
            "time_range_days": days,
            "activity_count": len(activity_logs)
        },
        "activities": [
            {
                "id": log.id,
                "activity_type": log.activity_type,
                "duration": log.duration,
                "intensity": log.intensity,
                "notes": log.notes,
                "performed_at": log.performed_at.isoformat() if log.performed_at else None,
                "created_at": log.created_at.isoformat()
            }
            for log in activity_logs
        ]
    }
    
    if format.lower() == "json":
        # Return JSON data
        return export_data
    elif format.lower() == "csv":
        # Convert to CSV format
        csv_data = convert_activities_to_csv(export_data)
        
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
            headers={
                "Content-Disposition": f"attachment; filename=activities_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format. Supported formats: json, csv"
        )

def convert_activities_to_csv(data: Dict[str, Any]) -> List[List[str]]:
    """Convert activities export data to CSV format."""
    csv_rows = []
    
    # Add export info
    csv_rows.append(["Export Information"])
    csv_rows.append(["Exported At", data["export_info"]["exported_at"]])
    csv_rows.append(["User Email", data["export_info"]["user_email"]])
    csv_rows.append(["Time Range (days)", str(data["export_info"]["time_range_days"])])
    csv_rows.append(["Activity Count", str(data["export_info"]["activity_count"])])
    csv_rows.append([])  # Empty row
    
    # Add activities header
    csv_rows.append(["Activities"])
    csv_rows.append([
        "ID", "Activity Type", "Duration (min)", "Intensity", 
        "Notes", "Performed At", "Created At"
    ])
    
    # Add activities data
    for activity in data["activities"]:
        csv_rows.append([
            str(activity["id"]),
            activity["activity_type"],
            str(activity["duration"]),
            activity["intensity"] or "",
            activity["notes"] or "",
            activity["performed_at"] or "",
            activity["created_at"]
        ])
    
    return csv_rows

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

def convert_summary_to_csv(data: Dict[str, Any], summary_type: str) -> List[List[str]]:
    """Convert summary export data to CSV format."""
    csv_rows = []
    
    # Add export info
    csv_rows.append([f"{summary_type} Summary Export Information"])
    csv_rows.append(["Exported At", data["export_info"]["exported_at"]])
    csv_rows.append(["User Email", data["export_info"]["user_email"]])
    csv_rows.append(["Summary Type", data["export_info"]["summary_type"]])
    csv_rows.append([])  # Empty row
    
    # Get the summary data
    summary_key = f"{summary_type.lower()}_summary"
    summary = data[summary_key]
    
    # Add period information
    if "period" in summary:
        csv_rows.append([f"{summary_type} Period"])
        csv_rows.append(["Start Date", summary["period"]["start"]])
        csv_rows.append(["End Date", summary["period"]["end"]])
        if "type" in summary["period"]:
            csv_rows.append(["Period Type", summary["period"]["type"]])
        csv_rows.append([])  # Empty row
    
    # Add metrics
    if "metrics" in summary:
        csv_rows.append([f"{summary_type} Metrics"])
        for key, value in summary["metrics"].items():
            if value is not None:
                csv_rows.append([key.replace("_", " ").title(), str(value)])
        csv_rows.append([])  # Empty row
    
    # Add activities
    if "activities" in summary:
        csv_rows.append([f"{summary_type} Activities"])
        for key, value in summary["activities"].items():
            if isinstance(value, list):
                csv_rows.append([key.replace("_", " ").title(), ", ".join(map(str, value))])
            else:
                csv_rows.append([key.replace("_", " ").title(), str(value)])
        csv_rows.append([])  # Empty row
    
    # Add goals progress
    if "goals_progress" in summary:
        csv_rows.append([f"{summary_type} Goals Progress"])
        for goal_type, goal_data in summary["goals_progress"].items():
            csv_rows.append([f"{goal_type.replace('_', ' ').title()} Goal"])
            for key, value in goal_data.items():
                csv_rows.append([f"  {key.replace('_', ' ').title()}", str(value)])
        csv_rows.append([])  # Empty row
    
    return csv_rows

@router.get("/weekly-summary")
async def export_weekly_summary(
    format: str = "json",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export weekly health summary for the current user."""
    
    # Get weekly summary using the existing endpoint logic
    from services.analytics import calculate_weekly_summary
    summary = calculate_weekly_summary(current_user.id, db)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No health profile found or no data available"
        )
    
    # Prepare export data
    export_data = {
        "export_info": {
            "exported_at": datetime.utcnow().isoformat(),
            "user_id": current_user.id,
            "user_email": current_user.email,
            "export_format": format,
            "summary_type": "weekly"
        },
        "weekly_summary": summary
    }
    
    if format.lower() == "json":
        return export_data
    elif format.lower() == "csv":
        # Convert to CSV format
        csv_data = convert_summary_to_csv(export_data, "Weekly")
        
        # Create CSV file in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        for row in csv_data:
            writer.writerow(row)
        
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=weekly_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format. Supported formats: json, csv"
        )

@router.get("/monthly-summary")
async def export_monthly_summary(
    format: str = "json",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export monthly health summary for the current user."""
    
    # Get monthly summary using the existing endpoint logic
    from services.analytics import calculate_monthly_summary
    summary = calculate_monthly_summary(current_user.id, db)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No health profile found or no data available"
        )
    
    # Prepare export data
    export_data = {
        "export_info": {
            "exported_at": datetime.utcnow().isoformat(),
            "user_id": current_user.id,
            "user_email": current_user.email,
            "export_format": format,
            "summary_type": "monthly"
        },
        "monthly_summary": summary
    }
    
    if format.lower() == "json":
        return export_data
    elif format.lower() == "csv":
        # Convert to CSV format
        csv_data = convert_summary_to_csv(export_data, "Monthly")
        
        # Create CSV file in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        for row in csv_data:
            writer.writerow(row)
        
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=monthly_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format. Supported formats: json, csv"
        )

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