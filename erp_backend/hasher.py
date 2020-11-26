__all__ = [
    "password_hasher",
]
from hashlib import scrypt

from env import DKLEN, SALT, N, P, R


def password_hasher(password_bytes):
    return scrypt(
        password_bytes,
        salt=SALT,
        n=N,
        r=R,
        p=P,
        dklen=DKLEN,
    )
