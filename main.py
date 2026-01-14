from fastapi import FastAPI, Depends
from database import engine
from models import User, Note
from models.version import NoteVersion
from routers.auth import router as auth_router
from routers.note import router as note_router
from routers.versions import router as versions_router
from utils.dependencies import get_current_user

app = FastAPI()

app.include_router(auth_router)
app.include_router(note_router)
app.include_router(versions_router)

# ⚠️ TEMP table creation (before Alembic)
User.__table__.create(bind=engine, checkfirst=True)
Note.__table__.create(bind=engine, checkfirst=True)
NoteVersion.__table__.create(bind=engine, checkfirst=True)

@app.get("/")
def main():
    return {"message": "Notes API is running"}

@app.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email
    }
