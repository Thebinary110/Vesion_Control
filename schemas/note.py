from pydantic import BaseModel
from datetime import datetime

class NoteCreated(BaseModel):
    title: str
    content : str   
    
class NoteUpdate(BaseModel):
    title: str
    content: str
    
class NoteResponse(BaseModel):
    id:int
    title: str   
    content:str   
    owner_id:int  
    created_at:datetime
    updated_at:datetime
    
    class Config:
        from_attributes = True
        