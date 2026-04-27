from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
import uuid
from app.api.dependencies import get_db
from app.services.ingestion import process_and_store_document
import PyPDF2
from io import BytesIO

router = APIRouter()

@router.post("/document")
async def ingest_document(
    title: str = Form(...),
    owner_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Accepts PDF files, extracts text, chunks it, embeds it, and saves to pgvector.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported currently.")
        
    try:
        contents = await file.read()
        pdf_reader = PyPDF2.PdfReader(BytesIO(contents))
        text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
            
        doc = await process_and_store_document(
            db=db,
            title=title,
            content=text,
            owner_id=uuid.UUID(owner_id),
            source_uri=file.filename
        )
        
        return {"message": "Document ingested successfully", "document_id": str(doc.id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest document: {e}")
