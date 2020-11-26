__all__ = [
    "GoodSchema",
    "GoodsPostSchema",
    "GoodsSchema",
]
from typing import List

from pydantic import BaseModel, validator

from .pagination import PaginationSchema


class GoodSchema(BaseModel):
    id: int
    name: str
    code: str
    warehouse_id: int


class GoodsPostSchema(BaseModel):
    name: str
    code: str
    warehouse_id: int

    @validator("name")
    def validate_name(cls, v):
        if len(v) > 128:
            raise ValueError("Invalid length")
        return v

    @validator("code")
    def validate_code(cls, v):
        if len(v) > 32:
            raise ValueError("Invalid length")
        return v


class GoodsSchema(BaseModel):
    data: List[GoodSchema]
    pagination: PaginationSchema
