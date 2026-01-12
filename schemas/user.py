from pydantic import BaseModel, EmailStr,Field
# import annotated_types
# from typing_extensions import Annotated

class UserCreate(BaseModel):
    email: EmailStr
    password:str = Field(min_length=8, max_length= 72)  
    
class UserResponse(BaseModel):
    id:int
    email:EmailStr
    
    class Config:
        from_attributtes = True