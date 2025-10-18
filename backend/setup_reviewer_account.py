#!/usr/bin/env python3
"""
Simple script to help reviewers set up test account
This script provides clear instructions and checks if the backend is running
"""

import sys
import os
import subprocess

def check_backend_running():
    """Check if backend server is running."""
    try:
        import urllib.request
        import urllib.error
        
        # Try to connect to the backend
        req = urllib.request.Request("http://localhost:8000/health")
        response = urllib.request.urlopen(req, timeout=5)
        return True
    except:
        return False

def main():
    print("🔧 Setting up reviewer test account...")
    print("=" * 60)
    
    # Check if backend is running
    print("🔍 Checking if backend server is running...")
    if check_backend_running():
        print("✅ Backend server is running!")
    else:
        print("❌ Backend server is not running!")
        print("\n💡 Please start the backend server first:")
        print("   cd backend")
        print("   source venv/bin/activate")
        print("   python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        print("\n   Then run this script again.")
        return False
    
    print("\n📋 Manual setup instructions:")
    print("=" * 60)
    print("Run these two commands in your terminal:")
    print()
    print('1. Register the account:')
    print('   curl -X POST "http://localhost:8000/auth/register" \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"email": "reviewer@test.com", "password": "testpass123"}\'')
    print()
    print('2. Verify the account:')
    print('   curl -X POST "http://localhost:8000/auth/verify-email-simple?email=reviewer@test.com"')
    print()
    print("3. Test login:")
    print('   curl -X POST "http://localhost:8000/auth/token" \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"email": "reviewer@test.com", "password": "testpass123"}\'')
    print()
    print("=" * 60)
    print("✅ After running these commands, you can login with:")
    print("   📧 Email: reviewer@test.com")
    print("   🔑 Password: testpass123")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
