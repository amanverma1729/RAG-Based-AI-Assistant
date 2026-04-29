from fastapi import APIRouter, HTTPException
from app.models.request import ImageRequest
from app.models.response import ImageResponse
from app.services.image_service import ImageGenerationService

router = APIRouter()
image_service = ImageGenerationService()

@router.post("/", response_model=ImageResponse)
async def create_image(payload: ImageRequest):
    """Generates an image from a prompt."""
    try:
        image_url = await image_service.generate_image(payload.prompt)
        return ImageResponse(image_url=image_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
