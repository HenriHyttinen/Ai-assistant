#!/usr/bin/env python3
"""
Migration script to encrypt existing sensitive data in the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models.user import User
from models.health_profile import HealthProfile
from models.activity_log import ActivityLog
from utils.encryption import encryption
import json

def migrate_encrypt_sensitive_data():
    """Encrypt existing sensitive data in the database"""
    db = SessionLocal()
    try:
        print("🔐 Starting encryption migration...")
        
        # Encrypt user sensitive data
        users = db.query(User).all()
        for user in users:
            updated = False
            
            # Encrypt 2FA secret if exists
            if user.two_factor_secret and not user.two_factor_secret.startswith('encrypted:'):
                user.two_factor_secret = 'encrypted:' + encryption.encrypt_string(user.two_factor_secret)
                updated = True
            
            # Encrypt backup codes if exist
            if user.backup_codes and not user.backup_codes.startswith('encrypted:'):
                user.backup_codes = 'encrypted:' + encryption.encrypt_string(user.backup_codes)
                updated = True
            
            if updated:
                print(f"Encrypted sensitive data for user {user.email}")
        
        # Encrypt health profile sensitive data
        profiles = db.query(HealthProfile).all()
        for profile in profiles:
            updated = False
            
            # Encrypt dietary preferences
            if profile.dietary_preferences and not profile.dietary_preferences.startswith('encrypted:'):
                profile.dietary_preferences = 'encrypted:' + encryption.encrypt_string(profile.dietary_preferences)
                updated = True
            
            # Encrypt dietary restrictions
            if profile.dietary_restrictions and not profile.dietary_restrictions.startswith('encrypted:'):
                profile.dietary_restrictions = 'encrypted:' + encryption.encrypt_string(profile.dietary_restrictions)
                updated = True
            
            # Encrypt strength indicators
            if profile.strength_indicators and not profile.strength_indicators.startswith('encrypted:'):
                profile.strength_indicators = 'encrypted:' + encryption.encrypt_string(profile.strength_indicators)
                updated = True
            
            # Encrypt exercise types
            if profile.exercise_types and not profile.exercise_types.startswith('encrypted:'):
                profile.exercise_types = 'encrypted:' + encryption.encrypt_string(profile.exercise_types)
                updated = True
            
            if updated:
                print(f"Encrypted health profile data for user {profile.user_id}")
        
        db.commit()
        print("✅ Encryption migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during encryption migration: {e}")
        db.rollback()
    finally:
        db.close()

def verify_encryption():
    """Verify that encryption is working correctly"""
    db = SessionLocal()
    try:
        print("🔍 Verifying encryption...")
        
        # Test decrypting a few records
        users = db.query(User).limit(5).all()
        for user in users:
            if user.two_factor_secret and user.two_factor_secret.startswith('encrypted:'):
                encrypted_data = user.two_factor_secret[10:]  # Remove 'encrypted:' prefix
                decrypted = encryption.decrypt_string(encrypted_data)
                print(f"✅ Successfully decrypted 2FA secret for user {user.email}")
        
        print("✅ Encryption verification completed!")
        
    except Exception as e:
        print(f"❌ Error during encryption verification: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🔐 Data Encryption Migration")
    print("=" * 50)
    
    # Run migration
    migrate_encrypt_sensitive_data()
    
    # Verify encryption
    verify_encryption()
    
    print("\n📝 Next steps:")
    print("1. Set ENCRYPTION_KEY in your .env file")
    print("2. Restart your backend server")
    print("3. Test that data can be decrypted properly")
