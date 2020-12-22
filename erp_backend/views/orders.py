from datetime import datetime

import sqlalchemy as sa
from fastapi import Depends, HTTPException
from sqlalchemy import func

from .._api import api
from ..current_user import get_current_user
from ..db import DeliveryCompanies, Goods, OrderGoods, Orders, engine
from ..pagination import pagination_view_builder
from ..schemas import (
    OrderGoodSchema,
    OrderSchema,
    OrdersSchema,
    OrderStatusEnum,
    OrderUpdateStatePostSchema,
    OrderWithGoodsPostSchema,
    OrderWithGoodsSchema,
    UserRoleEnum,
    UserSchema,
)


@api.get("/orders/{order_id}", response_model=OrderWithGoodsSchema)
async def order_get(
    order_id: int,
    current_user: UserSchema = Depends(get_current_user),
):
    if current_user.role not in (
        UserRoleEnum.ADMIN,
        UserRoleEnum.WAREHOUSE,
        UserRoleEnum.DELIVERY,
        UserRoleEnum.CLIENT,
    ):
        raise HTTPException(status_code=403, detail="Access forbidden")
    order_query = sa.select([Orders]).where(Orders.c.id == order_id)
    goods_query = sa.select([Goods, OrderGoods.c.quantity]).select_from(
        Goods.join(OrderGoods, OrderGoods.c.order_id == order_id)
    )

    async with engine.begin() as conn:
        res = (await conn.execute(order_query)).fetchone()
        if res is None:
            raise HTTPException(status_code=404, detail="Order not found")

        (
            id_,
            status,
            created_at,
            delivery_expected_at,
            delivery_company_id,
        ) = res
        goods = [
            OrderGoodSchema(
                id=id_,
                name=name,
                code=code,
                quantity=quantity,
                warehouse_id=warehouse_id,
            )
            for id_, name, code, warehouse_id, quantity in (
                await conn.execute(goods_query)
            ).fetchall()
        ]
    return OrderWithGoodsSchema(
        id=id_,
        status=status,
        created_at=int(created_at.timestamp() * 1000),
        delivery_expected_at=int(delivery_expected_at.timestamp() * 1000),
        delivery_company_id=delivery_company_id,
        goods=goods,
    )


@api.post("/orders", response_model=OrderWithGoodsSchema)
async def order_post(
    order: OrderWithGoodsPostSchema,
    current_user: UserSchema = Depends(get_current_user),
):
    if current_user.role not in (
        UserRoleEnum.ADMIN,
        UserRoleEnum.CLIENT,
    ):
        raise HTTPException(status_code=403, detail="Access forbidden")

    check_company = sa.select([func.count(DeliveryCompanies.c.id)]).where(
        DeliveryCompanies.c.id == order.delivery_company_id
    )
    order_insert_query = (
        sa.insert(Orders)
        .values(
            status=OrderStatusEnum.CREATED.value,
            created_at=datetime.now(),
            delivery_expected_at=datetime.fromtimestamp(
                order.delivery_expected_at / 1000
            ),
            delivery_company_id=order.delivery_company_id,
            user_id=current_user.id,
        )
        .returning(Orders)
    )

    check_goods_query = sa.select([func.count(Goods.c.id)]).where(
        Goods.c.id.in_(tuple(g.id for g in order.goods))
    )

    async with engine.begin() as conn:
        if (await conn.execute(check_goods_query)).fetchone()[0] != len(
            order.goods
        ):
            raise HTTPException(
                status_code=404, detail="Got some non-existent goods"
            )

        if (await conn.execute(check_company)).fetchone()[0] == 0:
            raise HTTPException(
                status_code=409, detail="Given delivery company doesn't exist"
            )
        (
            order_id,
            status,
            created_at,
            delivery_expected_at,
            delivery_company_id,
            user_id,
        ) = (await conn.execute(order_insert_query)).fetchone()

        order_goods_insert_query = sa.insert(OrderGoods).values(
            [(order_id, g.id, g.quantity) for g in order.goods]
        )
        goods_query = (
            sa.select([Goods, OrderGoods.c.quantity])
            .select_from(Goods.join(OrderGoods))
            .where(OrderGoods.c.order_id == order_id)
            .order_by(Goods.c.id)
        )

        await conn.execute(order_goods_insert_query)

        goods = [
            OrderGoodSchema(
                id=id_,
                name=name,
                code=code,
                quantity=quantity,
                warehouse_id=warehouse_id,
            )
            for id_, name, code, warehouse_id, quantity in (
                await conn.execute(goods_query)
            ).fetchall()
        ]
    return OrderWithGoodsSchema(
        id=order_id,
        status=status,
        created_at=int(created_at.timestamp() * 1000),
        delivery_expected_at=int(delivery_expected_at.timestamp() * 1000),
        delivery_company_id=delivery_company_id,
        user_id=user_id,
        goods=goods,
    )


