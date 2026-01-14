import pytest


def register_user(client, email, password="strongpassword123", role="user"):
    client.post(
        "/auth/register",
        json={"email": email, "password": password}
    )

    if role == "admin":
        client.patch(
            f"/admin/promote/{email}",
            headers={"Authorization": f"Bearer {get_token(client, email, password)}"}
        )


def get_token(client, email, password="strongpassword123"):
    res = client.post(
        "/auth/login",
        data={"username": email, "password": password}
    )
    return res.json()["access_token"]


def create_note(client, token):
    res = client.post(
        "/notes",
        json={"title": "Admin Test Note", "content": "Content"},
        headers={"Authorization": f"Bearer {token}"}
    )
    return res.json()["id"]


def create_comment(client, token, note_id):
    res = client.post(
        f"/notes/{note_id}/comments",
        json={"content": "Admin comment"},
        headers={"Authorization": f"Bearer {token}"}
    )
    return res.json()["id"]


# ---------------------------------------------------
# ADMIN TESTS
# ---------------------------------------------------

def test_admin_can_list_users(client):
    register_user(client, "admin@gmail.com", role="admin")
    register_user(client, "user1@gmail.com")

    admin_token = get_token(client, "admin@gmail.com")

    res = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert res.status_code == 200
    data = res.json()

    assert isinstance(data, list)
    assert any(u["email"] == "admin@gmail.com" for u in data)
    assert any(u["email"] == "user1@gmail.com" for u in data)


def test_non_admin_cannot_list_users(client):
    register_user(client, "normal@gmail.com")
    token = get_token(client, "normal@gmail.com")

    res = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code == 403


def test_admin_can_delete_any_user(client):
    register_user(client, "admin2@gmail.com", role="admin")
    register_user(client, "victim@gmail.com")

    admin_token = get_token(client, "admin2@gmail.com")

    res = client.delete(
        "/admin/users/victim@gmail.com",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert res.status_code == 204


def test_admin_can_delete_any_note(client):
    register_user(client, "admin3@gmail.com", role="admin")
    register_user(client, "author@gmail.com")

    author_token = get_token(client, "author@gmail.com")
    note_id = create_note(client, author_token)

    admin_token = get_token(client, "admin3@gmail.com")

    res = client.delete(
        f"/admin/notes/{note_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert res.status_code == 204


def test_admin_can_delete_any_comment(client):
    register_user(client, "admin4@gmail.com", role="admin")
    register_user(client, "commenter@gmail.com")

    commenter_token = get_token(client, "commenter@gmail.com")
    note_id = create_note(client, commenter_token)
    comment_id = create_comment(client, commenter_token, note_id)

    admin_token = get_token(client, "admin4@gmail.com")

    res = client.delete(
        f"/admin/comments/{comment_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert res.status_code == 204


def test_user_cannot_delete_others_comment(client):
    register_user(client, "userA@gmail.com")
    register_user(client, "userB@gmail.com")

    tokenA = get_token(client, "userA@gmail.com")
    tokenB = get_token(client, "userB@gmail.com")

    note_id = create_note(client, tokenA)
    comment_id = create_comment(client, tokenA, note_id)

    res = client.delete(
        f"/comments/{comment_id}",
        headers={"Authorization": f"Bearer {tokenB}"}
    )

    assert res.status_code == 403
