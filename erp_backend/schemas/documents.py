__all__ = [
    "DocumentMimeEnum",
    "DocumentSchema",
    "DocumentsSchema",
]
import enum
from typing import List

from pydantic import BaseModel

from .pagination import PaginationSchema


class DocumentMimeEnum(enum.Enum):
    doc = "application/msword"
    docx = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml."
        "document"
    )
    pdf = "application/pdf"


class DocumentSchema(BaseModel):
    id: int
    name: str
    order_id: int


class DocumentsSchema(BaseModel):
    data: List[DocumentSchema]
    pagination: PaginationSchema
