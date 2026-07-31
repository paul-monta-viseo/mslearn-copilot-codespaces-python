from fastapi import APIRouter, Depends

from webapp.app.models import Body, PaginatedResponse, PaginationParams
from webapp.app.services.token_service import TokenService, get_token_service

router = APIRouter()


@router.get("/ping")
async def ping() -> dict[str, str]:
    """Return a lightweight liveness response."""
    return {"status": "ok"}


@router.get("/health")
async def health() -> dict[str, str]:
    """Return the API health status."""
    return {"status": "ok"}


@router.post("/generate")
async def generate(
    body: Body, service: TokenService = Depends(get_token_service)
) -> dict[str, str]:
    """Generate a pseudo-random token ID.

    Args:
        body: Requested token length.
        service: Token service supplied by dependency injection.
    """
    token = service.generate(body.length)
    return {"token": token}


@router.get("/token", response_model=PaginatedResponse)
async def list_tokens(
    pagination: PaginationParams = Depends(),
    service: TokenService = Depends(get_token_service),
) -> PaginatedResponse:
    """Return generated tokens using validated pagination parameters."""
    items, total = service.list_paginated(pagination.page, pagination.page_size)
    total_pages = (total + pagination.page_size - 1) // pagination.page_size
    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )
