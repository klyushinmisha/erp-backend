import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient

from env import DB_URL
from erp_backend import api
from erp_backend.db import (
    DeliveryCompanies,
    Documents,
    Goods,
    OrderGoods,
    Orders,
    Users,
    Warehouses,
)

client = TestClient(api)


engine = sa.create_engine(f"postgresql+psycopg2://{DB_URL}")


@pytest.fixture(scope="function", autouse=True)
def delete_tables():
    engine.execute(sa.delete(Documents))
    engine.execute(sa.delete(OrderGoods))
    engine.execute(sa.delete(Goods))
    engine.execute(sa.delete(Orders))
    engine.execute(sa.delete(DeliveryCompanies))
    engine.execute(sa.delete(Warehouses))
    engine.execute(sa.delete(Users))


@pytest.fixture(scope="function")
def token():
    response = client.post(
        "/users",
        json={
            "username": "testuser",
            "password": "testpassword",
            "role": "admin",
        },
    )
    return response.json()["token"]
