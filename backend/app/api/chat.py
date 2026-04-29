from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from app.api.dependencies import get_db
from app.models.request import ChatRequest
from app.models.response import ChatResponse
from app.services.rag_service import rag_service
from app.utils.helpers import get_timestamp

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Standard RAG chat endpoint.
    """
    try:
        owner_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
        
        answer, sources = await rag_service.answer_query(payload.message, db=db, owner_id=owner_id)
        
        conv_id = payload.conversation_id or uuid.uuid4()
        
        # Format sources into the list of dicts expected by the frontend
        formatted_sources = [{"id": s} for s in sources]
        
        return ChatResponse(
            answer=answer,
            sources=formatted_sources,
            conversation_id=conv_id,
            created_at=get_timestamp()
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

import logging
logger = logging.getLogger(__name__)
