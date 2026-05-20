import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
import os
from typing import Tuple, List, Dict
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP

# Automatically configure Tesseract path for Windows if it's installed in the default location
if os.name == 'nt':
    default_tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(default_tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = default_tesseract_path

def extract_text(pdf_path: str) -> Tuple[List[Tuple[int, str]], int]:
    """Extracts text from a PDF file using PyMuPDF.
       If a page has no text, falls back to OCR using pytesseract.
    """
    pages_text = []
    
    try:
        doc = fitz.open(pdf_path)
        
        for i, page in enumerate(doc):
            # Try getting text normally
            t = page.get_text()
            if t and t.strip():
                pages_text.append((i + 1, t.strip()))
            else:
                # Fallback to OCR for this page
                try:
                    pix = page.get_pixmap(dpi=300)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    text = pytesseract.image_to_string(img)
                    if text and text.strip():
                        pages_text.append((i + 1, text.strip()))
                except Exception as e:
                    print(f"OCR failed on page {i+1} for {pdf_path}: {e}")
                
        return pages_text, len(doc)
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return pages_text, 0

def make_chunks(pages_text: List[Tuple[int, str]]) -> List[Dict]:
    """Splits text into chunks of specified size and overlap, preferring sentence boundaries."""
    chunks = []
    for page_num, text in pages_text:
        # Simple sentence splitting using regex (split by ., !, ?)
        # Using a lookbehind to keep the punctuation with the sentence
        # but Python's re doesn't support variable length lookbehinds easily.
        # Let's split and then combine if needed, or just use a simple regex.
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_words = sentence.split()
            if not sentence_words:
                continue
                
            if current_length + len(sentence_words) > CHUNK_SIZE and current_chunk:
                chunk_text = " ".join(current_chunk)
                if len(chunk_text.strip()) > 50:
                    chunks.append({"text": chunk_text, "page": page_num})
                
                # Keep some overlap
                overlap_words = 0
                overlap_chunk = []
                for s in reversed(current_chunk):
                    s_words = s.split()
                    if overlap_words + len(s_words) <= CHUNK_OVERLAP:
                        overlap_chunk.insert(0, s)
                        overlap_words += len(s_words)
                    else:
                        break
                        
                current_chunk = overlap_chunk
                current_length = sum(len(s.split()) for s in current_chunk)
                
            current_chunk.append(sentence)
            current_length += len(sentence_words)
            
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            if len(chunk_text.strip()) > 50:
                chunks.append({"text": chunk_text, "page": page_num})
                
    return chunks
