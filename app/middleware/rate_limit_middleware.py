from fastapi import Request, HTTPException, status
from ..services.cache_service import CacheService
from ..models.user import User, SubscriptionTier
from datetime import datetime, timezone

cache_service = CacheService()

class RateLimitMiddleware:
    def __init__(self, user: User):
        self.user = user
    
    def check_daily_limit(self):
        """Check if user has exceeded daily message limit"""
        # Reset daily count if it's a new day
        now = datetime.now(tz=timezone.utc)
        if self.user.last_usage_reset.date() < now.date():
            self.user.daily_usage_count = 0
            self.user.last_usage_reset = now
        
        # Check limits based on subscription tier
        if self.user.subscription_tier == SubscriptionTier.BASIC:
            if self.user.daily_usage_count >= 5:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Daily message limit exceeded. Upgrade to Pro for unlimited messages."
                )
        # PRO users have unlimited messages
        
        return True
    
    def increment_usage(self):
        """Increment user's daily usage count"""
        self.user.daily_usage_count += 1
        return True
    
    def check_rate_limit(self, key: str, limit: int, window: int):
        """Generic rate limiting function"""
        current_requests = cache_service.get(key) or 0
        
        if current_requests >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        cache_service.set(key, current_requests + 1, window)
        return True