from fastapi import APIRouter, Depends

from webapp.app.models import Body
from webapp.app.services.token_service import TokenService

router = APIRouter()


@router.get("/ping")
def ping():
    return {"status": "ok"}


@router.post("/generate")
def generate(body: Body, service: TokenService = Depends(TokenService)):
    """
    Generate a pseudo-random token ID. Default length is 20 characters.

    Example request body:
        {"length": 20}
    """
    token = service.generate(body.length)
    return {"token": token}
