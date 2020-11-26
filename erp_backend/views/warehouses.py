import sqlalchemy as sa
from fastapi import Depends, HTTPException
from sqlalchemy import func

from .._api import api
from ..current_user import get_current_user
from ..db import Warehouses, engine
from ..pagination import pagination_view_builder
from ..schemas import (
    UserRoleEnum,
    UserSchema,
    WarehouseSchema,
    WarehousesPostSchema,
    WarehousesSchema,
)


@api.post("/warehouses", response_model=WarehouseSchema)
async def warehouses_post(
    warehouse: WarehousesPostSchema,
    current_user: UserSchema = Depends(get_current_user),
):
    if current_user.role not in (UserRoleEnum.ADMIN,):
        raise HTTPException(status_code=403, detail="Access forbidden")
    sel_query = sa.select([func.count(Warehouses.c.id)]).where(
        Warehouses.c.address == warehouse.address
    )
    ins_query = (
        sa.insert(Warehouses)
        .values(address=warehouse.address)
        .returning(Warehouses)
    )
    async with engine.begin() as conn:
        wh_cnt = (await conn.execute(sel_query)).fetchone()[0]
        if wh_cnt != 0:
            raise HTTPException(
                status_code=409, detail="Warehouse already exist"
            )
        id_, address = (await conn.execute(ins_query)).fetchone()
    return WarehouseSchema(id=id_, address=address)


@api.get("/warehouses", response_model=WarehousesSchema)
async def warehouses_get(
    page: int = 0,
    per_page: int = 100,
    address: str = None,
    current_user: UserSchema = Depends(get_current_user),
):
    if current_user.role not in (
        UserRoleEnum.ADMIN,
        UserRoleEnum.WAREHOUSE,
        UserRoleEnum.DELIVERY,
    ):
        raise HTTPException(status_code=403, detail="Access forbidden")
    sel = sa.select([Warehouses]).order_by(Warehouses.c.id)
    sel_cnt = sa.select([func.count(Warehouses.c.id)])
    if address is not None:
        # used concat to prevent sql injection
        sel = sel.where(
            Warehouses.c.address.like(func.concat(address, "%")),
        )
        sel_cnt = sel_cnt.where(
            Warehouses.c.address.like(func.concat(address, "%")),
        )
    return await pagination_view_builder(
        sel,
        sel_cnt,
        lambda id_, addr: WarehouseSchema(id=id_, address=addr),
        WarehousesSchema,
        page,
        per_page,
    )
