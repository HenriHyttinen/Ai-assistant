#!/usr/bin/env python3
"""
Simple database setup script that works from any directory
"""
import sys
import os
from pathlib import Path

# Get the backend directory (parent of this script)
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def setup_database():
    """Set up the database with proper error handling"""
    try:
        print("🔧 Setting up database...")
        
        # Change to backend directory
        os.chdir(backend_dir)
        print(f"📁 Working directory: {os.getcwd()}")
        
        # Import after setting up path
        from database import SessionLocal, engine
        from sqlalchemy import text
        
        print("✅ Successfully imported database modules")
        
        # Create database file if it doesn't exist
        db_path = backend_dir / "dev.db"
        if not db_path.exists():
            print(f"📁 Creating database file: {db_path}")
            db_path.touch()
        
        # Test database connection
        db = SessionLocal()
        try:
            # Test the connection
            result = db.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            
            # Create tables
            print("🔨 Creating database tables...")
            from models import Base
            Base.metadata.create_all(bind=engine)
            print("✅ Database tables created successfully")
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
        finally:
            db.close()
        
        print("🎉 Database setup completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running this from the backend directory")
        print("💡 Try: cd /path/to/backend && python database_setup/simple_setup.py")
        return False
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
