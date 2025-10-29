#!/usr/bin/env python3
"""
Add missing micronutrient columns to the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from sqlalchemy import text

def add_micronutrient_columns():
    """Add missing micronutrient columns to ingredients and nutritional_logs tables"""
    
    micronutrient_columns = [
        ('vitamin_c', 'REAL DEFAULT 0.0'),
        ('vitamin_a', 'REAL DEFAULT 0.0'),
        ('vitamin_e', 'REAL DEFAULT 0.0'),
        ('vitamin_k', 'REAL DEFAULT 0.0'),
        ('thiamine', 'REAL DEFAULT 0.0'),
        ('riboflavin', 'REAL DEFAULT 0.0'),
        ('niacin', 'REAL DEFAULT 0.0'),
        ('folate', 'REAL DEFAULT 0.0'),
        ('magnesium', 'REAL DEFAULT 0.0'),
        ('zinc', 'REAL DEFAULT 0.0'),
        ('selenium', 'REAL DEFAULT 0.0'),
        ('potassium', 'REAL DEFAULT 0.0'),
        ('phosphorus', 'REAL DEFAULT 0.0'),
        ('omega_3', 'REAL DEFAULT 0.0'),
        ('omega_6', 'REAL DEFAULT 0.0')
    ]
    
    with engine.connect() as conn:
        # Add columns to ingredients table
        print("Adding micronutrient columns to ingredients table...")
        for column_name, column_type in micronutrient_columns:
            try:
                conn.execute(text(f'ALTER TABLE ingredients ADD COLUMN {column_name} {column_type}'))
                print(f"  ✅ Added {column_name}")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print(f"  ⚠️  Column {column_name} already exists")
                else:
                    print(f"  ❌ Error adding {column_name}: {e}")
        
        # Add columns to nutritional_logs table
        print("\nAdding micronutrient columns to nutritional_logs table...")
        for column_name, column_type in micronutrient_columns:
            try:
                conn.execute(text(f'ALTER TABLE nutritional_logs ADD COLUMN {column_name} {column_type}'))
                print(f"  ✅ Added {column_name}")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print(f"  ⚠️  Column {column_name} already exists")
                else:
                    print(f"  ❌ Error adding {column_name}: {e}")
        
        conn.commit()
        print("\n✅ Migration completed!")

if __name__ == "__main__":
    add_micronutrient_columns()





