"""initial_migration

Revision ID: 630af467ee03
Revises: 
Create Date: 2020-11-29 01:29:51.568397

"""
from alembic import op

revision = "630af467ee03"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(
        """
CREATE TABLE "users" (
    id                      SERIAL PRIMARY KEY,
    username                VARCHAR(32) UNIQUE NOT NULL,
    password_hash           BYTEA NOT NULL,
    role                    VARCHAR(32) NOT NULL
);


CREATE INDEX ON "users"(username, password_hash);


CREATE TABLE "warehouses" (
    id                      SERIAL PRIMARY KEY,
    address                 VARCHAR(256) UNIQUE NOT NULL
);


CREATE TABLE "delivery_companies" (
    id                      SERIAL PRIMARY KEY,
    name                    VARCHAR(256) UNIQUE NOT NULL,
    price                   NUMERIC(10, 2) NOT NULL CHECK (price > 0)
);


CREATE TABLE "orders" (
    id                      SERIAL PRIMARY KEY,
    status                  VARCHAR(32),
    created_at              TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    delivery_expected_at    TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    delivery_company_id     INTEGER REFERENCES "delivery_companies",
    user_id                 INTEGER REFERENCES "users"
);


CREATE TABLE "goods" (
    id                      SERIAL PRIMARY KEY,
    name                    VARCHAR(128) UNIQUE NOT NULL,
    code                    VARCHAR(32) UNIQUE NOT NULL,
    warehouse_id            INTEGER REFERENCES "warehouses"
);


CREATE TABLE "order_goods" (
    order_id                INTEGER REFERENCES "orders",
    good_id                 INTEGER REFERENCES "goods",
    quantity                INTEGER NOT NULL CHECK (quantity > 0)
);


CREATE INDEX ON "order_goods"(order_id, good_id);


CREATE TABLE "documents" (
    id                      SERIAL PRIMARY KEY,
    name                    VARCHAR(256) NOT NULL,
    data                    BYTEA NOT NULL,
    order_id                INTEGER REFERENCES "orders"
);


CREATE INDEX ON "documents"(name);
"""
    )


def downgrade():
    pass
