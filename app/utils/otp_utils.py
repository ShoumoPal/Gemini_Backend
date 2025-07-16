import random
import string
from datetime import datetime, timedelta
from ..services.cache_service import CacheService

cache_service = CacheService()

def generate_otp(length: int = 6) -> str:
    """Generate a random OTP"""
    return ''.join(random.choices(string.digits, k=length))

def store_otp(mobile_number: str, otp: str, expiration_minutes: int = 5):
    """Store OTP in cache with expiration"""
    key = f"otp:{mobile_number}"
    cache_service.set(key, otp, expiration_minutes * 60)

def verify_otp(mobile_number: str, otp: str) -> bool:
    """Verify OTP from cache"""
    key = f"otp:{mobile_number}"
    stored_otp = cache_service.get(key)
    if stored_otp and stored_otp == otp:
        cache_service.delete(key)  # OTP used, remove it
        return True
    return False

def send_otp_sms(mobile_number: str, otp: str):
    """Mock SMS sending - replace with actual SMS service"""
    print(f"Sending OTP {otp} to {mobile_number}")
    # In production, integrate with SMS service like Twilio
    return True