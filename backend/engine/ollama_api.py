import requests
from typing import Tuple, Optional, List
from config.settings import OLLAMA_URL

def check_ollama() -> Tuple[bool, str]:
    """Checks if Ollama is running and finds the best available model."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        if r.status_code == 200:
            models = r.json().get("models", [])
            if models:
                # Prefer certain models in order
                preferred = ["llama3", "llama3.2", "llama3.1", "mistral", "phi3",
                             "phi", "gemma", "neural-chat", "qwen"]
                names = [m["name"] for m in models]
                for pref in preferred:
                    for n in names:
                        if pref in n.lower():
                            return True, n
                return True, names[0]
            return True, "No models pulled"
    except Exception:
        pass
    return False, "Ollama not running"

def build_context(chunks: List[dict]) -> str:
    """Builds a formatted string of context from PDF chunks."""
    parts = []
    for chunk in chunks:
        parts.append(f"[From: {chunk['filename']}, Page {chunk['page']}]\n{chunk['text']}")
    return "\n\n---\n\n".join(parts)

def query_ollama(model_name: str, question: str, chunks: List[dict]) -> Optional[str]:
    """Queries the Ollama LLM with context to get an answer."""
    context = build_context(chunks)
    prompt = f"""You are a helpful assistant answering questions about PDF documents.

RELEVANT CONTENT FROM PDFs:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
- Answer based only on the provided content
- Be clear and concise
- Mention which document/page the info came from when relevant
- If answer is not in content, say so clearly
- Respond in the same language as the question (Hindi or English)

ANSWER:"""

    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": False},
            timeout=120
        )
        if r.status_code == 200:
            ans = r.json().get("response", "").strip()
            if ans:
                return f"🤖 **[Ollama: {model_name}]**\n\n{ans}"
    except Exception:
        pass
    return None
