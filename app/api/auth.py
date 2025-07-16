from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database import get_db
from ..schemas.user import UserCreate, UserLogin, UserResponse, Token, OTPRequest, OTPVerify, TokenRefresh
from ..services.auth_service import AuthService
from ..utils.jwt_utils import create_access_token, create_refresh_token, verify_token
from ..middleware.rate_limit_middleware import RateLimitMiddleware, cache_service

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    auth_service = AuthService(db)
    
    # Check if user already exists
    existing_user = auth_service.get_user_by_mobile(user_data.mobile_number)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this mobile number already exists"
        )
    
    user = auth_service.create_user(user_data)
    return user

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user with mobile and password"""
    auth_service = AuthService(db)
    
    # Rate limiting for login attempts
    rate_limit_key = f"login_attempts:{user_data.mobile_number}"
    try:
        rate_limit = RateLimitMiddleware(None)
        rate_limit.check_rate_limit(rate_limit_key, 5, 300)  # 5 attempts per 5 minutes
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    user = auth_service.authenticate_user(user_data.mobile_number, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create tokens
    access_token = create_access_token(data={"user_id": user.id})
    refresh_token = create_refresh_token(data={"user_id": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 3600
    }

@router.post("/send-otp")
async def send_otp(otp_request: OTPRequest, db: Session = Depends(get_db)):
    """Send OTP to mobile number"""
    auth_service = AuthService(db)
    
    # Rate limiting for OTP requests
    rate_limit_key = f"otp_requests:{otp_request.mobile_number}"
    try:
        rate_limit = RateLimitMiddleware(None)
        rate_limit.check_rate_limit(rate_limit_key, 3, 300)  # 3 OTPs per 5 minutes
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many OTP requests. Please try again later."
        )
    
    success = auth_service.send_otp(otp_request.mobile_number)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP"
        )
    
    return {"message": "OTP sent successfully"}

@router.post("/verify-otp")
async def verify_otp(otp_data: OTPVerify, db: Session = Depends(get_db)):
    """Verify OTP and allow password reset"""
    auth_service = AuthService(db)
    
    # Verify OTP
    is_valid = auth_service.verify_otp_code(otp_data.mobile_number, otp_data.otp)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Check if user exists
    user = auth_service.get_user_by_mobile(otp_data.mobile_number)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "OTP verified successfully", "user_id": user.id}

@router.post("/reset-password")
async def reset_password(mobile_number: str, new_password: str, otp: str, db: Session = Depends(get_db)):
    """Reset password after OTP verification"""
    auth_service = AuthService(db)
    
    # Verify OTP first
    is_valid = auth_service.verify_otp_code(mobile_number, otp)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    success = auth_service.reset_password(mobile_number, new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "Password reset successfully"}

@router.post("/refresh-token", response_model=Token)
async def refresh_token(token_data: TokenRefresh):
    """Refresh access token using refresh token"""
    payload = verify_token(token_data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Create new tokens
    access_token = create_access_token(data={"user_id": user_id})
    refresh_token = create_refresh_token(data={"user_id": user_id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 3600
    }