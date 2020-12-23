__all__ = [
    "OrderStatusEnum",
    "OrderSchema",
    "OrderGoodSchema",
    "OrderWithGoodsSchema",
    "OrderGoodPostSchema",
    "OrderWithGoodsPostSchema",
    "OrderUpdateStatePostSchema",
    "OrdersSchema",
]
import enum
from datetime import datetime
from typing import List

import arrow
from pydantic import BaseModel, validator

from .pagination import PaginationSchema


class OrderStatusEnum(str, enum.Enum):
    CREATED = "created"
    FORMALIZING = "formalizing"
    COLLECTING = "collecting"
    DELIVERING = "delivering"
    DONE = "done"


class OrderSchema(BaseModel):
    id: int
    status: OrderStatusEnum
    created_at: int
    delivery_expected_at: int
    delivery_company_id: int
    user_id: int


class OrderGoodSchema(BaseModel):
    id: int
    name: str
    code: str
    quantity: int
    warehouse_id: int


class OrderWithGoodsSchema(BaseModel):
    id: int
    status: OrderStatusEnum
    created_at: int
    delivery_expected_at: int
    delivery_company_id: int
    user_id: int
    goods: List[OrderGoodSchema]


class OrderGoodPostSchema(BaseModel):
    id: int
    quantity: int

    @validator("quantity")
    def validate_quantity(cls, v):
        if v < 1:
            raise ValueError("Got negative quantity")
        return v


class OrderWithGoodsPostSchema(BaseModel):
    delivery_expected_at: int
    delivery_company_id: int
    goods: List[OrderGoodPostSchema]

    @classmethod
    def _validate_time_string(cls, ts):
        try:
            datetime.fromtimestamp(ts / 1000)
        except arrow.parser.ParserError:
            raise ValueError("Invalid unix timestamp")

    @validator("delivery_expected_at")
    def validate_delivery_expected_at(cls, v):
        try:
            datetime.fromtimestamp(v / 1000)
        except arrow.parser.ParserError:
            raise ValueError("Invalid unix timestamp")
        return v


class OrderUpdateStatePostSchema(BaseModel):
    status: OrderStatusEnum


class OrdersSchema(BaseModel):
    data: List[OrderSchema]
    pagination: PaginationSchema
