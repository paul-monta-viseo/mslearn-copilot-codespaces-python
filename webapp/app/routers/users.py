from uuid import UUID

from fastapi import APIRouter, Depends

from webapp.app.models import User, UserCreate, UserUpdate
from webapp.app.services.user_service import UserService, get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[User])
def list_users(service: UserService = Depends(get_user_service)):
    return service.list_all()


@router.post("", response_model=User, status_code=201)
def create_user(data: UserCreate, service: UserService = Depends(get_user_service)):
    return service.create(data)


@router.get("/{user_id}", response_model=User)
def get_user(user_id: UUID, service: UserService = Depends(get_user_service)):
    return service.get(user_id)


@router.put("/{user_id}", response_model=User)
def update_user(user_id: UUID, data: UserUpdate, service: UserService = Depends(get_user_service)):
    return service.update(user_id, data)


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: UUID, service: UserService = Depends(get_user_service)):
    service.delete(user_id)
