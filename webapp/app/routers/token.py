from fastapi import APIRouter, Depends

from webapp.app.models import Body, PaginatedResponse, PaginationParams
from webapp.app.services.token_service import TokenService, get_token_service

router = APIRouter()


@router.get("/ping")
def ping():
    return {"status": "ok"}


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/generate")
def generate(body: Body, service: TokenService = Depends(get_token_service)):
    """
    Generate a pseudo-random token ID. Default length is 20 characters.

    Example request body:
        {"length": 20}
    """
    token = service.generate(body.length)
    return {"token": token}


@router.get("/token", response_model=PaginatedResponse)
def list_tokens(
    pagination: PaginationParams = Depends(),
    service: TokenService = Depends(get_token_service),
):
    items, total = service.list_paginated(pagination.page, pagination.page_size)
    total_pages = (total + pagination.page_size - 1) // pagination.page_size
    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )
