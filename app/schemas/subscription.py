from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ..models.user import SubscriptionTier, SubscriptionStatus

class SubscriptionCreate(BaseModel):
    tier: SubscriptionTier

class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    tier: SubscriptionTier
    status: SubscriptionStatus
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class StripeCheckoutRequest(BaseModel):
    tier: SubscriptionTier
    success_url: str
    cancel_url: str