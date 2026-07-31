from uuid import UUID, uuid4

from fastapi import HTTPException

from webapp.app.models import User, UserCreate, UserUpdate


class UserService:
    def __init__(self) -> None:
        self._store: dict[UUID, User] = {}

    def create(self, data: UserCreate) -> User:
        user = User(id=uuid4(), name=data.name, email=data.email)
        self._store[user.id] = user
        return user

    def get(self, user_id: UUID) -> User:
        user = self._store.get(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def list_all(self) -> list[User]:
        return list(self._store.values())

    def update(self, user_id: UUID, data: UserUpdate) -> User:
        user = self.get(user_id)
        updated = user.model_copy(update=data.model_dump(exclude_none=True))
        self._store[user_id] = updated
        return updated

    def delete(self, user_id: UUID) -> None:
        self.get(user_id)  # raises 404 if missing
        del self._store[user_id]


# Module-level singleton so in-memory state persists across requests
user_service = UserService()


def get_user_service() -> UserService:
    return user_service
