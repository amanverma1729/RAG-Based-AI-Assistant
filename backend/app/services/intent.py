import logging
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

async def classify_intent(query: str) -> str:
    """
    Classifies the user's query into 'TEXT' or 'IMAGE'.
    - TEXT: Informational requests, questions, or document lookups.
    - IMAGE: Creative requests to generate, draw, or visualize something.
    """
    if not client:
        # Fallback to simple keyword matching if no API key
        query_lower = query.lower()
        if any(word in query_lower for word in ["generate", "draw", "picture", "image", "visualize"]):
            return "IMAGE"
        return "TEXT"

    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Classify the user's intent into exactly one word: 'TEXT' or 'IMAGE'. "
                                             "TEXT: asking for information, summarization, or chat. "
                                             "IMAGE: requesting to create a new visual asset, draw, or generate an image."},
                {"role": "user", "content": query}
            ],
            temperature=0,
            max_tokens=10
        )
        intent = response.choices[0].message.content.strip().upper()
        return "IMAGE" if "IMAGE" in intent else "TEXT"
    except Exception as e:
        logger.error(f"Error classifying intent: {e}")
        return "TEXT" # Default to text
