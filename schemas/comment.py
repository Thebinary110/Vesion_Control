from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CommentCreate(BaseModel):
    note_id: int
    content: str
    parent_id: Optional[int] = None

class CommentResponse(BaseModel):
    id: int
    note_id: int
    user_id: int
    parent_id: Optional[int]
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
