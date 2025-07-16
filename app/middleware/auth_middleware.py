from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..utils.jwt_utils import verify_token
from ..services.auth_service import AuthService
from ..database import SessionLocal

security = HTTPBearer()

class AuthMiddleware:
    def __init__(self, request: Request, credentials: HTTPAuthorizationCredentials):
        self.request = request
        self.credentials = credentials
    
    def get_current_user(self):
        """Get current user from JWT token"""
        token = self.credentials.credentials
        payload = verify_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        db = SessionLocal()
        try:
            auth_service = AuthService(db)
            user = auth_service.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            return user
        finally:
            db.close()