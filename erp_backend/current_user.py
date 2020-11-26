__all__ = [
    "get_current_user",
    "get_current_user_from_cookie",
]

from typing import Optional

import jwt
import sqlalchemy as sa
from fastapi import Cookie, Header, HTTPException

from .db import Users, engine
from .jwt import jwt_decode
from .schemas import UserRoleEnum, UserSchema


async def _get_current_user_from_token(token):
    try:
        payload = jwt_decode(token)
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token provided")

    sel_query = sa.select([Users.c.id, Users.c.username, Users.c.role]).where(
        Users.c.username == payload["username"]
    )
    async with engine.begin() as conn:
        row = (await conn.execute(sel_query)).fetchone()
        if row is None:
            raise HTTPException(status_code=401, detail=f"Identity not found")

    id_, username, role = row
    return UserSchema(id=id_, username=username, role=UserRoleEnum(role))


async def get_current_user(authorization: Optional[str] = Header(None)):
    if authorization is None:
        raise HTTPException(
            status_code=401, detail=f"Authorization header is missing"
        )
    return await _get_current_user_from_token(authorization)


async def get_current_user_from_cookie(token: Optional[str] = Cookie(None)):
    if token is None:
        raise HTTPException(status_code=401, detail=f"Token cookie is missing")
    return await _get_current_user_from_token(token)
