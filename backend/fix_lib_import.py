#!/usr/bin/env python3
"""
Specific fix for lib.supabase import issues
"""
import sys
import os
import subprocess

def fix_lib_import():
    """Fix the lib.supabase import issue specifically"""
    print("🔧 Fixing lib.supabase import issue...")
    
    # Add current directory to Python path
    current_dir = os.getcwd()
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
        print(f"✅ Added {current_dir} to Python path")
    
    # Check if lib directory exists
    lib_dir = os.path.join(current_dir, 'lib')
    if not os.path.exists(lib_dir):
        print(f"❌ lib directory not found at {lib_dir}")
        return False
    
    # Check if lib/__init__.py exists
    init_file = os.path.join(lib_dir, '__init__.py')
    if not os.path.exists(init_file):
        print(f"❌ lib/__init__.py not found")
        return False
    else:
        print("✅ lib/__init__.py exists")
    
    # Check if lib/supabase.py exists
    supabase_file = os.path.join(lib_dir, 'supabase.py')
    if not os.path.exists(supabase_file):
        print(f"❌ lib/supabase.py not found")
        return False
    else:
        print("✅ lib/supabase.py exists")
    
    # Test the import
    try:
        from lib.supabase import supabase
        print("✅ lib.supabase import successful")
        return True
    except Exception as e:
        print(f"❌ lib.supabase import failed: {e}")
        
        # Try alternative import methods
        print("🔄 Trying alternative import methods...")
        
        # Try importing the module directly
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("supabase", supabase_file)
            supabase_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(supabase_module)
            print("✅ Direct module import successful")
            return True
        except Exception as e2:
            print(f"❌ Direct module import failed: {e2}")
        
        return False

def create_alternative_import():
    """Create an alternative import method if needed"""
    print("🔄 Creating alternative import method...")
    
    # Create a simple import wrapper
    wrapper_content = '''#!/usr/bin/env python3
"""
Alternative import wrapper for lib.supabase
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

try:
    from lib.supabase import supabase
    print("✅ lib.supabase import successful via wrapper")
except Exception as e:
    print(f"❌ lib.supabase import failed via wrapper: {e}")
    sys.exit(1)
'''
    
    with open('test_lib_import.py', 'w') as f:
        f.write(wrapper_content)
    
    print("✅ Created test_lib_import.py wrapper")

if __name__ == "__main__":
    if fix_lib_import():
        print("\n🎉 lib.supabase import fixed!")
    else:
        print("\n❌ lib.supabase import still failing")
        create_alternative_import()
        print("Try running: python test_lib_import.py")
