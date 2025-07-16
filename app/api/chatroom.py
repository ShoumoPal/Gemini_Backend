from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from ..database import get_db
from ..schemas.chatroom import ChatroomCreate, ChatroomResponse, ChatroomList, MessageCreate, MessageResponse
from ..models.chatroom import Chatroom, Message
from ..middleware.auth_middleware import AuthMiddleware, security
from ..middleware.rate_limit_middleware import RateLimitMiddleware
from ..tasks.gemini_tasks import process_gemini_message

router = APIRouter(prefix="/chatrooms", tags=["Chatrooms"])

@router.post("/", response_model=ChatroomResponse)
async def create_chatroom(
    chatroom_data: ChatroomCreate,
    credentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Create a new chatroom"""
    auth_middleware = AuthMiddleware(None, credentials)
    user = auth_middleware.get_current_user()
    
    chatroom = Chatroom(
        user_id=user.id,
        title=chatroom_data.title
    )
    
    db.add(chatroom)
    db.commit()
    db.refresh(chatroom)
    
    return chatroom

@router.get("/", response_model=ChatroomList)
async def get_chatrooms(
    skip: int = 0,
    limit: int = 20,
    credentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user's chatrooms"""
    auth_middleware = AuthMiddleware(None, credentials)
    user = auth_middleware.get_current_user()
    
    chatrooms = db.query(Chatroom).filter(
        Chatroom.user_id == user.id
    ).order_by(desc(Chatroom.last_activity)).offset(skip).limit(limit).all()
    
    total = db.query(Chatroom).filter(Chatroom.user_id == user.id).count()
    
    return {
        "chatrooms": chatrooms,
        "total": total
    }

@router.get("/{chatroom_id}", response_model=ChatroomResponse)
async def get_chatroom(
    chatroom_id: int,
    credentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get specific chatroom with messages"""
    auth_middleware = AuthMiddleware(None, credentials)
    user = auth_middleware.get_current_user()
    
    chatroom = db.query(Chatroom).filter(
        Chatroom.id == chatroom_id,
        Chatroom.user_id == user.id
    ).first()
    
    if not chatroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatroom not found"
        )
    
    return chatroom

@router.post("/{chatroom_id}/messages", response_model=MessageResponse)
async def send_message(
    chatroom_id: int,
    message_data: MessageCreate,
    background_tasks: BackgroundTasks,
    credentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Send a message to chatroom"""
    auth_middleware = AuthMiddleware(None, credentials)
    user = auth_middleware.get_current_user()
    
    # Check rate limits
    rate_limit = RateLimitMiddleware(user)
    rate_limit.check_daily_limit()
    
    # Verify chatroom ownership
    chatroom = db.query(Chatroom).filter(
        Chatroom.id == chatroom_id,
        Chatroom.user_id == user.id
    ).first()
    
    if not chatroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatroom not found"
        )
    
    # Create message
    message = Message(
        chatroom_id=chatroom_id,
        content=message_data.content,
        is_user_message=True
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Update chatroom stats
    chatroom.message_count += 1
    chatroom.last_activity = message.created_at
    
    # Increment user usage
    rate_limit.increment_usage()
    db.commit()
    
    # Process message with Gemini in background
    background_tasks.add_task(process_gemini_message, message.id)
    
    return message

@router.get("/{chatroom_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    chatroom_id: int,
    skip: int = 0,
    limit: int = 50,
    credentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get messages from chatroom"""
    auth_middleware = AuthMiddleware(None, credentials)
    user = auth_middleware.get_current_user()
    
    # Verify chatroom ownership
    chatroom = db.query(Chatroom).filter(
        Chatroom.id == chatroom_id,
        Chatroom.user_id == user.id
    ).first()
    
    if not chatroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatroom not found"
        )
    
    messages = db.query(Message).filter(
        Message.chatroom_id == chatroom_id
    ).order_by(Message.created_at).offset(skip).limit(limit).all()
    
    return messages

@router.delete("/{chatroom_id}")
async def delete_chatroom(
    chatroom_id: int,
    credentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Delete chatroom and all messages"""
    auth_middleware = AuthMiddleware(None, credentials)
    user = auth_middleware.get_current_user()
    
    chatroom = db.query(Chatroom).filter(
        Chatroom.id == chatroom_id,
        Chatroom.user_id == user.id
    ).first()
    
    if not chatroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatroom not found"
        )
    
    # Delete all messages first
    db.query(Message).filter(Message.chatroom_id == chatroom_id).delete()
    
    # Delete chatroom
    db.delete(chatroom)
    db.commit()
    
    return {"message": "Chatroom deleted successfully"}

@router.put("/{chatroom_id}", response_model=ChatroomResponse)
async def update_chatroom(
    chatroom_id: int,
    chatroom_data: ChatroomCreate,
    credentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Update chatroom title"""
    auth_middleware = AuthMiddleware(None, credentials)
    user = auth_middleware.get_current_user()
    
    chatroom = db.query(Chatroom).filter(
        Chatroom.id == chatroom_id,
        Chatroom.user_id == user.id
    ).first()
    
    if not chatroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatroom not found"
        )
    
    chatroom.title = chatroom_data.title
    db.commit()
    db.refresh(chatroom)
    
    return chatroom