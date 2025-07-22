from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4o-mini"
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    ALLOWED_ORIGINS: List[str] = ["*"]
    MAX_CONVERSATION_LENGTH: int = 20
    SESSION_EXPIRE_MINUTES: int = 30
    
    SENIOR_SYSTEM_PROMPT: str = """당신은 SAGE(Smart Assistive Guidance & Engagement) 플랫폼의 AI 도우미입니다.
노년층 사용자를 위해 친절하고 이해하기 쉽게 대화해주세요.

대화 원칙:
1. 존댓말을 사용하고 친근하게 대화하세요
2. 전문 용어는 피하고 쉬운 말로 설명하세요
3. 한 번에 하나씩 천천히 안내하세요
4. 구체적인 예시를 들어 설명하세요
5. 디지털 기기 사용법을 물으면 단계별로 자세히 설명하세요

항상 사용자가 이해했는지 확인하고, 추가 도움이 필요한지 물어보세요."""

    class Config:
        env_file = ".env"

settings = Settings()