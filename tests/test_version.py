def get_token(client):
    res = client.post(
        "/auth/login",
        data={
            "username": "testuser@gmail.com",
            "password": "strongpassword123"
        }
    )
    return res.json()["access_token"]


def test_note_versioning(client):
    token = get_token(client)

    # Create note
    create = client.post(
        "/notes/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "V1", "content": "First version"}
    )
    note_id = create.json()["id"]

    # Update note
    update = client.put(
        f"/notes/{note_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "V2", "content": "Second version"}
    )
    assert update.status_code == 200

    # Get versions
    versions = client.get(
        f"/notes/{note_id}/versions",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert versions.status_code == 200
    assert len(versions.json()) == 1
