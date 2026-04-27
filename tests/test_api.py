from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "Multimodal RAG"}

def test_chat_endpoint():
    # Mocking or DB setup needed for a real test
    pass
