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

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify note exists
    note = db.query(Note).filter(Note.id == comment.note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    if note.comments_locked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comments are locked for this note"
        )

    new_comment = Comment(
        note_id = comment.note_id,
        user_id = current_user.id,
        content = comment.content,
        parent_id = comment.parent_id
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


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


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == id).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
        
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment"
        )

    # Soft delete
    comment.is_deleted = True
    db.commit()
