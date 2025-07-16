from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Chatroom(Base):
    __tablename__ = 'chatrooms'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    message_count = Column(Integer, default=0)
    last_activity = Column(DateTime, default=datetime.now(tz=timezone.utc))
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))
    modified_at = Column(DateTime, default=datetime.now(tz=timezone.utc), onupdate=datetime.now(tz=timezone.utc))

    user = relationship('User', back_populates='chatrooms')
    messages = relationship('Message', back_populates='chatroom', cascade='all, delete-orphan')

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True)
    chatroom_id = Column(Integer, ForeignKey('chatrooms.id'))
    content = Column(Text, nullable=False)
    is_user_message = Column(Boolean, default=True)
    gemini_response = Column(Text, nullable=True)
    processing_status = Column(String, default='Pending..')
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))

    chatroom = relationship('Chatroom', back_populates='messages')