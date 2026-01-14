import pytest
from models.comment import Comment
from models.note import Note
from models.user import User


def register_user(client, session, email, password="strongpassword123", role="user"):
    """Register a user and optionally set admin role directly in DB."""
    client.post(
        "/auth/register",
        json={"email": email, "password": password}
    )
    
    if role == "admin":
        user = session.query(User).filter(User.email == email).first()
        if user:
            user.role = "admin"
            session.commit()


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


# ---------------------------------------------------
# ADMIN TESTS - Testing existing endpoints
# ---------------------------------------------------

def test_admin_can_hide_comment(client, session):
    """Test PUT /admin/comments/{comment_id}/hide"""
    register_user(client, session, "admin@gmail.com", role="admin")
    register_user(client, session, "commenter@gmail.com")

    commenter_token = get_token(client, "commenter@gmail.com")
    note_id = create_note(client, commenter_token)

    # Get commenter's user_id
    commenter = session.query(User).filter(User.email == "commenter@gmail.com").first()
    comment_id = create_comment_in_db(session, note_id, commenter.id, "Comment to hide")

    admin_token = get_token(client, "admin@gmail.com")

    res = client.put(
        f"/admin/comments/{comment_id}/hide",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert res.status_code == 200
    assert res.json()["message"] == "Comment hidden"

    # Verify comment is marked as deleted
    comment = session.query(Comment).filter(Comment.id == comment_id).first()
    assert comment.is_deleted is True


def test_non_admin_cannot_hide_comment(client, session):
    """Test that regular users cannot hide comments"""
    register_user(client, session, "normal@gmail.com")
    register_user(client, session, "author@gmail.com")

    author_token = get_token(client, "author@gmail.com")
    note_id = create_note(client, author_token)

    author = session.query(User).filter(User.email == "author@gmail.com").first()
    comment_id = create_comment_in_db(session, note_id, author.id)

    normal_token = get_token(client, "normal@gmail.com")

    res = client.put(
        f"/admin/comments/{comment_id}/hide",
        headers={"Authorization": f"Bearer {normal_token}"}
    )

    assert res.status_code == 403


def test_admin_can_lock_comments_on_note(client, session):
    """Test PUT /admin/notes/{note_id}/lock-comments"""
    register_user(client, session, "admin2@gmail.com", role="admin")
    register_user(client, session, "noteowner@gmail.com")

    owner_token = get_token(client, "noteowner@gmail.com")
    note_id = create_note(client, owner_token)

    admin_token = get_token(client, "admin2@gmail.com")

    res = client.put(
        f"/admin/notes/{note_id}/lock-comments",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert res.status_code == 200
    assert res.json()["message"] == "Comments locked"

    # Verify note has comments locked
    note = session.query(Note).filter(Note.id == note_id).first()
    assert note.comments_locked is True


def test_non_admin_cannot_lock_comments(client, session):
    """Test that regular users cannot lock comments on notes"""
    register_user(client, session, "user1@gmail.com")
    register_user(client, session, "user2@gmail.com")

    user1_token = get_token(client, "user1@gmail.com")
    note_id = create_note(client, user1_token)

    user2_token = get_token(client, "user2@gmail.com")

    res = client.put(
        f"/admin/notes/{note_id}/lock-comments",
        headers={"Authorization": f"Bearer {user2_token}"}
    )

    assert res.status_code == 403


def test_hide_nonexistent_comment_returns_404(client, session):
    """Test hiding a comment that doesn't exist"""
    register_user(client, session, "admin3@gmail.com", role="admin")
    admin_token = get_token(client, "admin3@gmail.com")

    res = client.put(
        "/admin/comments/99999/hide",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert res.status_code == 404


def test_lock_comments_on_nonexistent_note_returns_404(client, session):
    """Test locking comments on a note that doesn't exist"""
    register_user(client, session, "admin4@gmail.com", role="admin")
    admin_token = get_token(client, "admin4@gmail.com")

    res = client.put(
        "/admin/notes/99999/lock-comments",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert res.status_code == 404
