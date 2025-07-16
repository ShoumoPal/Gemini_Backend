from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime, timedelta, timezone
from app.database import Base

class OTP(Base):
    __tablename__ = "otps"
    
    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String, nullable=False)
    otp_code = Column(String, nullable=False)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime, default=lambda: datetime.now(tz=timezone.utc) + timedelta(minutes=5))
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))