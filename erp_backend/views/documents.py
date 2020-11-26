import io
from urllib.parse import quote

import magic
import sqlalchemy as sa
from fastapi import Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import func

from .._api import api
from ..current_user import get_current_user, get_current_user_from_cookie
from ..db import Documents, Orders, engine
from ..pagination import pagination_view_builder
from ..schemas import (
    DocumentMimeEnum,
    DocumentSchema,
    DocumentsSchema,
    UserRoleEnum,
    UserSchema,
)


@api.post("/documents", response_model=DocumentSchema)
async def document_post(
    order_id: int = Form(...),
    name: str = Form(...),
    data: UploadFile = File(...),
    current_user: UserSchema = Depends(get_current_user),
):
    if current_user.role not in (
        UserRoleEnum.ADMIN,
        UserRoleEnum.LAWYER,
        UserRoleEnum.CLIENT,
    ):
        raise HTTPException(status_code=403, detail="Access forbidden")
    if len(name) > 256:
        raise HTTPException(
            status_code=422, detail="Invalid 'name' field length"
        )
    check_order = sa.select([func.count(Orders.c.id)]).where(
        Orders.c.id == order_id
    )
    try:
        DocumentMimeEnum(data.content_type)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Got invalid file mime: {data.content_type}",
        )
    async with engine.begin() as conn:
        if (await conn.execute(check_order)).fetchone()[0] == 0:
            raise HTTPException(
                status_code=409, detail="Given order doesn't exist"
            )
        contents = await data.read()
        ins = (
            sa.insert(Documents)
            .values(data=contents, name=name, order_id=order_id)
            .returning(Documents.c.id)
        )
        id_ = (await conn.execute(ins)).fetchone()[0]
    return DocumentSchema(id=id_, name=name, order_id=order_id)


@api.get("/documents", response_model=DocumentsSchema)
async def documents_get(
    page: int = 0,
    per_page: int = 100,
    name: str = None,
    current_user: UserSchema = Depends(get_current_user),
):
    if current_user.role not in (
        UserRoleEnum.ADMIN,
        UserRoleEnum.LAWYER,
        UserRoleEnum.CLIENT,
    ):
        raise HTTPException(status_code=403, detail="Access forbidden")
    sel = sa.select(
        [Documents.c.id, Documents.c.name, Documents.c.order_id]
    ).order_by(Documents.c.id)
    sel_cnt = sa.select([func.count(Documents.c.id)])
    if name is not None:
        # used concat to prevent sql injection
        sel = sel.where(
            Documents.c.name.like(func.concat(name, "%")),
        )
        sel_cnt = sel_cnt.where(
            Documents.c.name.like(func.concat(name, "%")),
        )
    return await pagination_view_builder(
        sel,
        sel_cnt,
        lambda id_, name_, order_id: DocumentSchema(
            id=id_, name=name_, order_id=order_id
        ),
        DocumentsSchema,
        page,
        per_page,
    )


@api.get("/documents/{doc_id}/data")
async def documents_get(
    doc_id: int,
    current_user: UserSchema = Depends(get_current_user_from_cookie),
):
    if current_user.role not in (
        UserRoleEnum.ADMIN,
        UserRoleEnum.LAWYER,
        UserRoleEnum.CLIENT,
    ):
        raise HTTPException(status_code=403, detail="Access forbidden")
    sel = sa.select([Documents.c.name, Documents.c.data]).where(
        Documents.c.id == doc_id
    )
    async with engine.begin() as conn:
        res = (await conn.execute(sel)).fetchone()
        if res is None:
            raise HTTPException(status_code=404, detail="Document not found")
        doc_name, data = res

    doc_mime = DocumentMimeEnum(magic.from_buffer(data, mime=True))
    doc_name = f"{doc_name.replace(' ', '_')}.{doc_mime.name}"

    try:
        doc_name.encode("ascii")
        file_expr = 'filename="{}"'.format(doc_name)
    except UnicodeEncodeError:
        # handle a non-ASCII filename
        file_expr = "filename*=utf-8''{}".format(quote(doc_name))

    headers = {"Content-Disposition": "attachment; {}".format(file_expr)}

    return StreamingResponse(
        io.BytesIO(data), headers=headers, media_type=doc_mime.value
    )
