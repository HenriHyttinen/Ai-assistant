#!/usr/bin/env python3
"""
Improved database setup script with better error handling
"""
import sys
import os
import sqlite3
from pathlib import Path

# Add the parent directory to the path so we can import from the backend
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def setup_database():
    """Set up the database with proper error handling"""
    try:
        # Import after adding to path
        from database import SessionLocal, engine
        from sqlalchemy import text
        
        print("🔧 Setting up database...")
        
        # Create database file if it doesn't exist
        db_path = backend_dir / "dev.db"
        if not db_path.exists():
            print(f"📁 Creating database file: {db_path}")
            db_path.touch()
        
        db = SessionLocal()
        try:
            print("📋 Creating database tables...")
            
            # Create all necessary tables
            tables_sql = [
                # Users table
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email VARCHAR UNIQUE NOT NULL,
                    hashed_password VARCHAR,
                    is_active BOOLEAN DEFAULT 1,
                    is_verified BOOLEAN DEFAULT 0,
                    two_factor_enabled BOOLEAN DEFAULT 0,
                    two_factor_secret VARCHAR,
                    backup_codes VARCHAR,
                    oauth_provider VARCHAR,
                    oauth_id VARCHAR,
                    profile_picture VARCHAR,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                """,
                
                # Health profiles table
                """
                CREATE TABLE IF NOT EXISTS health_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    age INTEGER,
                    gender VARCHAR,
                    height FLOAT,
                    weight FLOAT,
                    fitness_level VARCHAR,
                    activity_level VARCHAR,
                    goals TEXT,
                    medical_conditions TEXT,
                    medications TEXT,
                    allergies TEXT,
                    target_weight FLOAT,
                    fitness_goal VARCHAR,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                """,
                
                # Activity logs table
                """
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    activity_type VARCHAR NOT NULL,
                    duration INTEGER NOT NULL,
                    intensity VARCHAR,
                    notes TEXT,
                    performed_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                """,
                
                # Goals table
                """
                CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title VARCHAR NOT NULL,
                    description TEXT,
                    goal_type VARCHAR NOT NULL,
                    target_value FLOAT,
                    current_value FLOAT DEFAULT 0,
                    unit VARCHAR,
                    target_date DATE,
                    is_achieved BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                """,
                
                # Achievements table
                """
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
                """,
                
                # User achievements table
                """
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
                """,
                
                # User settings table
                """
                CREATE TABLE IF NOT EXISTS user_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    email_notifications BOOLEAN DEFAULT 1,
                    weekly_reports BOOLEAN DEFAULT 1,
                    ai_insights BOOLEAN DEFAULT 1,
                    data_sharing BOOLEAN DEFAULT 0,
                    measurement_system VARCHAR DEFAULT 'metric',
                    language VARCHAR DEFAULT 'en',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                """,
                
                # Data consent table
                """
                CREATE TABLE IF NOT EXISTS data_consent (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    analytics_consent BOOLEAN DEFAULT 0,
                    marketing_consent BOOLEAN DEFAULT 0,
                    data_processing_consent BOOLEAN DEFAULT 1,
                    consent_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                """,
                
                # Metrics history table
                """
                CREATE TABLE IF NOT EXISTS metrics_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    metric_type VARCHAR NOT NULL,
                    value FLOAT NOT NULL,
                    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                """
            ]
            
            for i, table_sql in enumerate(tables_sql, 1):
                try:
                    db.execute(text(table_sql))
                    print(f"  ✅ Table {i}/{len(tables_sql)} created")
                except Exception as e:
                    print(f"  ❌ Error creating table {i}: {e}")
                    raise
            
            db.commit()
            print("📊 Database tables created successfully!")
            
            # Check if achievements already exist
            result = db.execute(text("SELECT COUNT(*) FROM achievements")).scalar()
            if result > 0:
                print(f"🏆 Achievements already exist ({result} found). Skipping creation.")
            else:
                print("🏆 Creating achievements...")
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
                print("✅ Successfully created 15 achievements!")
            
            # Verify setup
            print("\n🔍 Verifying database setup...")
            tables_to_check = ['users', 'health_profiles', 'activity_logs', 'goals', 'achievements', 'user_achievements', 'user_settings', 'data_consent', 'metrics_history']
            
            for table in tables_to_check:
                try:
                    count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    print(f"  ✅ {table}: {count} records")
                except Exception as e:
                    print(f"  ❌ {table}: Error - {e}")
            
            print("\n🎉 Database setup completed successfully!")
            print("📝 You can now run the application with: python main.py")
            
        except Exception as e:
            print(f"❌ Error setting up database: {e}")
            db.rollback()
            raise
        finally:
            db.close()
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running this from the backend directory and have activated the virtual environment:")
        print("   cd backend")
        print("   source venv/bin/activate")
        print("   python database_setup/setup_improved.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()
