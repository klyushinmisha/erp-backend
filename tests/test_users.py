from tests import client


def test_users_post():
    response = client.post(
        "/users",
        json={
            "username": "testuser",
            "password": "testpassword",
            "role": "admin",
        },
    )
    assert response.status_code == 200
    assert "token" in response.json()
