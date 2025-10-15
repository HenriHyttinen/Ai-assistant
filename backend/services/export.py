import json
import csv
from io import StringIO
from typing import List, Dict, Any
from datetime import datetime, timedelta
from models.user import User, HealthProfile, ActivityLog, MetricsHistory
from sqlalchemy.orm import Session

class DataExporter:
    def __init__(self, db: Session):
        self.db = db
    
    def export_user_data(self, user: User, format: str = 'json') -> str:
        """Export all user data in specified format."""
        data = {
            'user': {
                'email': user.email,
                'created_at': user.created_at.isoformat(),
                'is_verified': user.is_verified,
                'two_factor_enabled': user.two_factor_enabled
            },
            'health_profile': self._get_health_profile_data(user.health_profile),
            'activity_logs': self._get_activity_logs_data(user.activity_logs),
            'metrics_history': self._get_metrics_history_data(user.health_profile.metrics_history)
        }
        
        if format == 'json':
            return json.dumps(data, indent=2)
        elif format == 'csv':
            return self._convert_to_csv(data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _get_health_profile_data(self, profile: HealthProfile) -> Dict[str, Any]:
        """Get health profile data."""
        if not profile:
            return {}
        
        return {
            'age': profile.age,
            'gender': profile.gender,
            'height': profile.height,
            'weight': profile.weight,
            'occupation_type': profile.occupation_type,
            'activity_level': profile.activity_level,
            'fitness_goal': profile.fitness_goal,
            'target_weight': profile.target_weight,
            'target_activity_level': profile.target_activity_level,
            'preferred_exercise_time': profile.preferred_exercise_time,
            'preferred_exercise_environment': profile.preferred_exercise_environment,
            'weekly_activity_frequency': profile.weekly_activity_frequency,
            'exercise_types': profile.exercise_types,
            'average_session_duration': profile.average_session_duration,
            'fitness_level': profile.fitness_level,
            'endurance_level': profile.endurance_level,
            'strength_indicators': profile.strength_indicators
        }
    
    def _get_activity_logs_data(self, logs: List[ActivityLog]) -> List[Dict[str, Any]]:
        """Get activity logs data."""
        return [{
            'activity_type': log.activity_type,
            'duration': log.duration,
            'intensity': log.intensity,
            'notes': log.notes,
            'created_at': log.created_at.isoformat()
        } for log in logs]
    
    def _get_metrics_history_data(self, history: List[MetricsHistory]) -> List[Dict[str, Any]]:
        """Get metrics history data."""
        return [{
            'weight': metric.weight,
            'bmi': metric.bmi,
            'wellness_score': metric.wellness_score,
            'recorded_at': metric.recorded_at.isoformat()
        } for metric in history]
    
    def _convert_to_csv(self, data: Dict[str, Any]) -> str:
        """Convert data to CSV format."""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write user data
        writer.writerow(['User Information'])
        writer.writerow(['Field', 'Value'])
        for key, value in data['user'].items():
            writer.writerow([key, value])
        writer.writerow([])
        
        # Write health profile
        writer.writerow(['Health Profile'])
        writer.writerow(['Field', 'Value'])
        for key, value in data['health_profile'].items():
            writer.writerow([key, value])
        writer.writerow([])
        
        # Write activity logs
        writer.writerow(['Activity Logs'])
        if data['activity_logs']:
            writer.writerow(data['activity_logs'][0].keys())
            for log in data['activity_logs']:
                writer.writerow(log.values())
        writer.writerow([])
        
        # Write metrics history
        writer.writerow(['Metrics History'])
        if data['metrics_history']:
            writer.writerow(data['metrics_history'][0].keys())
            for metric in data['metrics_history']:
                writer.writerow(metric.values())
        
        return output.getvalue()

def generate_health_report(
    db: Session,
    user_id: int,
    days: int = 30
) -> Dict[str, Any]:
    """Generate a comprehensive health report for a user."""
    # Get user's health profile
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == user_id).first()
    if not profile:
        return None
    
    # Get metrics history
    start_date = datetime.utcnow() - timedelta(days=days)
    metrics = db.query(MetricsHistory)\
        .filter(
            MetricsHistory.health_profile_id == profile.id,
            MetricsHistory.recorded_at >= start_date
        )\
        .order_by(MetricsHistory.recorded_at.asc())\
        .all()
    
    # Get activity logs
    activities = db.query(ActivityLog)\
        .filter(
            ActivityLog.user_id == user_id,
            ActivityLog.created_at >= start_date
        )\
        .order_by(ActivityLog.created_at.asc())\
        .all()
    
    # Calculate trends and statistics
    weight_trend = [m.weight for m in metrics]
    bmi_trend = [m.bmi for m in metrics]
    wellness_score_trend = [m.wellness_score for m in metrics]
    
    activity_summary = {
        "total_duration": sum(a.duration for a in activities),
        "activity_count": len(activities),
        "average_duration": sum(a.duration for a in activities) / len(activities) if activities else 0,
        "activity_types": list(set(a.activity_type for a in activities))
    }
    
    # Generate report
    report = {
        "user_id": user_id,
        "generated_at": datetime.utcnow().isoformat(),
        "period": {
            "start": start_date.isoformat(),
            "end": datetime.utcnow().isoformat(),
            "days": days
        },
        "profile": {
            "age": profile.age,
            "gender": profile.gender,
            "height": profile.height,
            "weight": profile.weight,
            "activity_level": profile.activity_level,
            "fitness_goal": profile.fitness_goal,
            "target_weight": profile.target_weight
        },
        "metrics": {
            "current": {
                "weight": weight_trend[-1] if weight_trend else None,
                "bmi": bmi_trend[-1] if bmi_trend else None,
                "wellness_score": wellness_score_trend[-1] if wellness_score_trend else None
            },
            "trends": {
                "weight": weight_trend,
                "bmi": bmi_trend,
                "wellness_score": wellness_score_trend
            }
        },
        "activities": {
            "summary": activity_summary,
            "logs": [
                {
                    "date": a.created_at.isoformat(),
                    "type": a.activity_type,
                    "duration": a.duration,
                    "intensity": a.intensity,
                    "notes": a.notes
                }
                for a in activities
            ]
        }
    }
    
    return report

