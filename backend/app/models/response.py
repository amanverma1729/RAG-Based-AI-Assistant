from pydantic import BaseModel, UUID4
from typing import List, Optional
from datetime import datetime

class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[dict]] = []
    conversation_id: UUID4
    created_at: datetime

class ImageResponse(BaseModel):
    image_url: str
    revised_prompt: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    service: str
