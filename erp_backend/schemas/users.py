__all__ = [
    "UsersPostSchema",
    "UserRoleEnum",
    "UserSchema",
]
import enum

from pydantic import BaseModel, validator


class UsersPostSchema(BaseModel):
    username: str
    password: str
    role: str

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

    @validator("password")
    def validate_role(cls, v):
        if 0 <= len(v) <= 32:
            return v
        raise ValueError("Invalid length")


class UserRoleEnum(str, enum.Enum):
    ADMIN = "admin"
    WAREHOUSE = "warehouse"
    DELIVERY = "delivery"
    LAWYER = "lawyer"
    CLIENT = "client"


class UserSchema(BaseModel):
    id: int
    username: str
    role: UserRoleEnum
