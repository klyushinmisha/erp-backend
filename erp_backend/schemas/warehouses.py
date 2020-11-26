__all__ = [
    "WarehousesPostSchema",
    "WarehouseSchema",
    "WarehousesSchema",
]
from typing import List

from pydantic import BaseModel, validator

from .pagination import PaginationSchema


class WarehousesPostSchema(BaseModel):
    address: str

    @validator("address")
    def validate_address(cls, v):
        if len(v) > 256:
            raise ValueError("Invalid length")
        return v


class WarehouseSchema(BaseModel):
    id: int
    address: str


class WarehousesSchema(BaseModel):
    data: List[WarehouseSchema]
    pagination: PaginationSchema
