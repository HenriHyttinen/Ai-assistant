#!/usr/bin/env python3
"""
Simple script to create achievements in the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
from sqlalchemy import text

def create_achievements():
    db = SessionLocal()
    try:
        # Check if achievements table exists
        result = db.execute(text("SELECT COUNT(*) FROM achievements")).scalar()
        if result > 0:
            print(f"Achievements already exist ({result} found). Skipping creation.")
            return
        
        # Create achievements directly with SQL
        achievements_sql = """
        INSERT INTO achievements (name, description, icon, category, requirement_type, requirement_value, points, is_active, created_at) VALUES
        ('First Steps', 'Log your first activity', '🥾', 'activity', 'first_activity', 1, 10, 1, datetime('now')),
        ('Getting Started', 'Log 5 activities', '🏃‍♂️', 'activity', 'total_activities', 5, 25, 1, datetime('now')),
        ('Active Lifestyle', 'Log 25 activities', '💪', 'activity', 'total_activities', 25, 50, 1, datetime('now')),
        ('Activity Master', 'Log 100 activities', '🏆', 'activity', 'total_activities', 100, 100, 1, datetime('now')),
        ('Time Investment', 'Log 100 minutes of total activity time', '⏱️', 'duration', 'total_duration', 100, 20, 1, datetime('now')),
        ('Endurance Builder', 'Log 500 minutes of total activity time', '🔥', 'duration', 'total_duration', 500, 50, 1, datetime('now')),
        ('Time Champion', 'Log 100+ minutes in a single session', '⏰', 'duration', 'single_session_duration', 100, 75, 1, datetime('now')),
        ('Consistent Logger', 'Log activities for 3 consecutive days', '📅', 'consistency', 'activity_streak', 3, 30, 1, datetime('now')),
        ('Week Warrior', 'Log activities for 7 consecutive days', '🗓️', 'consistency', 'activity_streak', 7, 75, 1, datetime('now')),
        ('Monthly Master', 'Log activities for 30 consecutive days', '📆', 'consistency', 'activity_streak', 30, 200, 1, datetime('now')),
        ('Explorer', 'Try 3 different activity types', '🎯', 'variety', 'activity_variety', 3, 40, 1, datetime('now')),
        ('Diverse Athlete', 'Try 5 different activity types', '🌟', 'variety', 'activity_variety', 5, 75, 1, datetime('now')),
        ('Activity Explorer', 'Try 10 different activity types', '🗺️', 'variety', 'activity_variety', 10, 150, 1, datetime('now')),
        ('Weekly Warrior', 'Be consistent for 2 weeks', '⚔️', 'weekly_consistency', 'weekly_consistency', 2, 60, 1, datetime('now')),
        ('Monthly Champion', 'Be consistent for 4 weeks', '👑', 'weekly_consistency', 'weekly_consistency', 4, 150, 1, datetime('now'));
        """
        
        db.execute(text(achievements_sql))
        db.commit()
        print("Successfully created 15 achievements!")
        
    except Exception as e:
        print(f"Error creating achievements: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_achievements()
