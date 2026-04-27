from pydantic import BaseModel, UUID4
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[UUID4] = None

class ImageRequest(BaseModel):
    prompt: str

class IngestRequest(BaseModel):
    url: Optional[str] = None
