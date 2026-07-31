import asyncio
from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from webapp.app.middleware import InProcessRateLimiter
from webapp.app.services.token_service import TokenService, get_token_service
from webapp.main import (
    app,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_token_service():
    service = TokenService()
    app.dependency_overrides[get_token_service] = lambda: service
    app.state.rate_limiter.reset()
    app.state.rate_limiter.limit = 60
    yield
    app.dependency_overrides.clear()
    app.state.rate_limiter.reset()


def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_serves_landing_page():
    response = client.get("/")

    assert response.status_code == 200
    assert "Codespaces & FastAPI" in response.text


def test_http_exception_handler_returns_detail():
    response = asyncio.run(
        http_exception_handler(None, HTTPException(status_code=418, detail="teapot"))
    )

    assert response.status_code == 418
    assert response.body == b'{"detail":"teapot"}'


def test_validation_exception_handler_returns_errors():
    error = Mock()
    error.errors.return_value = [{"loc": ["body"], "msg": "invalid"}]

    response = asyncio.run(validation_exception_handler(None, error))

    assert response.status_code == 422
    assert response.body == (
        b'{"detail":"Request validation failed","errors":'
        b'[{"loc":["body"],"msg":"invalid"}]}'
    )


def test_unhandled_exception_handler_returns_safe_response():
    response = asyncio.run(
        unhandled_exception_handler(None, RuntimeError("internal failure"))
    )

    assert response.status_code == 500
    assert response.body == b'{"detail":"An unexpected server error occurred."}'


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


@pytest.mark.parametrize("length", [0, 89, "invalid"])
def test_generate_rejects_invalid_length(length):
    response = client.post("/generate", json={"length": length})

    assert response.status_code == 422
    assert response.json()["detail"] == "Request validation failed"


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


def test_rate_limit_returns_retry_information():
    app.state.rate_limiter.limit = 1

    assert client.get("/ping").status_code == 200
    limited_response = client.get("/ping")
    assert limited_response.status_code == 429
    assert limited_response.json()["detail"] == (
        "Rate limit exceeded. Please retry later."
    )
    assert limited_response.headers["Retry-After"] == "60"
    assert limited_response.headers["X-RateLimit-Remaining"] == "0"


def test_token_service_dependency_returns_singleton():
    assert get_token_service() is not None


def test_rate_limiter_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        InProcessRateLimiter(limit=0)

    with pytest.raises(ValueError):
        InProcessRateLimiter(window=0)


def test_rate_limiter_expires_old_requests(mocker):
    mocker.patch(
        "webapp.app.middleware.monotonic",
        side_effect=[0.0, 2.0],
    )
    limiter = InProcessRateLimiter(limit=1, window=1.0)

    assert limiter.check("client") == (True, 0)
    assert limiter.check("client") == (True, 0)
