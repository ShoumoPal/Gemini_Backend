from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate
from ..utils.jwt_utils import verify_password, get_password_hash
from ..utils.otp_utils import generate_otp, store_otp, verify_otp, send_otp_sms
from ..config import settings

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            mobile_number=user_data.mobile_number,
            password_hash=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def authenticate_user(self, mobile_number: str, password: str) -> User:
        """Authenticate user with mobile and password"""
        user = self.db.query(User).filter(User.mobile_number == mobile_number).first()
        if not user or not verify_password(password, user.password_hash):
            return None
        return user
    
    def get_user_by_mobile(self, mobile_number: str) -> User:
        """Get user by mobile number"""
        return self.db.query(User).filter(User.mobile_number == mobile_number).first()
    
    def get_user_by_id(self, user_id: int) -> User:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def send_otp(self, mobile_number: str) -> bool:
        """Generate and send OTP"""
        otp = generate_otp()
        store_otp(mobile_number, otp, settings.otp_expiration_minutes)
        return send_otp_sms(mobile_number, otp)
    
    def verify_otp_code(self, mobile_number: str, otp: str) -> bool:
        """Verify OTP code"""
        return verify_otp(mobile_number, otp)
    
    def reset_password(self, mobile_number: str, new_password: str) -> bool:
        """Reset user password"""
        user = self.get_user_by_mobile(mobile_number)
        if not user:
            return False
        
        user.password_hash = get_password_hash(new_password)
        self.db.commit()
        return True