import pdfplumber
import pypdf
from typing import Tuple, List, Dict
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP

def extract_text(pdf_path: str) -> Tuple[List[Tuple[int, str]], int]:
    """Extracts text from a PDF file using pdfplumber, falling back to pypdf."""
    pages_text = []
    
    # Try with pdfplumber first
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                t = page.extract_text()
                if t and t.strip():
                    pages_text.append((i + 1, t.strip()))
        if pages_text:
            return pages_text, len(pages_text)
    except Exception:
        pass

    # Fallback to pypdf
    try:
        reader = pypdf.PdfReader(pdf_path)
        for i, page in enumerate(reader.pages):
            t = page.extract_text()
            if t and t.strip():
                pages_text.append((i + 1, t.strip()))
    except Exception:
        pass

    return pages_text, len(pages_text)

def make_chunks(pages_text: List[Tuple[int, str]]) -> List[Dict]:
    """Splits text into chunks of specified size and overlap."""
    chunks = []
    for page_num, text in pages_text:
        words = text.split()
        i = 0
        while i < len(words):
            chunk_words = words[i : i + CHUNK_SIZE]
            chunk_text  = " ".join(chunk_words)
            if len(chunk_text.strip()) > 50:
                chunks.append({"text": chunk_text, "page": page_num})
            i += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks
