import logging
from sqlalchemy.orm import Session
from app.services.llm_service import generate_rag_response_stream
import uuid
import json

logger = logging.getLogger(__name__)

class RAGService:
    async def answer_query(self, query: str, db: Session = None, owner_id: uuid.UUID = None):
        """
        Orchestrates the RAG flow and returns a consolidated response.
        """
        full_answer = ""
        sources = []
        
        if not owner_id:
            owner_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
            
        if not db:
            from app.db.postgres import SessionLocal
            db = SessionLocal()
            try:
                async for chunk in generate_rag_response_stream(db, query, owner_id):
                    if chunk.startswith("data: "):
                        try:
                            data = json.loads(chunk[6:])
                            if data.get("type") == "token":
                                full_answer += data["data"]
                            elif data.get("type") == "sources":
                                sources = data["data"]
                        except:
                            pass
            finally:
                db.close()
        else:
            async for chunk in generate_rag_response_stream(db, query, owner_id):
                if chunk.startswith("data: "):
                    try:
                        data = json.loads(chunk[6:])
                        if data.get("type") == "token":
                            full_answer += data["data"]
                        elif data.get("type") == "sources":
                            sources = data["data"]
                    except:
                        pass
                        
        return full_answer, sources

rag_service = RAGService()
