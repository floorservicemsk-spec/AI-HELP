from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import uuid

from services.rag_service import RAGService
from services.llm_service import LLMService
from database import get_db, ChatLog
from config import settings

router = APIRouter()

# Инициализация сервисов
rag_service = RAGService()
llm_service = LLMService()


class ChatRequest(BaseModel):
    question: str
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    context_sources: List[str]
    conversation_id: str


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Обработка пользовательского вопроса"""
    try:
        # Генерируем user_id если не указан
        user_id = request.user_id or str(uuid.uuid4())
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Поиск релевантных чанков
        context_chunks = rag_service.search(request.question, top_k=5)
        
        # Генерация ответа
        answer = llm_service.generate_response(
            question=request.question,
            context_chunks=context_chunks
        )
        
        # Извлекаем источники контекста
        context_sources = list(set([
            chunk.get("source", "") 
            for chunk in context_chunks 
            if chunk.get("source")
        ]))
        
        # Логируем запрос
        chat_log = ChatLog(
            user_id=user_id,
            question=request.question,
            answer=answer,
            context_used=[chunk.get("text", "") for chunk in context_chunks]
        )
        db.add(chat_log)
        db.commit()
        
        return ChatResponse(
            answer=answer,
            context_sources=context_sources,
            conversation_id=conversation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")
