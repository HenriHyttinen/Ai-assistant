#!/usr/bin/env python3
"""
Add timezone support to user settings
"""
import sys
import os
sys.path.append('.')

from database import SessionLocal, engine
from sqlalchemy import text

def add_timezone_support():
    """Add timezone column to user_settings table"""
    print("🕐 Adding timezone support to user settings...")
    
    db = SessionLocal()
    try:
        # Add timezone column to user_settings table
        alter_sql = """
        ALTER TABLE user_settings 
        ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC';
        """
        
        db.execute(text(alter_sql))
        db.commit()
        print("✅ Added timezone column to user_settings table")
        
        # Update existing users to have UTC timezone
        update_sql = """
        UPDATE user_settings 
        SET timezone = 'UTC' 
        WHERE timezone IS NULL;
        """
        
        db.execute(text(update_sql))
        db.commit()
        print("✅ Updated existing users with UTC timezone")
        
        # Verify the changes
        result = db.execute(text("SELECT COUNT(*) FROM user_settings WHERE timezone IS NOT NULL"))
        count = result.scalar()
        print(f"📊 Updated {count} user settings with timezone support")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding timezone support: {e}")
        # Check if column already exists
        try:
            result = db.execute(text("SELECT timezone FROM user_settings LIMIT 1"))
            print("✅ Timezone column already exists")
        except Exception:
            print("❌ Timezone column does not exist and could not be created")
    finally:
        db.close()

if __name__ == "__main__":
    add_timezone_support()










