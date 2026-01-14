from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.comment import Comment
from models.note import Note
from models.user import User
from utils.dependencies import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])


def require_admin(user: User):
    if user.role != "admin":
        raise HTTPException(403, "Admin access only")


@router.put("/comments/{comment_id}/hide")
def hide_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_admin(current_user)

    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(404, "Comment not found")

    comment.is_deleted = True
    db.commit()

    return {"message": "Comment hidden"}


@router.put("/notes/{note_id}/lock-comments")
def lock_comments(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_admin(current_user)

    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(404, "Note not found")

    note.comments_locked = True
    db.commit()

    return {"message": "Comments locked"}

