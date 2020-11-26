__all__ = [
    "pagination_view_builder",
]

from fastapi import HTTPException

from .db import engine
from .schemas import PaginationSchema


async def pagination_view_builder(
    query, count_query, item_builder, collection_schema, page, per_page
):
    if page < 0 or per_page < 1:
        raise HTTPException(
            status_code=400, detail="Invalid pagination query parameters"
        )
    query = query.offset(page * per_page).limit(per_page)
    async with engine.begin() as conn:
        data = [
            item_builder(*build_args)
            for build_args in (await conn.execute(query)).fetchall()
        ]
        total_items = (await conn.execute(count_query)).fetchone()[0]
        total_pages = total_items // per_page
        if total_items % per_page != 0:
            total_pages += 1
        return collection_schema(
            data=data,
            pagination=PaginationSchema(
                page=page, per_page=per_page, total_pages=total_pages
            ),
        )
