__all__ = [
    "jwt_encode",
    "jwt_decode",
]
import jwt

from env import ALGORITHM, SECRET


def jwt_encode(payload):
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def jwt_decode(token):
    return jwt.decode(token, SECRET, algorithms=[ALGORITHM])
