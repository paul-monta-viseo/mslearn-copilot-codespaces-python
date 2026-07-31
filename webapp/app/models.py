from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field


class Body(BaseModel):
    length: int = Field(
        default=20,
        ge=1,
        le=88,
        description="Token length in characters (between 1 and 88)",
    )

    model_config = {
        "json_schema_extra": {"examples": [{"length": 20}]}
    }


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="1-based page number")
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page (maximum 100)",
    )

    model_config = {
        "json_schema_extra": {"examples": [{"page": 1, "page_size": 20}]}
    }


class PaginatedResponse(BaseModel):
    items: list[str]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserCreate(BaseModel):
    name: str = Field(min_length=1, description="Display name")
    email: EmailStr

    model_config = {
        "json_schema_extra": {
            "examples": [{"name": "Alice", "email": "alice@example.com"}]
        }
    }


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, description="Display name")
    email: Optional[EmailStr] = None

    model_config = {
        "json_schema_extra": {
            "examples": [{"name": "Alice", "email": "alice@example.com"}]
        }
    }


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    email: EmailStr
