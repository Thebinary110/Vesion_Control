from fastapi import APIRouter, Depends , HTTPException, status
from sqlalchemy.orm import Session
from typing import List  

from database import get_db
from models.version import NoteVersion
from models.note import Note
from models.user import User
from schemas.version import VersionResponse
from utils.dependencies import get_current_user

router = APIRouter(prefix = "/notes", tags = ["Versions"])

@router.get("/{note_id}/versions", response_model = List[VersionResponse])
def list_versions(
    note_id: int,   
    db: Session =  Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.owner_id  == current_user.id   
    ).first()
    
    if not note:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Version not found"
        )
    return db.query(NoteVersion).filter(NoteVersion.note_id == note_id).order_by(NoteVersion.version_number).all()

@router.get("/{note_id}/versions/{version_no}", response_model = VersionResponse)
def get_version(
    note_id: int,
    version_no: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    version = db.query(NoteVersion).filter(
        NoteVersion.note_id == note_id,
        NoteVersion.version_number == version_no
    ).first()
    
    if not version:
        raise HTTPException(status_code = 404, detail = "Version not found")
    
    return version

@router.post("/{note_id}/restore/{version_no}")
def restore_version(
    note_id: int,
    version_no: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.owner_id == current_user.id
    ).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    version = db.query(NoteVersion).filter(
        NoteVersion.note_id == note_id,
        NoteVersion.version_number == version_no
    ).first()

    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    note.title = version.title
    note.content = version.content

    db.commit()
    return {"message": f"Restored to version {version_no}"}