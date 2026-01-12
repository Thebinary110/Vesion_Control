from fastapi import FastAPI, Depends
from database import engine
from models import User, Note
from routers.auth import router as auth_router
from utils.dependencies import get_current_user
from routers.note import router as note_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(note_router)
User.__table__.create(bind=engine,  checkfirst = True) ## this will tell sql alchemy that if the user table doesn't exist then create it
Note.__table__.create(bind = engine, checkfirst  = True) ## this will also first check if there is the table if nto create it


@app.get('/')
def main():
    return {
  "message": "Notes API is running"
}


@app.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return{
        "id": current_user.id, 
        "email": current_user.email
    }
    
