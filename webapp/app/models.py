from __future__ import annotations

from typing import Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field


class Body(BaseModel):
    length: Union[int, None] = 20


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="1-based page number")
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page (maximum 100)",
    )


class PaginatedResponse(BaseModel):
    items: list[str]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserCreate(BaseModel):
    name: str
    email: EmailStr


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    email: EmailStr
