import os
from typing import List, Optional
from engine.gemini_api import query_gemini
from engine.ollama_api import query_ollama, check_ollama

def get_ollama_model_name() -> Optional[str]:
    # First check env var
    env_model = os.environ.get("OLLAMA_MODEL")
    if env_model:
        return env_model
        
    # Then fallback to checking what's available
    ok, name = check_ollama()
    if ok and "No models" not in name:
        return name
    return None

def generate_answer(question: str, chunks: List[dict]) -> Optional[str]:
    provider = os.environ.get("MODEL_PROVIDER", "ollama").lower()
    
    if provider == "gemini":
        try:
            print("Attempting to query Gemini API...")
            answer = query_gemini(question, chunks)
            if answer:
                return answer
            print("Gemini returned None. Falling back to Ollama.")
        except Exception as e:
            print(f"Gemini API error: {e}. Falling back to Ollama.")
    
    # Fallback or if provider is ollama
    ollama_model = get_ollama_model_name()
    if ollama_model:
        try:
            print(f"Querying Ollama with model: {ollama_model}")
            return query_ollama(ollama_model, question, chunks)
        except Exception as e:
            print(f"Ollama API error: {e}")
    else:
        print("No valid Ollama model found to use.")
        
    return None
