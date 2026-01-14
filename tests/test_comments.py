import pytest


def register_and_login(client, email="commenter@gmail.com", password="strongpassword123"):
    client.post(
        "/auth/register",
        json={"email": email, "password": password}
    )

    res = client.post(
        "/auth/login",
        data={"username": email, "password": password}
    )

    return res.json()["access_token"]


def create_note(client, token):
    res = client.post(
        "/notes",
        json={"title": "Test Note", "content": "Test Content"},
        headers={"Authorization": f"Bearer {token}"}
    )
    return res.json()["id"]


def test_create_comment(client):
    token = register_and_login(client)
    note_id = create_note(client, token)

    res = client.post(
        f"/notes/{note_id}/comments",
        json={"content": "First comment"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code == 201
    data = res.json()

    assert data["content"] == "First comment"
    assert data["note_id"] == note_id
    assert "id" in data
    assert "created_at" in data


def test_get_comments(client):
    token = register_and_login(client, "viewer@gmail.com")
    note_id = create_note(client, token)

    client.post(
        f"/notes/{note_id}/comments",
        json={"content": "Comment A"},
        headers={"Authorization": f"Bearer {token}"}
    )

    client.post(
        f"/notes/{note_id}/comments",
        json={"content": "Comment B"},
        headers={"Authorization": f"Bearer {token}"}
    )

    res = client.get(
        f"/notes/{note_id}/comments",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code == 200
    data = res.json()

    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["content"] == "Comment A"
    assert data[1]["content"] == "Comment B"


def test_comment_requires_auth(client):
    res = client.post(
        "/notes/1/comments",
        json={"content": "No auth"}
    )

    assert res.status_code == 401


def test_delete_own_comment(client):
    token = register_and_login(client, "deleter@gmail.com")
    note_id = create_note(client, token)

    res = client.post(
        f"/notes/{note_id}/comments",
        json={"content": "To be deleted"},
        headers={"Authorization": f"Bearer {token}"}
    )

    comment_id = res.json()["id"]

    delete_res = client.delete(
        f"/comments/{comment_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert delete_res.status_code == 204


def test_cannot_delete_others_comment(client):
    token1 = register_and_login(client, "user1@gmail.com")
    token2 = register_and_login(client, "user2@gmail.com")

    note_id = create_note(client, token1)

    res = client.post(
        f"/notes/{note_id}/comments",
        json={"content": "User1 comment"},
        headers={"Authorization": f"Bearer {token1}"}
    )

    comment_id = res.json()["id"]

    res = client.delete(
        f"/comments/{comment_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )

    assert res.status_code == 403
