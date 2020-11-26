from tests import client


def test_warehouses_post(token):
    response = client.post(
        "/warehouses",
        json={"address": "somemagicaddress"},
        headers={"Authorization": token},
    )
    assert response.status_code == 200
    json = response.json()
    assert json.pop("id", None) is not None
    assert json == {"address": "somemagicaddress"}


def test_warehouses_get(token):
    addrs = ["a", "b", "c"]
    for address in addrs:
        response = client.post(
            "/warehouses",
            json={"address": address},
            headers={"Authorization": token},
        )
        assert response.status_code == 200

    query = {"page": 2, "per_page": 1}
    response = client.get(
        "/warehouses", params=query, headers={"Authorization": token}
    )
    query["total_pages"] = len(addrs)

    assert len(response.json()["data"]) == query["per_page"]
    assert response.json()["pagination"] == query
