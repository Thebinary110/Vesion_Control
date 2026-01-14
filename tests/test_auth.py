def test_register_user(client):
    res = client.post(
        "/auth/register",
        json={
            "email": "testuser@gmail.com",
            "password": "strongpassword123"
        }
    )

    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "testuser@gmail.com"
    assert "id" in data


def test_login_user(client):
    res = client.post(
        "/auth/login",
        data={
            "username": "testuser@gmail.com",
            "password": "strongpassword123"
        }
    )

    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
