import pyotp
import qrcode
from io import BytesIO
import base64
import json
import secrets
from typing import Tuple, List
from fastapi import HTTPException
from models.user import User
from sqlalchemy.orm import Session

def generate_totp_secret() -> str:
    """Generate a new TOTP secret."""
    return pyotp.random_base32()

def generate_totp_uri(email: str, secret: str) -> str:
    """Generate TOTP URI for QR code."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(email, issuer_name="Numbers Don't Lie")

def generate_qr_code(uri: str) -> str:
    """Generate QR code as base64 string."""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def verify_totp(secret: str, token: str) -> bool:
    """Verify TOTP token."""
    totp = pyotp.TOTP(secret)
    return totp.verify(token)

def setup_2fa(db: Session, user: User) -> Tuple[str, str, List[str]]:
    """Setup 2FA for a user."""
    if user.two_factor_enabled:
        raise HTTPException(status_code=400, detail="2FA is already enabled")
    
    secret = generate_totp_secret()
    uri = generate_totp_uri(user.email, secret)
    qr_code = generate_qr_code(uri)
    backup_codes = generate_backup_codes()
    
    # Store secret and backup codes temporarily until verified
    user.two_factor_secret = secret
    user.backup_codes = json.dumps(backup_codes)
    user.two_factor_enabled = False
    db.commit()
    
    return secret, qr_code, backup_codes

def verify_2fa_setup(db: Session, user: User, token: str) -> bool:
    """Verify and enable 2FA setup."""
    if not user.two_factor_secret:
        raise HTTPException(status_code=400, detail="2FA setup not initiated")
    
    if verify_totp(user.two_factor_secret, token):
        user.two_factor_enabled = True
        db.commit()
        return True
    return False

def generate_backup_codes(count: int = 8) -> List[str]:
    """Generate backup codes for 2FA recovery."""
    return [secrets.token_hex(4).upper() for _ in range(count)]

def verify_2fa_login(user: User, token: str) -> bool:
    """Verify 2FA token during login (supports both TOTP and backup codes)."""
    if not user.two_factor_enabled:
        raise HTTPException(status_code=400, detail="2FA not enabled")
    
    # First try TOTP verification
    if user.two_factor_secret and verify_totp(user.two_factor_secret, token):
        return True
    
    # Then try backup code verification
    if user.backup_codes:
        backup_codes = json.loads(user.backup_codes)
        if token in backup_codes:
            # Remove used backup code
            backup_codes.remove(token)
            user.backup_codes = json.dumps(backup_codes)
            return True
    
    return False

def verify_backup_code(user: User, code: str) -> bool:
    """Verify a backup code and remove it if valid."""
    if not user.backup_codes:
        return False
    
    backup_codes = json.loads(user.backup_codes)
    if code in backup_codes:
        backup_codes.remove(code)
        user.backup_codes = json.dumps(backup_codes)
        return True
    
    return False 