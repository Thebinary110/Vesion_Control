def register_and_get_token(client):
    """Register a user and return their access token."""
    client.post(
        "/auth/register",
        json={
            "email": "testuser@gmail.com",
            "password": "strongpassword123"
        }
    )

    res = client.post(
        "/auth/login",
        data={
            "username": "testuser@gmail.com",
            "password": "strongpassword123"
        }
    )
    return res.json()["access_token"]


def test_create_note(client):
    token = register_and_get_token(client)

    res = client.post(
        "/notes/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Note",
            "content": "This is a test note"
        }
    )

    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "This is a test note"


def test_get_notes(client):
    token = register_and_get_token(client)

    res = client.get(
        "/notes/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code == 200
    assert isinstance(res.json(), list)
