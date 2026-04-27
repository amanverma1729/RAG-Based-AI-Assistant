import logging
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

async def generate_image(prompt: str) -> str:
    """
    Generates an image via DALL-E 3 based on the user's prompt.
    Returns the URL of the generated image.
    """
    if not client:
        raise ValueError("OPENAI_API_KEY is not configured for image generation.")
        
    try:
        response = await client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url
    except Exception as e:
        logger.error(f"Error generating image with DALL-E 3: {e}")
        raise e
