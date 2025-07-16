from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from ..models.user import SubscriptionTier, SubscriptionStatus

class UserBase(BaseModel):
    mobile_number: str = Field(..., pattern=r'^\+?1?\d{9,15}$')

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    mobile_number: str
    password: str

class OTPRequest(BaseModel):
    mobile_number: str

class OTPVerify(BaseModel):
    mobile_number: str
    otp: str

class UserResponse(UserBase):
    id: int
    subscription_tier: SubscriptionTier
    subscription_status: SubscriptionStatus
    daily_usage_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenRefresh(BaseModel):
    refresh_token: str