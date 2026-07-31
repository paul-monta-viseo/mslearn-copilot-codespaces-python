import pytest
from fastapi.testclient import TestClient

from webapp.app.services.user_service import (
    UserService,
    get_user_service,
    user_service,
)
from webapp.main import app


@pytest.fixture(autouse=True)
def fresh_user_service():
    """Replace the singleton with a clean UserService for every test."""
    service = UserService()
    app.dependency_overrides[get_user_service] = lambda: service
    yield service
    app.dependency_overrides.clear()
    app.state.rate_limiter.reset()
    app.state.rate_limiter.limit = 60


client = TestClient(app)

USER_PAYLOAD = {"name": "Alice", "email": "alice@example.com"}


def test_create_user():
    response = client.post("/users", json=USER_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data


def test_list_users_empty():
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json() == []


def test_list_users_after_create():
    client.post("/users", json=USER_PAYLOAD)
    response = client.get("/users")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_user():
    created = client.post("/users", json=USER_PAYLOAD).json()
    response = client.get(f"/users/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_user_not_found():
    response = client.get("/users/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_update_user():
    created = client.post("/users", json=USER_PAYLOAD).json()
    response = client.put(f"/users/{created['id']}", json={"name": "Bob"})
    assert response.status_code == 200
    assert response.json()["name"] == "Bob"
    assert response.json()["email"] == "alice@example.com"


def test_update_user_not_found():
    response = client.put(
        "/users/00000000-0000-0000-0000-000000000000", json={"name": "Bob"}
    )
    assert response.status_code == 404


def test_delete_user():
    created = client.post("/users", json=USER_PAYLOAD).json()
    response = client.delete(f"/users/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/users/{created['id']}").status_code == 404


def test_delete_user_not_found():
    response = client.delete("/users/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_user_invalid_email(mocker):
    response = client.post("/users", json={"name": "Bad", "email": "not-an-email"})
    assert response.status_code == 422
    assert response.json()["detail"] == "Request validation failed"


def test_get_user_invalid_identifier():
    response = client.get("/users/not-a-uuid")

    assert response.status_code == 422
    assert response.json()["detail"] == "Request validation failed"


def test_user_service_dependency_returns_singleton():
    assert get_user_service() is user_service
