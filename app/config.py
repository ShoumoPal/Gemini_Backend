from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL : str
    REDIS_URL : str
    JWT_SECRET_KEY : str
    JWT_ALGORITHM : str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES : int = 30
    REFRESH_TOKEN_EXPIRE_DAYS : int = 7
    GEMINI_API_KEY : str
    STRIPE_SECRET_KEY : str
    STRIPE_WEBHOOK_SECRET: str
    OTP_EXPIRATION_MINUTES : int = 5

    class Config:
        env_file = 'app/.env'

settings = Settings()