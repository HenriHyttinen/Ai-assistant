#!/usr/bin/env python3
"""
Create test account for reviewers
This script creates and verifies the reviewer@test.com account for easy testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
from services.auth import create_user, verify_user_email
from models.user import User
from sqlalchemy.orm import Session

def create_test_account():
    """Create and verify the test account for reviewers."""
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
                verify_user_email(db=db, user=existing_user)
                print("✅ Test account verified!")
                print(f"📧 Email: reviewer@test.com")
                print(f"🔑 Password: testpass123")
                return True
        
        # Create the test account
        print("🔧 Creating test account...")
        test_user = create_user(
            db=db, 
            email="reviewer@test.com", 
            password="testpass123"
        )
        
        # Verify the account
        print("✅ Verifying test account...")
        verify_user_email(db=db, user=test_user)
        
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
    print("🔧 Setting up test account for reviewers...")
    success = create_test_account()
    if success:
        print("✅ Test account setup complete!")
    else:
        print("❌ Failed to create test account")
        sys.exit(1)
