import logging
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models import DocumentChunk, Document
from app.services.embedding_service import generate_embeddings

logger = logging.getLogger(__name__)

class VectorStore:
    async def similarity_search(self, db: Session, query: str, owner_id: uuid.UUID, top_k: int = 5) -> list[DocumentChunk]:
        """
        Implements HNSW (Hierarchical Navigable Small World) ANN search via pgvector.
        """
        try:
            query_embeddings = await generate_embeddings([query])
            query_embedding = query_embeddings[0]
        except Exception as e:
            logger.error(f"Failed to embed search query: {e}")
            return []

        stmt = (
            select(DocumentChunk)
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(Document.owner_id == owner_id)
            .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        
        try:
            results = db.execute(stmt).scalars().all()
            return list(results)
        except Exception as e:
            logger.error(f"Database error during retrieval: {e}")
            return []

vector_store = VectorStore()
