import logging
import json
import uuid
import time
from typing import AsyncGenerator
from openai import AsyncOpenAI
import litellm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.retrieval import search_documents
from app.services.evaluation import eval_logger
from app.services.intent import classify_intent
from app.services.image_service import ImageGenerationService

logger = logging.getLogger(__name__)

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

async def generate_rag_response_stream(
    db: Session, 
    query: str, 
    owner_id: uuid.UUID, 
    conversation_history: list[dict] = None,
    use_local_llm: bool = False
) -> AsyncGenerator[str, None]:
    """
    Multimodal Orchestrator:
    1. Detects Intent (Text vs Image).
    2. Routes to appropriate generator.
    3. Handles RAG for text or DALL-E for images.
    """
    
    # --- PHASE 1: INTENT CLASSIFICATION ---
    intent = await classify_intent(query)
    
    if intent == "IMAGE":
        yield f"data: {json.dumps({'type': 'status', 'data': 'Generating your image...'})}\n\n"
        try:
            image_gen = ImageGenerationService()
            image_url = await image_gen.generate_image(query)
            yield f"data: {json.dumps({'type': 'image', 'data': image_url})}\n\n"
            yield "data: [DONE]\n\n"
            return
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            yield f"data: {json.dumps({'type': 'error', 'data': 'Failed to generate image. Please try again.'})}\n\n"
            yield "data: [DONE]\n\n"
            return

    # --- PHASE 2: DOCUMENT RETRIEVAL (TEXT INTENT) ---
    if not use_local_llm and not openai_client:
        logger.warning("OPENAI_API_KEY not configured, falling back to local LLM.")
        use_local_llm = True
        
    relevant_chunks = await search_documents(db, query, owner_id, top_k=5)
    
    # Context Assembly
    context_text = "\n\n---\n\n".join([
        f"Source ID: {chunk.id}\nContent: {chunk.content}" 
        for chunk in relevant_chunks
    ])
    
    # Research-grade Grounded Prompt
    system_message = f"""You are a senior Research Assistant for the Multimodal RAG Project.
Your goal is to provide highly accurate, grounded answers based ONLY on the provided context.

GUIDELINES:
1. Cite information using [Source: ID].
2. If the context is insufficient, state: "The provided academic context does not contain sufficient data to answer the query."
3. Maintain a formal, academic tone.
4. If there are conflicting sources, mention both perspectives.

<academic_context>
{context_text}
</academic_context>
"""

    messages = [{"role": "system", "content": system_message}]
    
    if conversation_history:
        messages.extend(conversation_history[-5:])
        
    messages.append({"role": "user", "content": query})
    
    # --- PHASE 3: RESPONSE STREAMING ---
    start_time = time.time()
    source_ids = [str(c.id) for c in relevant_chunks]
    yield f"data: {json.dumps({'type': 'sources', 'data': source_ids})}\n\n"
    
    full_answer = ""
    
    try:
        if use_local_llm:
            response = await litellm.acompletion(
                model="ollama/llama3",
                messages=messages,
                api_base=settings.OLLAMA_BASE_URL,
                stream=True
            )
            async for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_answer += content
                    yield f"data: {json.dumps({'type': 'token', 'data': content})}\n\n"
        else:
            response = await openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.1, # Lower temperature for research accuracy
                stream=True
            )
            async for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_answer += content
                    yield f"data: {json.dumps({'type': 'token', 'data': content})}\n\n"
                    
    except Exception as e:
        logger.error(f"Error generating LLM response: {e}")
        yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"
        
    yield "data: [DONE]\n\n"

    # --- PHASE 4: LOGGING & EVALUATION ---
    end_time = time.time()
    eval_logger.log_trace(
        query=query,
        contexts=[c.content for c in relevant_chunks],
        answer=full_answer,
        latency_ms=round((end_time - start_time) * 1000, 2)
    )

async def generate_baseline_response(query: str) -> str:
    """
    Generates a response WITHOUT any external context.
    Used for 'Research Comparison' to show baseline model performance vs. RAG.
    """
    if not openai_client:
        return "Baseline comparison requires an active OpenAI client."
    
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Answer the user's query from your internal knowledge only."},
                {"role": "user", "content": query}
            ],
            temperature=0.7, # Higher temp for baseline to show variability
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in baseline generation: {e}")
        return f"Error: {e}"
