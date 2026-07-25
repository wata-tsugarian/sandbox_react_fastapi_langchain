from fastapi.testclient import TestClient
from app.main import app

test_client = TestClient(app)


def test_read_root():
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Hello, World!"


def test_healthz():
    response = test_client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
