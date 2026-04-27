import asyncio
import argparse
from app.db.postgres import SessionLocal
from app.services.ingestion import process_and_store_document
import uuid

async def main(file_path, title):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    db = SessionLocal()
    try:
        owner_id = uuid.uuid4() # Default owner for script ingestion
        doc = await process_and_store_document(db, title, content, owner_id)
        print(f"Successfully ingested document: {doc.title} (ID: {doc.id})")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest a text file into the RAG system.")
    parser.add_argument("file", help="Path to the text file")
    parser.add_argument("--title", help="Title of the document", default="Ingested Document")
    args = parser.parse_args()
    
    asyncio.run(main(args.file, args.title))