@api.post(
    "/orders/{order_id}/update_status", response_model=OrderWithGoodsSchema
)
async def orders_update_status_post(
    order_id: int,
    update_data: OrderUpdateStatePostSchema,
    current_user: UserSchema = Depends(get_current_user),
):
    if current_user.role not in (
        UserRoleEnum.ADMIN,
        UserRoleEnum.LAWYER,
        UserRoleEnum.WAREHOUSE,
        UserRoleEnum.DELIVERY,
    ):
        raise HTTPException(status_code=403, detail="Access forbidden")
    update_q = (
        sa.update(Orders)
        .where(Orders.c.id == order_id)
        .values(status=update_data.status)
        .returning(Orders)
    )
    async with engine.begin() as conn:
        res = (await conn.execute(update_q)).fetchone()
        if res is None:
            raise HTTPException(status_code=404, detail="Order doesn't exist")
        (
            id_,
            status,
            created_at,
            delivery_expected_at,
            delivery_company_id,
            user_id,
        ) = res

        goods_query = (
            sa.select([Goods, OrderGoods.c.quantity])
            .select_from(Goods.join(OrderGoods))
            .where(OrderGoods.c.order_id == order_id)
            .order_by(Goods.c.id)
        )

        goods = [
            OrderGoodSchema(
                id=id_,
                name=name,
                code=code,
                quantity=quantity,
                warehouse_id=warehouse_id,
            )
            for id_, name, code, warehouse_id, quantity in (
                await conn.execute(goods_query)
            ).fetchall()
        ]

    return OrderWithGoodsSchema(
        id=id_,
        status=status,
        created_at=int(created_at.timestamp() * 1000),
        delivery_expected_at=int(delivery_expected_at.timestamp() * 1000),
        delivery_company_id=delivery_company_id,
        user_id=user_id,
        goods=goods,
    )


def _order_args_builder(
    id_, status, created_at, delivery_expected_at, delivery_company_id, user_id
):
    return OrderSchema(
        id=id_,
        status=status,
        created_at=int(created_at.timestamp() * 1000),
        delivery_expected_at=int(delivery_expected_at.timestamp() * 1000),
        delivery_company_id=delivery_company_id,
        user_id=user_id,
    )


@api.get("/orders", response_model=OrdersSchema)
async def orders_get(
    page: int = 0,
    per_page: int = 100,
    user_id: int = None,
    status: str = None,
    current_user: UserSchema = Depends(get_current_user),
):
    if current_user.role not in (
        UserRoleEnum.ADMIN,
        UserRoleEnum.WAREHOUSE,
        UserRoleEnum.DELIVERY,
        UserRoleEnum.CLIENT,
        UserRoleEnum.LAWYER,
    ):
        raise HTTPException(status_code=403, detail="Access forbidden")
    sel = sa.select([Orders]).order_by(Orders.c.id)
    sel_cnt = sa.select([func.count(Orders.c.id)])
    if user_id is not None:
        sel = sel.where(Orders.c.user_id == user_id)
        sel_cnt = sel_cnt.where(Orders.c.user_id == user_id)
    if status is not None:
        sel = sel.where(Orders.c.status == status)
        sel_cnt = sel_cnt.where(Orders.c.status == status)
    return await pagination_view_builder(
        sel,
        sel_cnt,
        _order_args_builder,
        OrdersSchema,
        page,
        per_page,
    )
