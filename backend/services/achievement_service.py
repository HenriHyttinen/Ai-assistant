from sqlalchemy.orm import Session
from models.achievement import Achievement, UserAchievement
from models.user import User
from models.activity_log import ActivityLog
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class AchievementService:
    def __init__(self, db: Session):
        self.db = db
        self._cache = {}  # Simple in-memory cache for achievement checks
    
    def check_and_award_achievements(self, user_id: int) -> List[Dict]:
        """Check if user has unlocked any new achievements and award them"""
        new_achievements = []
        
        try:
            # Get all available achievements
            achievements = self.db.query(Achievement).filter(Achievement.is_active == True).all()
            
            for achievement in achievements:
                # Check if user already has this achievement
                existing = self.db.query(UserAchievement).filter(
                    UserAchievement.user_id == user_id,
                    UserAchievement.achievement_id == achievement.id
                ).first()
                
                if existing and existing.is_unlocked:
                    continue
                    
                # Check if achievement requirements are met
                if self._check_achievement_requirements(user_id, achievement):
                    # Award the achievement
                    if existing:
                        existing.is_unlocked = True
                        existing.unlocked_at = datetime.utcnow()
                    else:
                        user_achievement = UserAchievement(
                            user_id=user_id,
                            achievement_id=achievement.id,
                            is_unlocked=True,
                            progress=achievement.requirement_value
                        )
                        self.db.add(user_achievement)
                    
                    new_achievements.append({
                        "id": achievement.id,
                        "name": achievement.name,
                        "description": achievement.description,
                        "icon": achievement.icon,
                        "points": achievement.points,
                        "unlocked_at": datetime.utcnow().isoformat()
                    })
            
            if new_achievements:
                self.db.commit()
                
        except Exception as e:
            logger.error(f"Error in check_and_award_achievements: {e}")
            # Don't fail the entire request if achievement checking fails
            self.db.rollback()
        
        return new_achievements
    
    def _check_achievement_requirements(self, user_id: int, achievement: Achievement) -> bool:
        """Check if user meets the requirements for a specific achievement"""
        try:
            if achievement.requirement_type == "first_activity":
                activity_count = self.db.query(ActivityLog).filter(
                    ActivityLog.user_id == user_id
                ).count()
                return activity_count >= 1
                
            elif achievement.requirement_type == "activity_streak":
                # Check for consecutive days with activities
                return self._check_activity_streak(user_id, achievement.requirement_value)
                
            elif achievement.requirement_type == "total_activities":
                activity_count = self.db.query(ActivityLog).filter(
                    ActivityLog.user_id == user_id
                ).count()
                return activity_count >= achievement.requirement_value
                
            elif achievement.requirement_type == "total_duration":
                total_duration = self.db.query(ActivityLog).filter(
                    ActivityLog.user_id == user_id
                ).with_entities(ActivityLog.duration).all()
                total_minutes = sum(duration[0] for duration in total_duration)
                return total_minutes >= achievement.requirement_value
                
            elif achievement.requirement_type == "single_session_duration":
                max_duration = self.db.query(ActivityLog).filter(
                    ActivityLog.user_id == user_id
                ).with_entities(ActivityLog.duration).all()
                if max_duration:
                    max_minutes = max(duration[0] for duration in max_duration)
                    return max_minutes >= achievement.requirement_value
                return False
                
            elif achievement.requirement_type == "activity_variety":
                unique_activities = self.db.query(ActivityLog).filter(
                    ActivityLog.user_id == user_id
                ).with_entities(ActivityLog.activity_type).distinct().count()
                return unique_activities >= achievement.requirement_value
                
            elif achievement.requirement_type == "weekly_consistency":
                return self._check_weekly_consistency(user_id, achievement.requirement_value)
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking achievement requirements: {e}")
            return False
    
    def _check_activity_streak(self, user_id: int, required_days: int) -> bool:
        """Check if user has activities on consecutive days"""
        today = datetime.utcnow().date()
        start_date = today - timedelta(days=required_days - 1)
        
        # Get all activity dates for the user in the required period
        activity_dates = self.db.query(ActivityLog.created_at).filter(
            ActivityLog.user_id == user_id,
            ActivityLog.created_at >= start_date,
            ActivityLog.created_at < today + timedelta(days=1)
        ).all()
        
        # Convert to date set for faster lookup
        activity_date_set = {activity[0].date() for activity in activity_dates}
        
        # Check consecutive days from today backwards
        streak_count = 0
        for i in range(required_days):
            check_date = today - timedelta(days=i)
            if check_date in activity_date_set:
                streak_count += 1
            else:
                break
                
        return streak_count >= required_days
    
    def _check_weekly_consistency(self, user_id: int, required_weeks: int) -> bool:
        """Check if user has been consistent for required weeks"""
        today = datetime.utcnow().date()
        start_date = today - timedelta(days=(required_weeks * 7) + 6)
        
        # Get all activities for the user in the required period
        activities = self.db.query(ActivityLog.created_at).filter(
            ActivityLog.user_id == user_id,
            ActivityLog.created_at >= start_date,
            ActivityLog.created_at <= today
        ).all()
        
        # Group activities by week
        weekly_counts = {}
        for activity in activities:
            activity_date = activity[0].date()
            # Calculate week start (Monday)
            week_start = activity_date - timedelta(days=activity_date.weekday())
            if week_start not in weekly_counts:
                weekly_counts[week_start] = 0
            weekly_counts[week_start] += 1
        
        # Check consecutive weeks from current week backwards
        consistent_weeks = 0
        current_week_start = today - timedelta(days=today.weekday())
        
        for week in range(required_weeks):
            check_week = current_week_start - timedelta(weeks=week)
            if check_week in weekly_counts and weekly_counts[check_week] >= 3:
                consistent_weeks += 1
            else:
                break
                
        return consistent_weeks >= required_weeks
    
    def get_user_achievements(self, user_id: int) -> List[Dict]:
        """Get all achievements for a user"""
        user_achievements = self.db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).all()
        
        achievements = []
        for user_achievement in user_achievements:
            achievements.append({
                "id": user_achievement.achievement.id,
                "name": user_achievement.achievement.name,
                "description": user_achievement.achievement.description,
                "icon": user_achievement.achievement.icon,
                "points": user_achievement.achievement.points,
                "unlocked_at": user_achievement.unlocked_at.isoformat() if user_achievement.unlocked_at else None,
                "is_unlocked": user_achievement.is_unlocked,
                "progress": user_achievement.progress,
                "requirement_value": user_achievement.achievement.requirement_value
            })
        
        return achievements
    
    def get_available_achievements(self, user_id: int) -> List[Dict]:
        """Get all available achievements with user's progress"""
        all_achievements = self.db.query(Achievement).filter(Achievement.is_active == True).all()
        user_achievements = {
            ua.achievement_id: ua for ua in self.db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id
            ).all()
        }
        
        achievements = []
        for achievement in all_achievements:
            user_achievement = user_achievements.get(achievement.id)
            achievements.append({
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "icon": achievement.icon,
                "points": achievement.points,
                "category": achievement.category,
                "is_unlocked": user_achievement.is_unlocked if user_achievement else False,
                "progress": user_achievement.progress if user_achievement else 0,
                "requirement_value": achievement.requirement_value,
                "requirement_type": achievement.requirement_type
            })
        
        return achievements
