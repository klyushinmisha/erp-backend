__all__ = [
    "engine",
    "Users",
    "Warehouses",
    "DeliveryCompanies",
    "Orders",
    "Goods",
    "OrderGoods",
    "Documents",
]
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine

from env import DB_URL

engine = sa.create_engine(f"postgresql+psycopg2://{DB_URL}")
metadata = sa.MetaData()
metadata.reflect(bind=engine)
engine.dispose()


Users = metadata.tables["users"]
Warehouses = metadata.tables["warehouses"]
DeliveryCompanies = metadata.tables["delivery_companies"]
Orders = metadata.tables["orders"]
Goods = metadata.tables["goods"]
OrderGoods = metadata.tables["order_goods"]
Documents = metadata.tables["documents"]


engine = create_async_engine(f"postgresql+asyncpg://{DB_URL}")
