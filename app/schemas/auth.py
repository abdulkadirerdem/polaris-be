from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class SignUpRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, max_length=100, description="Password (min 6 characters)")

class SignInRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password")

class ResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address for password reset")

class VerifyEmailRequest(BaseModel):
    token: str = Field(..., description="Email verification token")

class ResendVerificationRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address to resend verification")

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    email: str
    email_confirmed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_sign_in_at: Optional[datetime] = None
    user_metadata: Optional[dict] = {}
    app_metadata: Optional[dict] = {}

class SignInResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"

class SignUpResponse(BaseModel):
    user: UserResponse
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    token_type: Optional[str] = None

class AuthMessage(BaseModel):
    message: str

class AuthError(BaseModel):
    error: str
    message: str