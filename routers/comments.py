from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.comment import Comment
from models.note import Note
from models.user import User
from schemas.comment import CommentCreate, CommentResponse
from utils.dependencies import get_current_user

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.get("/note/{note_id}", response_model=List[CommentResponse])
def get_comments(
    note_id: int,
    db: Session = Depends(get_db)
):
    return (
        db.query(Comment)
        .filter(
            Comment.note_id == note_id,
            Comment.is_deleted == False
        )
        .order_by(Comment.created_at.asc())
        .all()
    )

