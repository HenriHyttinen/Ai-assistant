#!/usr/bin/env python3
"""
Complete fix for missing files and imports
"""
import os
import sys

def create_missing_files():
    """Create all missing files"""
    print("🔧 Creating missing files...")
    
    # Create lib/supabase.py
    lib_supabase_content = '''import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
'''
    
    # Create lib directory and file
    os.makedirs('lib', exist_ok=True)
    with open('lib/supabase.py', 'w') as f:
        f.write(lib_supabase_content)
    print("✅ Created lib/supabase.py")
    
    # Create lib/__init__.py
    with open('lib/__init__.py', 'w') as f:
        f.write("# This file makes the lib directory a Python package\n")
    print("✅ Created lib/__init__.py")
    
    # Create other missing __init__.py files
    init_files = [
        "auth/__init__.py",
        "ai/__init__.py", 
        "middleware/__init__.py",
        "schemas/__init__.py"
    ]
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            os.makedirs(os.path.dirname(init_file), exist_ok=True)
            with open(init_file, 'w') as f:
                f.write("# This file makes the directory a Python package\n")
            print(f"✅ Created {init_file}")
        else:
            print(f"✅ {init_file} already exists")

def test_imports():
    """Test all imports"""
    print("\n🧪 Testing imports...")
    
    # Add current directory to Python path
    sys.path.insert(0, os.getcwd())
    
    try:
        from lib.supabase import supabase
        print("✅ lib.supabase import successful")
    except Exception as e:
        print(f"❌ lib.supabase import failed: {e}")
        return False
    
    try:
        from auth.supabase_auth import get_current_user_supabase
        print("✅ auth.supabase_auth import successful")
    except Exception as e:
        print(f"❌ auth.supabase_auth import failed: {e}")
        return False
    
    try:
        from routes.auth import router
        print("✅ routes.auth import successful")
    except Exception as e:
        print(f"❌ routes.auth import failed: {e}")
        return False
    
    try:
        import main
        print("✅ main.py import successful")
    except Exception as e:
        print(f"❌ main.py import failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_missing_files()
    
    if test_imports():
        print("\n🎉 All imports successful! You can now run the application.")
        print("Try running: python main.py")
    else:
        print("\n❌ Some imports still failing.")
        print("Try the alternative fix:")
        print("cp auth/supabase_auth_alternative.py auth/supabase_auth.py")
