from tests import client


def test_good_post(token):
    response = client.post(
        "/warehouses",
        json={"address": "somemagicaddress"},
        headers={"Authorization": token},
    )
    assert response.status_code == 200

    good_data = {
        "name": "some_name",
        "code": "some_code",
        "warehouse_id": response.json()["id"],
    }
    response = client.post(
        "/goods",
        json=good_data,
        headers={"Authorization": token},
    )
    assert response.status_code == 200
    json = response.json()
    assert json.pop("id", None) is not None
    assert json == good_data


def test_goods_get(token):
    response = client.post(
        "/warehouses",
        json={"address": "somemagicaddress"},
        headers={"Authorization": token},
    )
    assert response.status_code == 200

    names_and_codes = ["a", "b", "c"]
    for nc in names_and_codes:
        good_data = {
            "name": nc,
            "code": nc,
            "warehouse_id": response.json()["id"],
        }
        response_ = client.post(
            "/goods",
            json=good_data,
            headers={"Authorization": token},
        )
        assert response_.status_code == 200

    query = {"page": len(names_and_codes) - 1, "per_page": 1}
    response = client.get(
        "/goods", params=query, headers={"Authorization": token}
    )
    query["total_pages"] = len(names_and_codes)

    assert len(response.json()["data"]) == query["per_page"]
    assert response.json()["pagination"] == query
