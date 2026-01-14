from fastapi import FastAPI, Depends
from database import engine
from models import User, Note, NoteVersion

from routers.auth import router as auth_router
from routers.note import router as note_router
from routers.versions import router as version_router

from utils.dependencies import get_current_user

app = FastAPI()

app.include_router(auth_router)
app.include_router(note_router)
app.include_router(version_router)

# TEMP TABLE CREATION (OK for now, Alembic already exists)
User.__table__.create(bind=engine, checkfirst=True)
Note.__table__.create(bind=engine, checkfirst=True)
NoteVersion.__table__.create(bind=engine, checkfirst=True)


@app.get("/")
def root():
    return {"message": "Notes API is running"}


@app.get("/me")
def read_me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email
    }
