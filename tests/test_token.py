import pytest
from fastapi.testclient import TestClient

from webapp.app.services.token_service import TokenService, get_token_service
from webapp.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_token_service():
    service = TokenService()
    app.dependency_overrides[get_token_service] = lambda: service
    yield
    app.dependency_overrides.clear()


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


def test_list_tokens_empty():
    response = client.get("/token")

    assert response.status_code == 200
    assert response.json() == {
        "items": [],
        "total": 0,
        "page": 1,
        "page_size": 20,
        "total_pages": 0,
    }


def test_list_tokens_custom_page():
    generated = [
        client.post("/generate", json={"length": 8}).json()["token"]
        for _ in range(5)
    ]

    response = client.get("/token", params={"page": 2, "page_size": 2})

    assert response.status_code == 200
    assert response.json() == {
        "items": generated[2:4],
        "total": 5,
        "page": 2,
        "page_size": 2,
        "total_pages": 3,
    }


def test_list_tokens_page_beyond_range():
    client.post("/generate", json={"length": 8})

    response = client.get("/token", params={"page": 2, "page_size": 20})

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total_pages"] == 1


@pytest.mark.parametrize(
    "params",
    [
        {"page": 0},
        {"page_size": 0},
        {"page_size": 101},
    ],
)
def test_list_tokens_rejects_invalid_pagination(params):
    response = client.get("/token", params=params)

    assert response.status_code == 422


def test_token_openapi_documents_pagination():
    schema = client.get("/openapi.json").json()
    operation = schema["paths"]["/token"]["get"]
    parameters = {parameter["name"]: parameter for parameter in operation["parameters"]}

    assert parameters["page"]["required"] is False
    assert parameters["page_size"]["required"] is False
    assert operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/PaginatedResponse"
    )
