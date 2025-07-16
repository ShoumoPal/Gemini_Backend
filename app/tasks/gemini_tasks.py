from celery import Celery
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..services.gemini_service import GeminiService
from ..models.chatroom import Message
from ..config import settings

celery_app = Celery('gemini_tasks', broker=settings.redis_url)

@celery_app.task
def process_gemini_message(message_id: int):
    """Process message with Gemini API"""
    db: Session = SessionLocal()
    try:
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            return
        
        # Update status to processing
        message.processing_status = "processing"
        db.commit()
        
        # Get Gemini response
        gemini_service = GeminiService()
        response = gemini_service.generate_response(message.content)
        
        if response:
            message.gemini_response = response
            message.processing_status = "completed"
        else:
            message.processing_status = "failed"
        
        db.commit()
        
    except Exception as e:
        print(f"Gemini task error: {e}")
        message.processing_status = "failed"
        db.commit()
    finally:
        db.close()