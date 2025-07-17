from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.database import Base

class SubscriptionTier(enum.Enum):
    BASIC = 'basic'
    FREE = 'free'

class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.BASIC)
    subscription_status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.INACTIVE)
    daily_usage_count = Column(Integer, default=0)
    last_usage_reset = Column(DateTime, default=datetime.now(tz=timezone.utc))
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))
    modified_at = Column(DateTime, default=datetime.now(tz=timezone.utc), onupdate=datetime.now(tz=timezone.utc))

    chatrooms = relationship('Chatroom', back_populates='user', cascade='all, delete-orphan')
    subscriptions = relationship('Subscription', back_populates='user')