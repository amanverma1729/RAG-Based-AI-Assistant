# API Documentation

## Endpoints

### Chat
- **POST** `/api/v1/chat`
    - Request Body: `{"message": "string", "conversation_id": "uuid"}`
    - Response: `{"answer": "string", "sources": [], "conversation_id": "uuid"}`

### Images
- **POST** `/api/v1/images`
    - Request Body: `{"prompt": "string"}`
    - Response: `{"image_url": "string"}`

### Health
- **GET** `/health`
    - Response: `{"status": "healthy"}`
