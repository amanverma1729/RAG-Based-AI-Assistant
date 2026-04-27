from app.services.retrieval import RetrievalService
from app.services.llm_service import LLMOrchestrator
from app.services.image_service import ImageGenerationService

class RAGService:
    def __init__(self):
        self.retrieval = RetrievalService()
        self.llm = LLMOrchestrator()
        self.image_gen = ImageGenerationService()

    async def answer_query(self, query: str):
        # 1. Retrieve context
        context = await self.retrieval.get_context(query)
        
        # 2. Generate response using LLM
        response = await self.llm.generate_response(query, context)
        
        return response

rag_service = RAGService()
