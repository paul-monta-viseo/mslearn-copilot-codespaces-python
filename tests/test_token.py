import pytest
from fastapi.testclient import TestClient

from webapp.main import app

client = TestClient(app)


def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_default_length():
    response = client.post("/generate", json={})
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert len(data["token"]) == 20


def test_generate_custom_length():
    response = client.post("/generate", json={"length": 10})
    assert response.status_code == 200
    assert len(response.json()["token"]) == 10


def test_generate_mocked_service(mocker):
    mocker.patch(
        "webapp.app.services.token_service.TokenService.generate",
        return_value="mocked-token",
    )
    response = client.post("/generate", json={"length": 12})
    assert response.status_code == 200
    assert response.json()["token"] == "mocked-token"
