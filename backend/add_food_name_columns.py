#!/usr/bin/env python3
"""
Script to add food_name and meal_id columns to nutritional_logs table.
This is a workaround for migration issues.
"""

import sqlite3
import os
from pathlib import Path

def add_columns_to_sqlite():
    """Add food_name and meal_id columns to nutritional_logs table in SQLite"""
    
    # Try to find the SQLite database file
    # Check common locations
    db_paths = [
        Path("dev.db"),
        Path("app.db"),
        Path("../dev.db"),
        Path("../app.db"),
    ]
    
    db_path = None
    for path in db_paths:
        if path.exists():
            db_path = path
            break
    
    if not db_path:
        print("❌ Could not find SQLite database file (dev.db or app.db)")
        print("   Please specify the database path manually")
        return False
    
    print(f"📦 Found database: {db_path.absolute()}")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(nutritional_logs)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'food_name' in columns and 'meal_id' in columns:
            print("✅ Columns 'food_name' and 'meal_id' already exist")
            conn.close()
            return True
        
        # Add food_name column if it doesn't exist
        if 'food_name' not in columns:
            print("➕ Adding 'food_name' column...")
            cursor.execute("ALTER TABLE nutritional_logs ADD COLUMN food_name TEXT")
            print("   ✅ Added 'food_name' column")
        else:
            print("   ℹ️  'food_name' column already exists")
        
        # Add meal_id column if it doesn't exist
        if 'meal_id' not in columns:
            print("➕ Adding 'meal_id' column...")
            cursor.execute("ALTER TABLE nutritional_logs ADD COLUMN meal_id INTEGER")
            print("   ✅ Added 'meal_id' column")
        else:
            print("   ℹ️  'meal_id' column already exists")
        
        # SQLite doesn't support adding foreign key constraints via ALTER TABLE
        # but the column will work without it
        conn.commit()
        conn.close()
        
        print("✅ Successfully added columns to nutritional_logs table!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Adding food_name and meal_id columns to nutritional_logs table...")
    success = add_columns_to_sqlite()
    if success:
        print("\n✨ Done! You can now use the daily logging feature with food names.")
    else:
        print("\n❌ Failed to add columns. Please check the error messages above.")
        exit(1)

