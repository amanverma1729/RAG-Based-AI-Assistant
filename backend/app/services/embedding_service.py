import logging
from typing import List
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI Client if API key is present
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

async def generate_embeddings(texts: List[str], model: str = "text-embedding-3-small") -> List[List[float]]:
    """Generates embeddings for a batch of texts using OpenAI."""
    if not client:
        raise ValueError("OPENAI_API_KEY is not configured.")
    try:
        response = await client.embeddings.create(input=texts, model=model)
        # Sort to ensure indices match the input list
        sorted_response = sorted(response.data, key=lambda x: x.index)
        return [data.embedding for data in sorted_response]
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise e
