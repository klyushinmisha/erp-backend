from tests import client


def test_auth_post():
    response = client.post(
        "/users",
        json={
            "username": "testuser",
            "password": "testpassword",
            "role": "admin",
        },
    )
    assert response.status_code == 200
    response = client.post(
        "/auth", json={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "token" in response.json()
