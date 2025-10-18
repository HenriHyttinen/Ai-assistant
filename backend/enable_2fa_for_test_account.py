#!/usr/bin/env python3
"""
Enable 2FA for the test account to allow 123456 verification
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
from models.user import User

def enable_2fa_for_test_account():
    """Enable 2FA for the test account."""
    db = next(get_db())
    
    try:
        # Find the test account
        test_user = db.query(User).filter(User.email == "reviewer@test.com").first()
        if not test_user:
            print("❌ Test account not found!")
            return False
        
        # Enable 2FA for the test account
        test_user.two_factor_enabled = True
        test_user.two_factor_secret = "test_secret_for_development"
        
        db.commit()
        db.refresh(test_user)
        
        print("✅ 2FA enabled for test account!")
        print(f"📧 Email: {test_user.email}")
        print(f"🔑 Password: testpass123")
        print(f"🔐 2FA Code: 123456")
        print(f"✅ Status: Ready for 2FA testing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error enabling 2FA: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Enabling 2FA for test account...")
    success = enable_2fa_for_test_account()
    if success:
        print("✅ Test account 2FA setup complete!")
        print("\n💡 Now you can test 2FA verification with code: 123456")
    else:
        print("❌ Failed to enable 2FA for test account")
        sys.exit(1)
