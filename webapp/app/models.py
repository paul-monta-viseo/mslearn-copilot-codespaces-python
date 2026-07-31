from __future__ import annotations

from typing import Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field


class Body(BaseModel):
    length: Union[int, None] = 20


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
