import pytest
from models.comment import Comment
from models.note import Note
from models.user import User


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


def create_comment_in_db(session, note_id, user_id, content="Test comment"):
    """Create a comment directly in the database."""
    comment = Comment(
        note_id=note_id,
        user_id=user_id,
        content=content,
        is_deleted=False
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment.id


def get_user_id(session, email):
    """Get user ID by email."""
    user = session.query(User).filter(User.email == email).first()
    return user.id if user else None


# ---------------------------------------------------
# COMMENT TESTS - Testing existing endpoints
# ---------------------------------------------------

def test_get_comments_for_note(client, session):
    """Test GET /comments/note/{note_id}"""
    token = register_and_login(client)
    note_id = create_note(client, token)

    user_id = get_user_id(session, "commenter@gmail.com")

    # Create comments directly in DB
    create_comment_in_db(session, note_id, user_id, "Comment A")
    create_comment_in_db(session, note_id, user_id, "Comment B")

    res = client.get(f"/comments/note/{note_id}")

    assert res.status_code == 200
    data = res.json()

    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["content"] == "Comment A"
    assert data[1]["content"] == "Comment B"


def test_get_comments_excludes_deleted(client, session):
    """Test that deleted comments are not returned"""
    token = register_and_login(client, "viewer@gmail.com")
    note_id = create_note(client, token)

    user_id = get_user_id(session, "viewer@gmail.com")

    # Create a visible comment
    create_comment_in_db(session, note_id, user_id, "Visible comment")

    # Create a deleted comment directly in DB
    deleted_comment = Comment(
        note_id=note_id,
        user_id=user_id,
        content="Deleted comment",
        is_deleted=True
    )
    session.add(deleted_comment)
    session.commit()

    res = client.get(f"/comments/note/{note_id}")

    assert res.status_code == 200
    data = res.json()

    assert len(data) == 1
    assert data[0]["content"] == "Visible comment"


def test_get_comments_empty_for_note_without_comments(client, session):
    """Test that notes without comments return empty list"""
    token = register_and_login(client, "nocomments@gmail.com")
    note_id = create_note(client, token)

    res = client.get(f"/comments/note/{note_id}")

    assert res.status_code == 200
    data = res.json()

    assert isinstance(data, list)
    assert len(data) == 0


def test_get_comments_returns_ordered_by_created_at(client, session):
    """Test that comments are returned in order of creation"""
    token = register_and_login(client, "order@gmail.com")
    note_id = create_note(client, token)

    user_id = get_user_id(session, "order@gmail.com")

    # Create comments in order
    create_comment_in_db(session, note_id, user_id, "First")
    create_comment_in_db(session, note_id, user_id, "Second")
    create_comment_in_db(session, note_id, user_id, "Third")

    res = client.get(f"/comments/note/{note_id}")

    assert res.status_code == 200
    data = res.json()

    assert len(data) == 3
    assert data[0]["content"] == "First"
    assert data[1]["content"] == "Second"
    assert data[2]["content"] == "Third"


def test_get_comments_for_nonexistent_note_returns_empty(client, session):
    """Test getting comments for a note that doesn't exist returns empty list"""
    res = client.get("/comments/note/99999")

    assert res.status_code == 200
    data = res.json()

    assert isinstance(data, list)
    assert len(data) == 0
