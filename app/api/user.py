from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.user import UserResponse
from ..services.auth_service import AuthService
from ..middleware.auth_middleware import AuthMiddleware, security

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/profile", response_model=UserResponse)
async def get_profile(credentials = Depends(security), db: Session = Depends(get_db)):
    """Get current user profile"""
    auth_middleware = AuthMiddleware(None, credentials)
    user = auth_middleware.get_current_user()
    return user

@router.put("/profile", response_model=UserResponse)
async def update_profile(mobile_number: str, credentials = Depends(security), db: Session = Depends(get_db)):
    """Update user profile"""
    auth_middleware = AuthMiddleware(None, credentials)
    user = auth_middleware.get_current_user()
    
    auth_service = AuthService(db)
    
    # Check if new mobile number already exists
    existing_user = auth_service.get_user_by_mobile(mobile_number)
    if existing_user and existing_user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already in use"
        )
    
    user.mobile_number = mobile_number
    db.commit()
    db.refresh(user)
    
    return user

@router.get("/usage-stats")
async def get_usage_stats(credentials = Depends(security), db: Session = Depends(get_db)):
    """Get user usage statistics"""
    auth_middleware = AuthMiddleware(None, credentials)
    user = auth_middleware.get_current_user()
    
    return {
        "daily_usage_count": user.daily_usage_count,
        "subscription_tier": user.subscription_tier,
        "subscription_status": user.subscription_status,
        "last_usage_reset": user.last_usage_reset
    }