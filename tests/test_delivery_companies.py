from tests import client


def test_delivery_companies_post(token):
    response = client.post(
        "/delivery_companies",
        json={"name": "somemagicaname", "price": 2.0},
        headers={"Authorization": token},
    )
    assert response.status_code == 200
    json = response.json()
    assert json.pop("id", None) is not None
    assert json == {"name": "somemagicaname", "price": 2.0}


def test_delivery_companies_get(token):
    names = ["a", "b", "c"]
    for name in names:
        response = client.post(
            "/delivery_companies",
            json={"name": name, "price": 2.0},
            headers={"Authorization": token},
        )
        assert response.status_code == 200

    query = {"page": 2, "per_page": 1}
    response = client.get(
        "/delivery_companies", params=query, headers={"Authorization": token}
    )
    query["total_pages"] = len(names)

    assert len(response.json()["data"]) == query["per_page"]
    assert response.json()["pagination"] == query
