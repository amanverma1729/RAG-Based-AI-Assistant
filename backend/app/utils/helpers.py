import uuid
from datetime import datetime

def generate_uuid():
    return str(uuid.uuid4())

def get_timestamp():
    return datetime.utcnow().isoformat()

def format_source(chunk):
    return {
        "content": chunk.content[:100] + "...",
        "metadata": chunk.metadata,
        "document_id": str(chunk.document_id)
    }
