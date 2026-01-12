from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from database import get_db
from models import Note
from schemas.note import NoteCreated, NoteResponse
from utils.dependencies import get_current_user
from models.user import User

router =  APIRouter(prefix="/notes", tags=["Notes"])

@router.post("/", response_model = NoteResponse, status_code  = status.HTTP_201_CREATED)
def create_note(note:NoteCreated, db:Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    
    new_note = Note(
        title = note.title,
        content = note.content,
        owner_id = current_user.id
    )
    
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    
    return new_note