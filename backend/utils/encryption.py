"""
Encryption utilities for sensitive data at rest
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional
import json

class DataEncryption:
    """Handles encryption and decryption of sensitive data"""
    
    def __init__(self):
        # Get encryption key from environment or generate one
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self) -> bytes:
        """Get encryption key from environment or create a new one"""
        key_str = os.getenv("ENCRYPTION_KEY")
        
        if key_str:
            # Use existing key from environment
            return key_str.encode()
        else:
            # Generate new key (in production, this should be set in environment)
            key = Fernet.generate_key()
            print("WARNING: Generated new encryption key. Set ENCRYPTION_KEY in .env for production!")
            return key
    
    def encrypt_string(self, data: str) -> str:
        """Encrypt a string and return base64 encoded result"""
        if not data:
            return data
        
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_string(self, encrypted_data: str) -> str:
        """Decrypt a base64 encoded string"""
        if not encrypted_data:
            return encrypted_data
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            # If decryption fails, return the original data (might be unencrypted)
            print(f"Decryption failed: {e}")
            return encrypted_data
    
    def encrypt_dict(self, data: dict) -> str:
        """Encrypt a dictionary by converting to JSON first"""
        if not data:
            return ""
        
        json_str = json.dumps(data)
        return self.encrypt_string(json_str)
    
    def decrypt_dict(self, encrypted_data: str) -> dict:
        """Decrypt and parse JSON data"""
        if not encrypted_data:
            return {}
        
        try:
            json_str = self.decrypt_string(encrypted_data)
            return json.loads(json_str)
        except Exception as e:
            print(f"Failed to decrypt dict: {e}")
            return {}
    
    def encrypt_float(self, value: float) -> str:
        """Encrypt a float value"""
        if value is None:
            return ""
        return self.encrypt_string(str(value))
    
    def decrypt_float(self, encrypted_value: str) -> Optional[float]:
        """Decrypt a float value"""
        if not encrypted_value:
            return None
        
        try:
            decrypted_str = self.decrypt_string(encrypted_value)
            return float(decrypted_str)
        except (ValueError, TypeError):
            return None

# Global encryption instance
encryption = DataEncryption()

def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data"""
    return encryption.encrypt_string(data)

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    return encryption.decrypt_string(encrypted_data)

def encrypt_sensitive_dict(data: dict) -> str:
    """Encrypt sensitive dictionary data"""
    return encryption.encrypt_dict(data)

def decrypt_sensitive_dict(encrypted_data: str) -> dict:
    """Decrypt sensitive dictionary data"""
    return encryption.decrypt_dict(encrypted_data)
