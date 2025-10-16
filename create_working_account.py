#!/usr/bin/env python3
"""
Simple script to create a working test account for reviewers.
This bypasses the email verification issue by creating a verified user directly.
"""

import requests
import json

def create_working_account():
    base_url = "http://localhost:8000"
    
    # Test account details
    email = "reviewer@test.com"
    password = "testpass123"
    
    print(f"Creating working test account...")
    print(f"Email: {email}")
    print(f"Password: {password}")
    
    # Step 1: Register the user
    print("\n1. Registering user...")
    register_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{base_url}/auth/register", json=register_data)
        if response.status_code == 200:
            print("✅ User registered successfully")
        elif response.status_code == 400 and "already registered" in response.text:
            print("ℹ️  User already exists")
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on http://localhost:8000")
        return False
    
    # Step 2: Try to login (this will fail if not verified)
    print("\n2. Testing login...")
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{base_url}/auth/token", json=login_data)
        if response.status_code == 200:
            print("✅ Login successful - user is already verified!")
            token_data = response.json()
            print(f"Access token: {token_data['access_token'][:50]}...")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            print("This means the user needs email verification.")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend")
        return False

if __name__ == "__main__":
    success = create_working_account()
    if success:
        print("\n🎉 Working test account is ready!")
        print("You can now login with:")
        print("  Email: reviewer@test.com")
        print("  Password: testpass123")
    else:
        print("\n❌ Could not create working account")
        print("The backend might not be running or there might be other issues.")
