from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_search():
    response = client.post("/search", json={
        "text": "example query",
        "top_k": 5,
        "threshold": 0.5,
        "user_id": "test_user"
    })
    assert response.status_code == 200
    assert isinstance(response.json(), list)