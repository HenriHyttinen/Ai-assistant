#!/usr/bin/env python3
"""
Migration script to add performed_at column to activity_logs table
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
from sqlalchemy import text

def migrate_activity_logs():
    """Add performed_at column to activity_logs table"""
    print("Migrating activity_logs table...")
    
    with engine.connect() as conn:
        try:
            # Add performed_at column
            conn.execute(text("""
                ALTER TABLE activity_logs 
                ADD COLUMN performed_at DATETIME
            """))
            
            # Update existing records to use created_at as performed_at
            conn.execute(text("""
                UPDATE activity_logs 
                SET performed_at = created_at 
                WHERE performed_at IS NULL
            """))
            
            conn.commit()
            print("Successfully added performed_at column to activity_logs table!")
            
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("Column performed_at already exists. Skipping migration.")
            else:
                print(f"Error during migration: {e}")
                raise

if __name__ == "__main__":
    migrate_activity_logs()
