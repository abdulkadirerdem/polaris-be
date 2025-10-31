from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserResponse(BaseModel):
    id: str
    email: str
    auth_type: str = "email"
    subscription: Optional[str] = None
    is_active: bool = True
    email_verified: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    profile: Optional[Dict[str, Any]] = {}
    favorites: Optional[List[str]] = []
    settings: Optional[Dict[str, Any]] = {}

class UserUpdate(BaseModel):
    subscription: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None
    favorites: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None

class UserSettings(BaseModel):
    email_notifications: bool = True
    push_notifications: bool = False
    language: str = "tr"
    timezone: str = "Europe/Istanbul"
    theme: str = "light"

class UserProfile(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    country: Optional[str] = None
    city: Optional[str] = None

class UserDelete(BaseModel):
    password: str = Field(..., description="Password confirmation for account deletion")
    reason: Optional[str] = Field(None, description="Optional reason for account deletion")

class UserStats(BaseModel):
    total_forecasts: int = 0
    active_subscriptions: int = 0
    favorite_shares: int = 0
    account_age_days: int = 0