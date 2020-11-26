__all__ = [
    "DeliveryCompanySchema",
    "DeliveryCompaniesPostSchema",
    "DeliveryCompaniesSchema",
]
from typing import List

from pydantic import BaseModel, validator

from .pagination import PaginationSchema


class DeliveryCompanySchema(BaseModel):
    id: int
    name: str
    price: float


class DeliveryCompaniesPostSchema(BaseModel):
    name: str
    price: float

    @validator("name")
    def validate_name(cls, v):
        if len(v) > 256:
            raise ValueError("Invalid length")
        return v

    @validator("price")
    def validate_price(cls, v):
        PRICE_PRECISION = 10
        PRICE_SCALE = 2
        if v < 0.0:
            raise ValueError("Price value must be non-negative")
        if v > 10 ** (PRICE_PRECISION - PRICE_SCALE):
            raise ValueError("Price value exceeds supported limits")
        return v


class DeliveryCompaniesSchema(BaseModel):
    data: List[DeliveryCompanySchema]
    pagination: PaginationSchema
