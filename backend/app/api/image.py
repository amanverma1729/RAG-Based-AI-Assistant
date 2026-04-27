from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.image_gen import generate_image

router = APIRouter()

class ImageRequest(BaseModel):
    prompt: str

@router.post("/generate")
async def create_image(payload: ImageRequest):
    """Generates an image from a prompt via DALL-E 3."""
    try:
        image_url = await generate_image(payload.prompt)
        return {"url": image_url, "prompt": payload.prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
