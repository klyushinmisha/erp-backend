__all__ = [
    "SALT",
    "N",
    "R",
    "P",
    "DKLEN",
    "SECRET",
    "ALGORITHM",
    "DB_URL",
]
from environs import Env

env = Env()


with env.prefixed("SCRYPT_"):
    SALT = env.str("SALT", "secret_salt").encode()
    N = env.int("N", 16384)
    R = env.int("R", 8)
    P = env.int("P", 1)
    DKLEN = env.int("DKLEN", 128)


with env.prefixed("JWT_"):
    SECRET = env.str("SECRET", "secret")
    ALGORITHM = env.str("ALGORITHM", "HS256")


with env.prefixed("DB_"):
    DB_URL = env.str("URL", "postgres:postgres@localhost/upi")
