#!/usr/bin/env python3
"""
Standalone script to fix the missing performed_at column in activity_logs table.
Run this if you're getting "no such column: activity_logs.performed_at" errors.
"""
import sqlite3
import os

def fix_performed_at_column():
    """Add performed_at column to activity_logs table if it doesn't exist."""
    
    # Check which database file exists
    db_files = ["dev.db", "sql_app.db"]
    db_file = None
    
    for file in db_files:
        if os.path.exists(file):
            db_file = file
            break
    
    if not db_file:
        print("No database file found. Please run setup_reviewer.py first.")
        return
    
    print(f"Using database file: {db_file}")
    
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check if performed_at column already exists
        cursor.execute("PRAGMA table_info(activity_logs)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'performed_at' in columns:
            print("✅ 'performed_at' column already exists. No fix needed.")
            return
        
        print("🔧 Adding 'performed_at' column to 'activity_logs' table...")
        
        # Add the performed_at column
        cursor.execute("ALTER TABLE activity_logs ADD COLUMN performed_at DATETIME")
        
        # Populate performed_at with existing created_at values where performed_at is NULL
        cursor.execute("UPDATE activity_logs SET performed_at = created_at WHERE performed_at IS NULL")
        conn.commit()
        
        print("✅ Successfully added 'performed_at' column and populated it with existing data.")
        print("🎉 The 'no such column' error should now be fixed!")
        
    except sqlite3.Error as e:
        print(f"❌ Error fixing activity_logs table: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔧 Fixing missing performed_at column in activity_logs table...")
    fix_performed_at_column()
    print("✨ Done! You can now restart your backend server.")