def export_to_json(
    db: Session,
    user_id: int,
    days: int = 30
) -> str:
    """Export user's health data to JSON format."""
    report = generate_health_report(db, user_id, days)
    if not report:
        return None
    return json.dumps(report, indent=2)

def export_to_csv(
    db: Session,
    user_id: int,
    days: int = 30
) -> str:
    """Export user's health data to CSV format."""
    report = generate_health_report(db, user_id, days)
    if not report:
        return None
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Date",
        "Weight (kg)",
        "BMI",
        "Wellness Score",
        "Activity Type",
        "Activity Duration (min)",
        "Activity Intensity",
        "Notes"
    ])
    
    # Create a date-indexed dictionary for metrics
    metrics_by_date = {
        m.recorded_at.date(): m
        for m in db.query(MetricsHistory)\
            .filter(
                MetricsHistory.health_profile_id == report["profile"]["id"],
                MetricsHistory.recorded_at >= datetime.fromisoformat(report["period"]["start"])
            )
    }
    
    # Create a date-indexed dictionary for activities
    activities_by_date = {
        a.created_at.date(): a
        for a in db.query(ActivityLog)\
            .filter(
                ActivityLog.user_id == user_id,
                ActivityLog.created_at >= datetime.fromisoformat(report["period"]["start"])
            )
    }
    
    # Write data rows
    start_date = datetime.fromisoformat(report["period"]["start"]).date()
    end_date = datetime.fromisoformat(report["period"]["end"]).date()
    current_date = start_date
    
    while current_date <= end_date:
        metrics = metrics_by_date.get(current_date)
        activity = activities_by_date.get(current_date)
        
        writer.writerow([
            current_date.isoformat(),
            metrics.weight if metrics else "",
            metrics.bmi if metrics else "",
            metrics.wellness_score if metrics else "",
            activity.activity_type if activity else "",
            activity.duration if activity else "",
            activity.intensity if activity else "",
            activity.notes if activity else ""
        ])
        
        current_date += timedelta(days=1)
    
    return output.getvalue() 