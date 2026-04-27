# Architecture Overview

This project implements a Multimodal RAG (Retrieval-Augmented Generation) system.

## Components

- **Backend**: FastAPI powered server handling orchestration, embeddings, and LLM calls.
- **Frontend**: React application with a premium, responsive UI.
- **Database**: PostgreSQL with pgvector for vector similarity search.
- **Services**:
    - `rag_service`: Orchestrates the retrieval and generation flow.
    - `llm_service`: Manages communication with OpenAI GPT models.
    - `image_service`: Handles image generation via DALL-E.
    - `embedding_service`: Generates vector embeddings for text chunks.
