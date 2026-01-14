from pydantic import BaseModel
from datetime import datetime

class VersionResponse(BaseModel):
    id: int 
    version_number:int   
    title:str   
    content:str   
    edited_by: int   
    created_at: datetime
    
    class Config:
        orm_mode = True
        
        