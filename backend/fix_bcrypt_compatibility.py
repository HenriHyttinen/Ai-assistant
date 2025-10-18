#!/usr/bin/env python3
"""
Fix bcrypt compatibility issues by ensuring correct versions
This script checks and fixes bcrypt/passlib version compatibility
"""

import sys
import os
import subprocess

def check_and_fix_bcrypt():
    """Check bcrypt version and fix if needed."""
    print("🔧 Checking bcrypt compatibility...")
    
    try:
        import bcrypt
        import passlib
        
        print(f"📦 Current bcrypt version: {bcrypt.__version__}")
        print(f"📦 Current passlib version: {passlib.__version__}")
        
        # Check if bcrypt version is compatible
        bcrypt_version = bcrypt.__version__
        major_version = int(bcrypt_version.split('.')[0])
        
        if major_version >= 5:
            print("⚠️  bcrypt 5.x detected - this is incompatible with passlib 1.7.4")
            print("🔧 Fixing by downgrading bcrypt to 4.3.0...")
            
            # Downgrade bcrypt
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "bcrypt==4.3.0"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ bcrypt downgraded successfully!")
                print("🔄 Please restart your backend server for changes to take effect.")
                return True
            else:
                print(f"❌ Failed to downgrade bcrypt: {result.stderr}")
                return False
        else:
            print("✅ bcrypt version is compatible!")
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def create_test_account_via_api():
    """Create test account using API endpoints."""
    print("\n🔧 Creating test account via API...")
    
    try:
        import urllib.request
        import urllib.parse
        import json
        
        # Register account
        data = json.dumps({"email": "reviewer@test.com", "password": "testpass123"}).encode()
        req = urllib.request.Request(
            "http://localhost:8000/auth/register",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        
        try:
            response = urllib.request.urlopen(req, timeout=10)
            print("✅ Account registered successfully!")
        except urllib.error.HTTPError as e:
            if e.code == 400 and "already registered" in e.read().decode().lower():
                print("✅ Account already exists!")
            else:
                print(f"❌ Registration failed: {e}")
                return False
        
        # Verify account
        verify_req = urllib.request.Request(
            "http://localhost:8000/auth/verify-email-simple?email=reviewer@test.com"
        )
        
        try:
            verify_response = urllib.request.urlopen(verify_req, timeout=10)
            print("✅ Account verified successfully!")
        except urllib.error.HTTPError as e:
            print(f"❌ Verification failed: {e}")
            return False
        
        print(f"\n{'='*60}")
        print(f"🎉 TEST ACCOUNT READY!")
        print(f"{'='*60}")
        print(f"📧 Email: reviewer@test.com")
        print(f"🔑 Password: testpass123")
        print(f"✅ Status: Verified and ready to use")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"❌ API method failed: {e}")
        return False

def main():
    print("🔧 Fixing bcrypt compatibility and setting up test account...")
    print("=" * 60)
    
    # Check and fix bcrypt compatibility
    if not check_and_fix_bcrypt():
        print("\n💡 Manual solution:")
        print("Run these commands to fix bcrypt compatibility:")
        print("pip install bcrypt==4.3.0")
        print("Then restart your backend server.")
        return False
    
    # Create test account
    if create_test_account_via_api():
        print("✅ Test account setup complete!")
        return True
    else:
        print("\n💡 Manual solution:")
        print("Make sure backend server is running, then run:")
        print('curl -X POST "http://localhost:8000/auth/register" \\')
        print('  -H "Content-Type: application/json" \\')
        print('  -d \'{"email": "reviewer@test.com", "password": "testpass123"}\'')
        print('curl -X POST "http://localhost:8000/auth/verify-email-simple?email=reviewer@test.com"')
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
