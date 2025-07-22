from fastapi import APIRouter, HTTPException, status
from typing import Optional
from datetime import datetime
import logging

from app.models import ChatRequest, ChatResponse, ErrorResponse
from app.services import chat_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.on_event("startup")
async def startup_event():
    await chat_service.initialize_redis()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        if not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="메시지가 비어있습니다"
            )
        
        response_text, session_id, suggestions = await chat_service.generate_response(
            message=request.message,
            session_id=request.session_id,
            user_info=request.user_info
        )
        
        return ChatResponse(
            message=response_text,
            session_id=session_id,
            timestamp=datetime.utcnow(),
            suggestions=suggestions
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="챗봇 응답 생성 중 오류가 발생했습니다"
        )

@router.delete("/chat/{session_id}")
async def clear_chat_history(session_id: str):
    try:
        await chat_service.clear_session(session_id)
        return {"message": "대화 기록이 삭제되었습니다", "session_id": session_id}
    except Exception as e:
        logger.error(f"Clear history error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="대화 기록 삭제 중 오류가 발생했습니다"
        )

@router.get("/chat/{session_id}/history")
async def get_chat_history(session_id: str):
    try:
        history = await chat_service.get_conversation_history(session_id)
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="대화 기록을 찾을 수 없습니다"
            )
        return history
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get history error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="대화 기록 조회 중 오류가 발생했습니다"
        )

chat_router = router