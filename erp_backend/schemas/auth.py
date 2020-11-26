__all__ = [
    "AuthSchema",
    "AuthPostSchema",
]
from pydantic import BaseModel, validator


class AuthSchema(BaseModel):
    token: str


class AuthPostSchema(BaseModel):
    username: str
    password: str

    @validator("username")
    def validate_username(cls, v):
        if 8 <= len(v) <= 32:
            return v
        raise ValueError("Invalid length")

    @validator("password")
    def validate_password(cls, v):
        if 8 <= len(v) <= 32:
            return v
        raise ValueError("Invalid length")
