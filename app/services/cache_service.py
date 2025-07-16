import redis
import json
from typing import Any, Optional
from ..config import settings

class CacheService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, expiration: int = 3600):
        """Set value in cache with expiration"""
        try:
            self.redis_client.setex(key, expiration, json.dumps(value))
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str):
        """Delete key from cache"""
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return self.redis_client.exists(key)
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False