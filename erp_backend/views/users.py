import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy import func

from .._api import api
from ..db import Users, engine
from ..hasher import password_hasher
from ..jwt import jwt_encode
from ..schemas import AuthSchema, UserRoleEnum, UsersPostSchema


@api.post("/users", response_model=AuthSchema)
async def users_post(user: UsersPostSchema):
    try:
        UserRoleEnum(user.role)
    except ValueError:
        raise HTTPException(
            status_code=422, detail=f"Got invalid user role: {user.role}"
        )
    sel = sa.select([func.count(Users.c.id)]).where(
        Users.c.username == user.username
    )
    ins = (
        sa.insert(Users)
        .values(
            username=user.username,
            password_hash=password_hasher(user.password.encode()),
            role=user.role,
        )
        .returning(Users.c.id)
    )
    async with engine.begin() as conn:
        res = await conn.execute(sel)
        if res.fetchone()[0] != 0:
            raise HTTPException(
                status_code=409,
                detail=f"User with username '{user.username}' already exist",
            )
        id_ = (await conn.execute(ins)).fetchone()[0]
        token = jwt_encode(
            {"id": id_, "username": user.username, "role": user.role}
        )
        return AuthSchema(token=token)
