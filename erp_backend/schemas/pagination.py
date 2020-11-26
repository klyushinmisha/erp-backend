__all__ = [
    "PaginationSchema",
]
from pydantic import BaseModel


class PaginationSchema(BaseModel):
    page: int
    per_page: int
    total_pages: int
