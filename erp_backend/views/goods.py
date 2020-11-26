import sqlalchemy as sa
from fastapi import Depends, HTTPException
from sqlalchemy import func, or_

from .._api import api
from ..current_user import get_current_user
from ..db import Goods, Warehouses, engine
from ..pagination import pagination_view_builder
from ..schemas import (
    GoodSchema,
    GoodsPostSchema,
    GoodsSchema,
    UserRoleEnum,
    UserSchema,
)


@api.post("/goods", response_model=GoodSchema)
async def good_post(
    good: GoodsPostSchema,
    current_user: UserSchema = Depends(get_current_user),
):
    if current_user.role not in (UserRoleEnum.ADMIN, UserRoleEnum.WAREHOUSE):
        raise HTTPException(status_code=403, detail="Access forbidden")
    check_wh = sa.select([func.count(Warehouses.c.id)]).where(
        Warehouses.c.id == good.warehouse_id
    )
    validate_good = sa.select([func.count(Goods.c.id)]).where(
        or_(
            Goods.c.name == good.name,
            Goods.c.code == good.code,
        )
    )
    ins = (
        sa.insert(Goods)
        .values(
            name=good.name,
            code=good.code,
            warehouse_id=good.warehouse_id,
        )
        .returning(Goods)
    )
    async with engine.begin() as conn:
        if (await conn.execute(check_wh)).fetchone()[0] == 0:
            raise HTTPException(
                status_code=409, detail="Given warehouse doesn't exist"
            )
        if (await conn.execute(validate_good)).fetchone()[0] != 0:
            raise HTTPException(
                status_code=409, detail="Good's properties already taken"
            )
        id_, name, code, warehouse_id = (await conn.execute(ins)).fetchone()
    return GoodSchema(
        id=id_,
        name=name,
        code=code,
        warehouse_id=warehouse_id,
    )


@api.get("/goods", response_model=GoodsSchema)
async def goods_get(
    page: int = 0,
    per_page: int = 100,
    name: str = None,
    code: str = None,
    current_user: UserSchema = Depends(get_current_user),
):
    if current_user.role not in (
        UserRoleEnum.ADMIN,
        UserRoleEnum.CLIENT,
        UserRoleEnum.WAREHOUSE,
    ):
        raise HTTPException(status_code=403, detail="Access forbidden")
    sel = sa.select([Goods]).order_by(Goods.c.id)
    sel_cnt = sa.select([func.count(Goods.c.id)])
    if name is not None:
        # used concat to prevent sql injection
        sel = sel.where(
            Goods.c.name.like(func.concat(name, "%")),
        )
        sel_cnt = sel_cnt.where(
            Goods.c.name.like(func.concat(name, "%")),
        )
    if code is not None:
        # used concat to prevent sql injection
        sel = sel.where(
            Goods.c.code.like(func.concat(code, "%")),
        )
        sel_cnt = sel_cnt.where(
            Goods.c.code.like(func.concat(code, "%")),
        )
    return await pagination_view_builder(
        sel,
        sel_cnt,
        lambda id_, name_, code_, warehouse_id: GoodSchema(
            id=id_,
            name=name_,
            code=code_,
            warehouse_id=warehouse_id,
        ),
        GoodsSchema,
        page,
        per_page,
    )
