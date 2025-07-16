import google.generativeai as genai
from typing import Optional
from ..config import settings

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_response(self, prompt: str) -> Optional[str]:
        """Generate response from Gemini API"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None
    
    async def generate_chat_response(self, message: str, context: str = "") -> Optional[str]:
        """Generate chat response with context"""
        try:
            full_prompt = f"Context: {context}\n\nUser: {message}\n\nAssistant:"
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"Gemini chat error: {e}")
            return None