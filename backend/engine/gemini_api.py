import os
import google.generativeai as genai
from typing import List, Optional
from engine.ollama_api import build_context

def query_gemini(question: str, chunks: List[dict]) -> Optional[str]:
    """Queries the Gemini API with context to get an answer."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY is not set in environment.")
        return None

    try:
        genai.configure(api_key=api_key)
        
        # Using gemini-1.5-flash as requested
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        context = build_context(chunks)
        
        prompt = f"""You are a helpful AI assistant.

Use ONLY the provided context to answer.

If the answer is not present in context, say:
"I could not find relevant information."

Context:
{context}

Question:
{question}
"""

        # Gemini API call with safety settings/config can be added if needed
        # Robust exception handling is key
        response = model.generate_content(
            prompt,
            # Adjust timeout/retries via requests if needed, but google-generativeai handles it mostly internally.
            # We can rely on a try-except block to catch timeouts or other issues.
        )
        
        if response and response.text:
            return f"🌟 **[Gemini 1.5 Flash]**\n\n{response.text.strip()}"
        
        return None
    except Exception as e:
        print(f"Error querying Gemini API: {e}")
        return None
