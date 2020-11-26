import sqlalchemy as sa
from fastapi import Depends, HTTPException
from sqlalchemy import func

from .._api import api
from ..current_user import get_current_user
from ..db import DeliveryCompanies, engine
from ..pagination import pagination_view_builder
from ..schemas import (
    DeliveryCompaniesPostSchema,
    DeliveryCompaniesSchema,
    DeliveryCompanySchema,
    UserRoleEnum,
    UserSchema,
)


@api.post("/delivery_companies", response_model=DeliveryCompanySchema)
async def delivery_companies_post(
    delivery_company: DeliveryCompaniesPostSchema,
    current_user: UserSchema = Depends(get_current_user),
):
    if current_user.role not in (UserRoleEnum.ADMIN,):
        raise HTTPException(status_code=403, detail="Access forbidden")
    sel = sa.select([func.count(DeliveryCompanies.c.id)]).where(
        DeliveryCompanies.c.name == delivery_company.name
    )
    ins = (
        sa.insert(DeliveryCompanies)
        .values(name=delivery_company.name, price=delivery_company.price)
        .returning(DeliveryCompanies)
    )
    async with engine.begin() as conn:
        dc_cnt = (await conn.execute(sel)).fetchone()[0]
        if dc_cnt != 0:
            raise HTTPException(
                status_code=409,
                detail="Delivery company with given name already exist",
            )
        id_, name, price = (await conn.execute(ins)).fetchone()
    return DeliveryCompanySchema(id=id_, name=name, price=price)


@api.get("/delivery_companies", response_model=DeliveryCompaniesSchema)
async def delivery_companies_get(
    page: int = 0,
    per_page: int = 100,
    name: str = None,
    current_user: UserSchema = Depends(get_current_user),
):
    if current_user.role not in (UserRoleEnum.ADMIN, UserRoleEnum.CLIENT):
        raise HTTPException(status_code=403, detail="Access forbidden")
    sel = sa.select([DeliveryCompanies]).order_by(DeliveryCompanies.c.id)
    sel_cnt = sa.select([func.count(DeliveryCompanies.c.id)])
    if name is not None:
        # used concat to prevent sql injection
        sel = sel.where(
            DeliveryCompanies.c.name.like(func.concat(name, "%")),
        )
        sel_cnt = sel_cnt.where(
            DeliveryCompanies.c.name.like(func.concat(name, "%")),
        )
    return await pagination_view_builder(
        sel,
        sel_cnt,
        lambda id_, name_, price: DeliveryCompanySchema(
            id=id_, name=name_, price=price
        ),
        DeliveryCompaniesSchema,
        page,
        per_page,
    )
