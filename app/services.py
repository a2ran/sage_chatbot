from openai import AsyncOpenAI
from typing import List, Optional, Dict, Any, Tuple
import json
import redis.asyncio as redis
from datetime import datetime, timedelta
import uuid
import logging

from app.models import ChatMessage, MessageRole, ConversationHistory
from app.config import settings

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.redis_client = None
        self.model = settings.OPENAI_MODEL
        
    async def initialize_redis(self):
        try:
            self.redis_client = await redis.from_url(settings.REDIS_URL)
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory storage.")
            self.redis_client = None
    
    async def get_conversation_history(self, session_id: str) -> Optional[ConversationHistory]:
        if not self.redis_client:
            return None
            
        try:
            data = await self.redis_client.get(f"conversation:{session_id}")
            if data:
                return ConversationHistory.model_validate_json(data)
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}")
        return None
    
    async def save_conversation_history(self, history: ConversationHistory):
        if not self.redis_client:
            return
            
        try:
            key = f"conversation:{history.session_id}"
            await self.redis_client.setex(
                key,
                timedelta(minutes=settings.SESSION_EXPIRE_MINUTES),
                history.model_dump_json()
            )
        except Exception as e:
            logger.error(f"Error saving conversation history: {e}")
    
    async def generate_response(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_info: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str, Optional[List[str]]]:
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        history = await self.get_conversation_history(session_id)
        
        if not history:
            history = ConversationHistory(
                session_id=session_id,
                messages=[],
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                user_info=user_info
            )
        
        messages = [
            {"role": "system", "content": settings.SENIOR_SYSTEM_PROMPT}
        ]
        
        for msg in history.messages[-settings.MAX_CONVERSATION_LENGTH:]:
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        messages.append({"role": "user", "content": message})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            assistant_message = response.choices[0].message.content
            
            history.messages.append(ChatMessage(role=MessageRole.USER, content=message))
            history.messages.append(ChatMessage(role=MessageRole.ASSISTANT, content=assistant_message))
            history.last_activity = datetime.utcnow()
            
            await self.save_conversation_history(history)
            
            suggestions = await self.generate_suggestions(assistant_message, user_info)
            
            return assistant_message, session_id, suggestions
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    async def generate_suggestions(
        self,
        last_response: str,
        user_info: Optional[Dict[str, Any]] = None
    ) -> Optional[List[str]]:
        try:
            prompt = f"""이전 응답: {last_response}
            
사용자가 다음에 물어볼 만한 관련 질문 3개를 짧고 간단하게 제안해주세요.
노년층이 이해하기 쉬운 말로 작성하고, 각 질문은 20자 이내로 작성하세요.
JSON 배열 형식으로만 응답하세요."""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates question suggestions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=200
            )
            
            suggestions_text = response.choices[0].message.content
            suggestions = json.loads(suggestions_text)
            
            return suggestions[:3] if isinstance(suggestions, list) else None
            
        except Exception as e:
            logger.warning(f"Error generating suggestions: {e}")
            return None
    
    async def clear_session(self, session_id: str):
        if self.redis_client:
            try:
                await self.redis_client.delete(f"conversation:{session_id}")
            except Exception as e:
                logger.error(f"Error clearing session: {e}")

chat_service = ChatService()