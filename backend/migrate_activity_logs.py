#!/usr/bin/env python3
"""
Migration script to add performed_at column to activity_logs table
"""
import sqlite3
from datetime import datetime

def migrate_activity_logs():
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
    print("Migrating activity_logs table...")
    migrate_activity_logs()
    print("Migration completed!")