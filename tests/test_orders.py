from datetime import datetime

import magic
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
from erp_backend.jwt import jwt_decode
from tests import client


def test_order_post(token):
    dc_resp = client.post(
        "/delivery_companies",
        json={"name": "somemagicaname", "price": 2.0},
        headers={"Authorization": token},
    )
    assert dc_resp.status_code == 200
    comp_id = dc_resp.json()["id"]

    wh_resp = client.post(
        "/warehouses",
        json={"address": "somemagicaddress"},
        headers={"Authorization": token},
    )
    assert wh_resp.status_code == 200
    wh_id = wh_resp.json()["id"]

    names_and_codes = ["a", "b", "c"]
    goods_ids = []
    for nc in names_and_codes:
        good_data = {
            "name": nc,
            "code": nc,
            "warehouse_id": wh_id,
        }
        response_ = client.post(
            "/goods",
            json=good_data,
            headers={"Authorization": token},
        )
        assert response_.status_code == 200
        goods_ids.append(response_.json()["id"])

    order_data = {
        "delivery_expected_at": int(datetime.now().timestamp() * 1000),
        "delivery_company_id": comp_id,
        "goods": [{"id": g_id, "quantity": 1} for g_id in goods_ids],
    }

    response = client.post(
        "/orders",
        json=order_data,
        headers={"Authorization": token},
    )
    order_data["status"] = "created"
    json = response.json()
    assert response.status_code == 200
    assert json.pop("id", None) is not None
    assert json.pop("created_at", None) is not None
    assert json.pop("goods", None) is not None
    order_data.pop("goods")
    assert json == order_data


def test_order_get(token):
    dc_resp = client.post(
        "/delivery_companies",
        json={"name": "somemagicaname", "price": 2.0},
        headers={"Authorization": token},
    )
    assert dc_resp.status_code == 200
    comp_id = dc_resp.json()["id"]

    wh_resp = client.post(
        "/warehouses",
        json={"address": "somemagicaddress"},
        headers={"Authorization": token},
    )
    assert wh_resp.status_code == 200
    wh_id = wh_resp.json()["id"]

    names_and_codes = ["a", "b", "c"]
    goods_ids = []
    for nc in names_and_codes:
        good_data = {
            "name": nc,
            "code": nc,
            "warehouse_id": wh_id,
        }
        response_ = client.post(
            "/goods",
            json=good_data,
            headers={"Authorization": token},
        )
        assert response_.status_code == 200
        goods_ids.append(response_.json()["id"])

    order_data = {
        "delivery_expected_at": int(datetime.now().timestamp() * 1000),
        "delivery_company_id": comp_id,
        "goods": [{"id": g_id, "quantity": 1} for g_id in goods_ids],
    }

    response = client.post(
        "/orders",
        json=order_data,
        headers={"Authorization": token},
    )
    order_data["status"] = "created"
    json = response.json()
    assert response.status_code == 200
    assert json.pop("id", None) is not None
    assert json.pop("created_at", None) is not None
    assert json.pop("goods", None) is not None
    order_data.pop("goods")
    assert json == order_data


def test_order_update_status(token):
    dc_resp = client.post(
        "/delivery_companies",
        json={"name": "somemagicaname", "price": 2.0},
        headers={"Authorization": token},
    )
    assert dc_resp.status_code == 200
    comp_id = dc_resp.json()["id"]

    wh_resp = client.post(
        "/warehouses",
        json={"address": "somemagicaddress"},
        headers={"Authorization": token},
    )
    assert wh_resp.status_code == 200
    wh_id = wh_resp.json()["id"]

    names_and_codes = ["a", "b", "c"]
    goods_ids = []
    for nc in names_and_codes:
        good_data = {
            "name": nc,
            "code": nc,
            "warehouse_id": wh_id,
        }
        response_ = client.post(
            "/goods",
            json=good_data,
            headers={"Authorization": token},
        )
        assert response_.status_code == 200
        goods_ids.append(response_.json()["id"])

    order_data = {
        "delivery_expected_at": int(datetime.now().timestamp() * 1000),
        "delivery_company_id": comp_id,
        "goods": [{"id": g_id, "quantity": 1} for g_id in goods_ids],
    }

    response = client.post(
        "/orders",
        json=order_data,
        headers={"Authorization": token},
    )
    order_data = response.json()
    order_data["status"] = "formalizing"

    response = client.post(
        f"/orders/{order_data['id']}/update_status",
        json={"status": "formalizing"},
        headers={"Authorization": token},
    )
    assert response.status_code == 200
    json = response.json()
    assert json == order_data


def test_orders_get(token):
    dc_resp = client.post(
        "/delivery_companies",
        json={"name": "somemagicaname", "price": 2.0},
        headers={"Authorization": token},
    )
    assert dc_resp.status_code == 200
    comp_id = dc_resp.json()["id"]

    wh_resp = client.post(
        "/warehouses",
        json={"address": "somemagicaddress"},
        headers={"Authorization": token},
    )
    assert wh_resp.status_code == 200
    wh_id = wh_resp.json()["id"]

    names_and_codes = ["a", "b", "c"]
    goods_ids = []
    for nc in names_and_codes:
        good_data = {
            "name": nc,
            "code": nc,
            "warehouse_id": wh_id,
        }
        response_ = client.post(
            "/goods",
            json=good_data,
            headers={"Authorization": token},
        )
        assert response_.status_code == 200
        goods_ids.append(response_.json()["id"])

    clients_cnt = 3
    for _ in range(clients_cnt):
        order_data = {
            "delivery_expected_at": int(datetime.now().timestamp() * 1000),
            "delivery_company_id": comp_id,
            "goods": [{"id": g_id, "quantity": 1} for g_id in goods_ids],
        }

        response_ = client.post(
            "/orders",
            json=order_data,
            headers={"Authorization": token},
        )
        assert response_.status_code == 200

    id_ = jwt_decode(token)["id"]
    pagination = {"page": clients_cnt - 1, "per_page": 1}
    query = pagination.copy()
    query.update({"user_id": id_})
    response = client.get(
        "/orders", params=query, headers={"Authorization": token}
    )
    pagination["total_pages"] = clients_cnt

    assert len(response.json()["data"]) == pagination["per_page"]
    assert response.json()["pagination"] == pagination
