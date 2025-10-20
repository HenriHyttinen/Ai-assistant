#!/usr/bin/env python3
"""
Simple script to create achievements in the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models.achievement import Achievement

def create_achievements():
    db = SessionLocal()
    try:
        # Check if achievements already exist
        existing_count = db.query(Achievement).count()
        if existing_count > 0:
            print(f"Achievements already exist ({existing_count} found). Skipping creation.")
            return
        
        # Create achievements using ORM
        achievements_data = [
            {
                "name": "First Steps",
                "description": "Log your first activity",
                "icon": "🥾",
                "category": "activity",
                "requirement_type": "first_activity",
                "requirement_value": 1,
                "points": 10,
                "is_active": True
            },
            {
                "name": "Getting Started",
                "description": "Log 5 activities",
                "icon": "🏃‍♂️",
                "category": "activity",
                "requirement_type": "total_activities",
                "requirement_value": 5,
                "points": 25,
                "is_active": True
            },
            {
                "name": "Active Lifestyle",
                "description": "Log 25 activities",
                "icon": "💪",
                "category": "activity",
                "requirement_type": "total_activities",
                "requirement_value": 25,
                "points": 50,
                "is_active": True
            },
            {
                "name": "Activity Master",
                "description": "Log 100 activities",
                "icon": "🏆",
                "category": "activity",
                "requirement_type": "total_activities",
                "requirement_value": 100,
                "points": 100,
                "is_active": True
            },
            {
                "name": "Time Investment",
                "description": "Log 100 minutes of total activity time",
                "icon": "⏱️",
                "category": "duration",
                "requirement_type": "total_duration",
                "requirement_value": 100,
                "points": 20,
                "is_active": True
            },
            {
                "name": "Endurance Builder",
                "description": "Log 500 minutes of total activity time",
                "icon": "🔥",
                "category": "duration",
                "requirement_type": "total_duration",
                "requirement_value": 500,
                "points": 50,
                "is_active": True
            },
            {
                "name": "Time Champion",
                "description": "Log 100+ minutes in a single session",
                "icon": "⏰",
                "category": "duration",
                "requirement_type": "single_session_duration",
                "requirement_value": 100,
                "points": 75,
                "is_active": True
            },
            {
                "name": "Consistent Logger",
                "description": "Log activities for 3 consecutive days",
                "icon": "📅",
                "category": "consistency",
                "requirement_type": "activity_streak",
                "requirement_value": 3,
                "points": 30,
                "is_active": True
            },
            {
                "name": "Week Warrior",
                "description": "Log activities for 7 consecutive days",
                "icon": "🗓️",
                "category": "consistency",
                "requirement_type": "activity_streak",
                "requirement_value": 7,
                "points": 75,
                "is_active": True
            },
            {
                "name": "Monthly Master",
                "description": "Log activities for 30 consecutive days",
                "icon": "📆",
                "category": "consistency",
                "requirement_type": "activity_streak",
                "requirement_value": 30,
                "points": 200,
                "is_active": True
            },
            {
                "name": "Explorer",
                "description": "Try 3 different activity types",
                "icon": "🎯",
                "category": "variety",
                "requirement_type": "activity_variety",
                "requirement_value": 3,
                "points": 40,
                "is_active": True
            },
            {
                "name": "Diverse Athlete",
                "description": "Try 5 different activity types",
                "icon": "🌟",
                "category": "variety",
                "requirement_type": "activity_variety",
                "requirement_value": 5,
                "points": 75,
                "is_active": True
            },
            {
                "name": "Activity Explorer",
                "description": "Try 10 different activity types",
                "icon": "🗺️",
                "category": "variety",
                "requirement_type": "activity_variety",
                "requirement_value": 10,
                "points": 150,
                "is_active": True
            },
            {
                "name": "Weekly Warrior",
                "description": "Be consistent for 2 weeks",
                "icon": "⚔️",
                "category": "weekly_consistency",
                "requirement_type": "weekly_consistency",
                "requirement_value": 2,
                "points": 60,
                "is_active": True
            },
            {
                "name": "Monthly Champion",
                "description": "Be consistent for 4 weeks",
                "icon": "👑",
                "category": "weekly_consistency",
                "requirement_type": "weekly_consistency",
                "requirement_value": 4,
                "points": 150,
                "is_active": True
            }
        ]
        
        # Create achievement objects
        for achievement_data in achievements_data:
            achievement = Achievement(**achievement_data)
            db.add(achievement)
        
        db.commit()
        print("Successfully created 15 achievements!")
        
    except Exception as e:
        print(f"Error creating achievements: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_achievements()
