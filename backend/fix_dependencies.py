#!/usr/bin/env python3
"""
Script to fix missing dependencies for reviewers
"""
import subprocess
import sys
import os

def install_missing_dependencies():
    """Install missing dependencies that might not be in requirements.txt"""
    print("Installing missing dependencies...")
    
    missing_deps = [
        "supabase==2.3.0",
    ]
    
    # Create __init__.py files for Python packages
    print("Creating missing __init__.py files...")
    init_files = [
        "lib/__init__.py",
        "auth/__init__.py",
        "ai/__init__.py",
        "middleware/__init__.py",
        "schemas/__init__.py",
    ]
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            try:
                with open(init_file, 'w') as f:
                    f.write("# This file makes the directory a Python package\n")
                print(f"✅ Created {init_file}")
            except Exception as e:
                print(f"❌ Failed to create {init_file}: {e}")
        else:
            print(f"✅ {init_file} already exists")
    
    for dep in missing_deps:
        try:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            return False
    
    print("✅ All dependencies installed successfully!")
    return True

if __name__ == "__main__":
    if install_missing_dependencies():
        print("\n🎉 Dependencies fixed! You can now run the application.")
        print("Try running: python main.py")
    else:
        print("\n❌ Failed to install some dependencies.")
        print("Please run: pip install supabase==2.3.0")
