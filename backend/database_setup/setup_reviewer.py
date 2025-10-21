#!/usr/bin/env python3
"""
Quick setup script for reviewers to get the database ready
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
from sqlalchemy import text

def setup_reviewer_database():
    """Set up database for reviewer"""
    print("Setting up database for reviewer...")
    
    # Create all tables using raw SQL to avoid ORM issues
    with engine.connect() as conn:
        # Create user_settings table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                email_notifications BOOLEAN DEFAULT 1,
                weekly_reports BOOLEAN DEFAULT 1,
                ai_insights BOOLEAN DEFAULT 1,
                data_sharing BOOLEAN DEFAULT 0,
                measurement_system VARCHAR(10) DEFAULT 'metric',
                language VARCHAR(5) DEFAULT 'en',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """))
        
        # Create achievements table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                icon VARCHAR(10),
                category VARCHAR(50),
                requirement_type VARCHAR(50),
                requirement_value INTEGER,
                points INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create user_achievements table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_id INTEGER NOT NULL,
                earned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (achievement_id) REFERENCES achievements (id)
            )
        """))
        
        conn.commit()
    
    print("Database tables created successfully!")
    
    # Check if achievements exist, if not create them
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT COUNT(*) FROM achievements"))
        count = result.scalar()
        
        if count == 0:
            print("Creating achievements...")
            achievements_data = [
                ("First Steps", "Log your first activity", "🥾", "activity", "first_activity", 1, 10),
                ("Consistent", "Log activities for 3 consecutive days", "🔥", "consistency", "consecutive_days", 3, 25),
                ("Week Warrior", "Log activities for 7 consecutive days", "💪", "consistency", "consecutive_days", 7, 50),
                ("Monthly Master", "Log activities for 30 consecutive days", "🏆", "consistency", "consecutive_days", 30, 100),
                ("Speed Demon", "Log a running activity", "🏃", "activity", "activity_type", 1, 15),
                ("Strength Builder", "Log a strength training activity", "💪", "activity", "activity_type", 1, 15),
                ("Cardio King", "Log a cardio activity", "❤️", "activity", "activity_type", 1, 15),
                ("Flexibility Focus", "Log a flexibility activity", "🧘", "activity", "activity_type", 1, 15),
                ("Distance Runner", "Run 5km in a single activity", "🏃‍♂️", "distance", "distance_km", 5, 30),
                ("Marathon Ready", "Run 10km in a single activity", "🏃‍♀️", "distance", "distance_km", 10, 50),
                ("Time Master", "Exercise for 60+ minutes", "⏰", "duration", "duration_minutes", 60, 25),
                ("Early Bird", "Log an activity before 8 AM", "🌅", "time", "morning_activity", 1, 20),
                ("Night Owl", "Log an activity after 8 PM", "🦉", "time", "evening_activity", 1, 20),
                ("Weekend Warrior", "Log activities on both weekend days", "🏖️", "weekend", "weekend_activities", 2, 30),
                ("Goal Getter", "Complete your first goal", "🎯", "goals", "goal_completion", 1, 40)
            ]
            
            for achievement in achievements_data:
                db.execute(text("""
                    INSERT INTO achievements (name, description, icon, category, requirement_type, requirement_value, points)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """), achievement)
            
            db.commit()
            print("Successfully created 15 achievements!")
        else:
            print(f"Achievements already exist ({count} found). Skipping creation.")
            
    except Exception as e:
        print(f"Error with achievements: {e}")
        db.rollback()
    finally:
        db.close()
    
    # Run migration for performed_at column
    migrate_activity_logs()
    
    print("Reviewer database setup completed successfully!")

def migrate_activity_logs():
    """Add performed_at column to activity_logs table if it doesn't exist."""
    import sqlite3
    
    conn = None
    try:
        conn = sqlite3.connect("dev.db")
        cursor = conn.cursor()
        
        # Check if performed_at column already exists
        cursor.execute("PRAGMA table_info(activity_logs)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'performed_at' in columns:
            print("'performed_at' column already exists. No migration needed.")
            return
        
        # Add the performed_at column
        cursor.execute("ALTER TABLE activity_logs ADD COLUMN performed_at DATETIME")
        print("Added 'performed_at' column to 'activity_logs' table.")
        
        # Populate performed_at with existing created_at values where performed_at is NULL
        cursor.execute("UPDATE activity_logs SET performed_at = created_at WHERE performed_at IS NULL")
        conn.commit()
        print("Successfully populated 'performed_at' column with 'created_at' values.")
        
    except sqlite3.Error as e:
        print(f"Error migrating activity_logs table: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    setup_reviewer_database()
