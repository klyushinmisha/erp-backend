import sqlalchemy as sa
from fastapi import HTTPException, Response

from .._api import api
from ..db import Users, engine
from ..hasher import password_hasher
from ..jwt import jwt_encode
from ..schemas import AuthPostSchema, AuthSchema


@api.post("/auth", response_model=AuthSchema)
async def auth_post(
    response: Response,
    user: AuthPostSchema,
):
    password_hash = password_hasher(user.password.encode())

    sel = sa.select([Users.c.id, Users.c.role]).where(
        Users.c.username == user.username,
        Users.c.password_hash == password_hash,
    )
    async with engine.begin() as conn:
        res = (await conn.execute(sel)).fetchone()
        if res is None:
            raise HTTPException(
                status_code=401,
                detail=f"Invaild credentials were provided",
            )
        id_, role = res
        token = jwt_encode(
            {"id": id_, "username": user.username, "role": role}
        )
    response.set_cookie("token", token, httponly=True)
    return AuthSchema(token=token)
