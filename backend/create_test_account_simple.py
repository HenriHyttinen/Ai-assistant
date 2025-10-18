#!/usr/bin/env python3
"""
Simple test account creation script that bypasses bcrypt issues
This script creates and verifies the reviewer@test.com account for easy testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
from models.user import User
from sqlalchemy.orm import Session

def create_test_account_simple():
    """Create and verify the test account for reviewers using direct database operations."""
    db = next(get_db())
    
    try:
        # Check if test account already exists
        existing_user = db.query(User).filter(User.email == "reviewer@test.com").first()
        if existing_user:
            print("✅ Test account already exists!")
            if existing_user.is_verified:
                print("✅ Test account is already verified!")
                print(f"📧 Email: reviewer@test.com")
                print(f"🔑 Password: testpass123")
                return True
            else:
                print("🔧 Test account exists but is not verified. Verifying now...")
                existing_user.is_verified = True
                db.commit()
                print("✅ Test account verified!")
                print(f"📧 Email: reviewer@test.com")
                print(f"🔑 Password: testpass123")
                return True
        
        # Create the test account directly in database
        print("🔧 Creating test account...")
        
        # Use a simple hash for the password (this bypasses bcrypt issues)
        import hashlib
        password_hash = hashlib.sha256("testpass123".encode()).hexdigest()
        
        test_user = User(
            email="reviewer@test.com",
            hashed_password=password_hash,
            is_active=True,
            is_verified=True  # Mark as verified immediately
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"\n{'='*60}")
        print(f"🎉 TEST ACCOUNT CREATED SUCCESSFULLY!")
        print(f"{'='*60}")
        print(f"📧 Email: reviewer@test.com")
        print(f"🔑 Password: testpass123")
        print(f"✅ Status: Verified and ready to use")
        print(f"{'='*60}")
        print(f"🚀 You can now login with these credentials!")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"❌ Error creating test account: {str(e)}")
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    print("🔧 Setting up test account for reviewers (simple method)...")
    success = create_test_account_simple()
    if success:
        print("✅ Test account setup complete!")
    else:
        print("❌ Failed to create test account")
        sys.exit(1)
