from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Note
from schemas.note import NoteCreated, NoteResponse, NoteUpdate
from models.version import NoteVersion
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


## this can get all the notes
@router.get("/", response_model=List[NoteResponse])
def get_notes(
    db:Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notes = db.query(Note).filter(Note.owner_id == current_user.id).all()
    return notes

##Get single NOte
@router.get("/{id}", response_model = NoteResponse)
def get_note(id : int, db:Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = db.query(Note).filter(Note.id == id, Note.owner_id == current_user.id).first()
    
    if not note:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Note not Found"
        )
        
    return note  

@router.put("/{id}", response_model = NoteResponse)
def update_note(id: int,
    updated_note: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    note = db.query(Note).filter(
        Note.id == id,
        Note.owner_id == current_user.id
    ).first()

    if not note:
        raise HTTPException(
            status_code=404, 
            detail="Note not found"
            )

    #  Get latest version number
    last_version = db.query(NoteVersion).filter(NoteVersion.note_id == id).order_by(NoteVersion.version_number.desc()).first()

    next_version = 1 if not last_version else last_version.version_number + 1

    #  Save old version
    version = NoteVersion(
        note_id=id,
        version_number=next_version,
        title=note.title,
        content=note.content,
        edited_by=current_user.id
    )

    db.add(version)

    #  Update note
    note.title = updated_note.title
    note.content = updated_note.content

    db.commit()
    db.refresh(note)

    return note
    
@router.delete("/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_note(
    id:int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note_query = db.query(Note).filter(
        Note.id == id,
        Note.owner_id == current_user.id  
    )
    
    note = note_query.first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    note_query.delete(synchronize_session =False) 
    db.commit()
    
    return {"Message" : f"Note with id: {id} is deleted Successfully"}