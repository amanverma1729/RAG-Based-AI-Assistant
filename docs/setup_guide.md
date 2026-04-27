# Setup Guide

## Prerequisites
- Docker & Docker Compose
- OpenAI API Key

## Local Setup
1. Clone the repository.
2. Create a `.env` file in the `backend` directory.
3. Add your `OPENAI_API_KEY`.
4. Run `docker-compose up`.

## Manual Setup
1. **Backend**:
    - `cd backend`
    - `pip install -r requirements.txt`
    - `uvicorn app.main:app --reload`
2. **Frontend**:
    - `cd frontend`
    - `npm install`
    - `npm run dev`
