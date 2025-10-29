#!/usr/bin/env python3
"""
Script to create micronutrient tables directly in the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine
from models.micronutrients import Base as MicronutrientBase

def create_micronutrient_tables():
    """Create micronutrient tables in the database"""
    try:
        # Create all tables
        MicronutrientBase.metadata.create_all(bind=engine)
        print("✅ Micronutrient tables created successfully!")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        micronutrient_tables = [table for table in tables if 'micronutrient' in table]
        print(f"📊 Micronutrient tables found: {micronutrient_tables}")
        
        return True
    except Exception as e:
        print(f"❌ Error creating micronutrient tables: {e}")
        return False

if __name__ == "__main__":
    create_micronutrient_tables()
