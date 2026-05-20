from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
import shutil

# Ensure the backend directory is in the python path regardless of where it's run from
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from engine.ai_engine import OfflineAIEngine
from engine.ollama_api import check_ollama

app = FastAPI(title="PDF Intelligence Pro API")

# Setup CORS to allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = OfflineAIEngine()

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ChatRequest(BaseModel):
    question: str
    active_slots: List[int]

@app.get("/status")
def get_status():
    """Check AI model and Ollama status."""
    model_ready = engine.model is not None
    ollama_ok, ollama_name = check_ollama()
    return {
        "model_loaded": model_ready,
        "ollama_available": ollama_ok,
        "ollama_model": ollama_name if "No models" not in ollama_name else None
    }

from fastapi import BackgroundTasks

@app.post("/load_model")
def load_model(background_tasks: BackgroundTasks):
    """Load the sentence-transformer model into memory in the background."""
    if engine.model is not None:
        return {"message": "Model already loaded"}
    
    background_tasks.add_task(engine.load_model)
    return {"message": "Model is loading in the background..."}

@app.post("/upload")
async def upload_pdf(slot_index: int = Form(...), file: UploadFile = File(...)):
    """Upload a PDF and index it in the specified slot."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    success, result = engine.index_pdf(slot_index, file_path)
    if not success:
        raise HTTPException(status_code=500, detail=result)
    
    return {"message": "PDF loaded successfully", "data": result}

@app.post("/chat")
def chat(request: ChatRequest):
    """Ask a question based on active slots."""
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    answer = engine.answer(request.question, request.active_slots)
    return {"answer": answer}

@app.delete("/remove/{slot_index}")
def remove_pdf(slot_index: int):
    """Remove a PDF from a slot."""
    engine.remove_pdf(slot_index)
    return {"message": f"Slot {slot_index} cleared"}

@app.delete("/clear_all")
def clear_all():
    """Clear all PDFs."""
    for i in range(5):
        engine.remove_pdf(i)
    # Also clean up uploads folder
    for f in os.listdir(UPLOAD_DIR):
        os.remove(os.path.join(UPLOAD_DIR, f))
    return {"message": "All PDFs cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
