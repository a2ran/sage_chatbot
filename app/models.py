from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_info: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "스마트폰에서 사진을 찍는 방법을 알려주세요",
                "session_id": "user123",
                "user_info": {
                    "age": 75,
                    "tech_level": "beginner"
                }
            }
        }

class ChatResponse(BaseModel):
    message: str
    session_id: str
    timestamp: datetime
    suggestions: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "네, 스마트폰으로 사진 찍는 방법을 알려드릴게요. 먼저 화면에서 카메라 앱을 찾아주세요.",
                "session_id": "user123",
                "timestamp": "2024-01-20T10:30:00Z",
                "suggestions": ["카메라 앱이 어디있나요?", "찍은 사진은 어디서 보나요?"]
            }
        }

class ConversationHistory(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    created_at: datetime
    last_activity: datetime
    user_info: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime
    version: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)