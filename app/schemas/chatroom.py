from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

class MessageCreate(MessageBase):
    pass

class MessageResponse(BaseModel):
    id: int
    content: str
    is_user_message: bool
    created_at: datetime
    gemini_response: Optional[str] = None
    processing_status: str
    
    class Config:
        from_attributes = True

class ChatroomBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)

class ChatroomCreate(ChatroomBase):
    pass

class ChatroomResponse(ChatroomBase):
    id: int
    user_id: int
    message_count: int
    last_activity: datetime
    created_at: datetime
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True

class ChatroomList(BaseModel):
    chatrooms: List[ChatroomResponse]
    total: int