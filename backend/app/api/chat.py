from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import uuid
import json
from app.api.dependencies import get_db
from app.services.llm_orchestrator import generate_rag_response_stream, generate_baseline_response
from app.services.evaluation import eval_logger
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    owner_id: str
    conversation_id: str | None = None
    use_local_llm: bool = False

@router.post("/stream")
async def chat_stream(request: Request, payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Streams the LLM generation back to the frontend using SSE (Server-Sent Events).
    """
    owner_uuid = uuid.UUID(payload.owner_id)
    
    # History fetching would go here using conversation_id
    history = []
    
    return StreamingResponse(
        generate_rag_response_stream(
            db=db,
            query=payload.query,
            owner_id=owner_uuid,
            conversation_history=history,
            use_local_llm=payload.use_local_llm
        ),
        media_type="text/event-stream"
    )

@router.post("/compare")
async def chat_compare(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Side-by-side comparison of RAG vs. No-RAG (Baseline).
    Returns a unified JSON object with metrics.
    """
    owner_uuid = uuid.UUID(payload.owner_id)
    
    # 1. Run RAG (We'll consume the generator for this non-streaming endpoint)
    rag_gen = generate_rag_response_stream(db, payload.query, owner_uuid)
    rag_answer = ""
    sources = []
    
    async for chunk in rag_gen:
        if chunk.startswith("data: "):
            try:
                data = json.loads(chunk[6:])
                if data["type"] == "token":
                    rag_answer += data["data"]
                elif data["type"] == "sources":
                    sources = data["data"]
            except:
                pass

    # 2. Run Baseline (No-RAG)
    baseline_answer = await generate_baseline_response(payload.query)

    # 3. Calculate Research Delta
    comparison = eval_logger.compare_rag_impact(payload.query, rag_answer, baseline_answer)

    return {
        "rag_answer": rag_answer,
        "baseline_answer": baseline_answer,
        "sources": sources,
        "comparison_metrics": comparison
    }
