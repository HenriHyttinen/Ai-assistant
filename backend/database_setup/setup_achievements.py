#!/usr/bin/env python3
"""
Simple script to setup achievements table and populate it
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
from sqlalchemy import text

def setup_achievements():
    db = SessionLocal()
    try:
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            icon VARCHAR(50) NOT NULL,
            category VARCHAR(50) NOT NULL,
            requirement_type VARCHAR(50) NOT NULL,
            requirement_value INTEGER NOT NULL,
            points INTEGER DEFAULT 10,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        db.execute(text(create_table_sql))
        
        # Create user_achievements table if it doesn't exist
        create_user_achievements_table_sql = """
        CREATE TABLE IF NOT EXISTS user_achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            achievement_id INTEGER NOT NULL,
            unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            progress INTEGER DEFAULT 0,
            is_unlocked BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (achievement_id) REFERENCES achievements (id)
        );
        """
        
        db.execute(text(create_user_achievements_table_sql))
        db.commit()
        
        # Check if achievements already exist
        result = db.execute(text("SELECT COUNT(*) FROM achievements")).scalar()
        if result > 0:
            print(f"Achievements already exist ({result} found). Skipping creation.")
            return
        
        # Create achievements
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
        print("Successfully created achievements table and populated it with 15 achievements!")
        
    except Exception as e:
        print(f"Error setting up achievements: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_achievements()
