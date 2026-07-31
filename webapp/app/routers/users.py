from uuid import UUID

from fastapi import APIRouter, Depends

from webapp.app.models import User, UserCreate, UserUpdate
from webapp.app.services.user_service import UserService, get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[User])
def list_users(service: UserService = Depends(get_user_service)) -> list[User]:
    """List all users currently held by the user service."""
    return service.list_all()


@router.post("", response_model=User, status_code=201)
def create_user(data: UserCreate, service: UserService = Depends(get_user_service)) -> User:
    """Create a user after validating the request body."""
    return service.create(data)


@router.get("/{user_id}", response_model=User)
def get_user(user_id: UUID, service: UserService = Depends(get_user_service)) -> User:
    """Return a user or a 404 response when it does not exist."""
    return service.get(user_id)


@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: UUID, data: UserUpdate, service: UserService = Depends(get_user_service)
) -> User:
    """Update the supplied fields of an existing user."""
    return service.update(user_id, data)


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: UUID, service: UserService = Depends(get_user_service)) -> None:
    """Delete a user, returning 404 when the user does not exist."""
    service.delete(user_id)
