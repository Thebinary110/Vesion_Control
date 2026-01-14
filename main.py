from fastapi import FastAPI, Depends
from database import engine
from models.user import User
from models.note import Note
from models.version import NoteVersion
from models.comment import Comment

from routers.auth import router as auth_router
from routers.note import router as note_router
from routers.versions import router as version_router
from routers.comments import router as comment_router
from routers.admin import router as admin_router

from utils.dependencies import get_current_user
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(comment_router)
app.include_router(admin_router)
app.include_router(note_router)
app.include_router(version_router)

# Create tables if they don't exist
User.__table__.create(bind=engine, checkfirst=True)
Note.__table__.create(bind=engine, checkfirst=True)
NoteVersion.__table__.create(bind=engine, checkfirst=True)
Comment.__table__.create(bind=engine, checkfirst=True)


@app.get("/")
def root():
    return {"message": "Notes API is running"}


@app.get("/me")
def read_me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email
    }
