"""User model and authentication."""

from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: str
    name: str
    email: str
    password_hash: str
    created_at: datetime

    @classmethod
    def create(cls, name: str, email: str, password_hash: str) -> "User":
        return cls(
            id=str(uuid4()),
            name=name,
            email=email,
            password_hash=password_hash,
            created_at=datetime.utcnow(),
        )
