from pydantic import BaseModel, EmailStr, constr
from typing import Optional

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str
    requires_2fa: Optional[bool] = False

class TokenData(BaseModel):
    email: Optional[str] = None

class RefreshToken(BaseModel):
    refresh_token: str

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: constr(min_length=8, max_length=72)

class LoginData(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    two_factor_enabled: bool
    oauth_provider: Optional[str] = None
    profile_picture: Optional[str] = None

    class Config:
        from_attributes = True

class TwoFactorSetup(BaseModel):
    secret: str
    qr_code: str
    backup_codes: list[str]

class TwoFactorVerify(BaseModel):
    code: str

class OAuthLogin(BaseModel):
    provider: str
    code: str

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: constr(min_length=8, max_length=72)

class ChangePassword(BaseModel):
    current_password: str
    new_password: constr(min_length=8, max_length=72)

class OAuthResponse(BaseModel):
    url: str 