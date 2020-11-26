from datetime import datetime

import magic

from tests import client


def test_documents_post(token):
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
    assert response.status_code == 200

    with open("tests/samples/test.docx", "rb") as doc:
        response = client.post(
            "/documents",
            data={"order_id": response.json()["id"], "name": "custom_doc"},
            files={
                "data": (
                    "tests/samples/test.docx",
                    doc,
                    (
                        "application/vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    ),
                ),
            },
            headers={"Authorization": token},
        )
        assert response.status_code == 200


def test_documents_get(token):
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
    assert response.status_code == 200

    docs_cnt = 3
    with open("tests/samples/test.docx", "rb") as doc:
        for _ in range(docs_cnt):
            response_ = client.post(
                "/documents",
                data={"order_id": response.json()["id"], "name": "custom_doc"},
                files={
                    "data": (
                        "tests/samples/test.docx",
                        doc,
                        (
                            "application/vnd.openxmlformats-officedocument."
                            "wordprocessingml.document"
                        ),
                    ),
                },
                headers={"Authorization": token},
            )
            assert response_.status_code == 200

    query = {"page": docs_cnt - 1, "per_page": 1}
    response = client.get(
        "/documents", params=query, headers={"Authorization": token}
    )
    query["total_pages"] = docs_cnt

    assert len(response.json()["data"]) == query["per_page"]
    assert response.json()["pagination"] == query


def test_document_data_get(token):
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
    assert response.status_code == 200

    with open("tests/samples/test.docx", "rb") as doc:
        response_ = client.post(
            "/documents",
            data={"order_id": response.json()["id"], "name": "custom_doc"},
            files={
                "data": (
                    "tests/samples/test.docx",
                    doc,
                    (
                        "application/vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    ),
                ),
            },
            headers={"Authorization": token},
        )
        assert response_.status_code == 200

    response = client.get(
        f"/documents/{response_.json()['id']}/data",
        cookies={"token": token},
    )
    assert response.status_code == 200
    assert magic.from_buffer(response.content, mime=True) == (
        "application/vnd.openxmlformats-officedocument.wordprocessingml."
        "document"
    )
