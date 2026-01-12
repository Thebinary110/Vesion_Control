from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
# from sqlalchemy.sql import func  
from database import Base

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key = True, nullable = False)
    title = Column(String, nullable = False)
    content = Column(String, nullable = False)
    owner_id = Column(Integer , ForeignKey("Users.id", ondelete = "CASCADE"), nullable = False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default = text("now()"),
        nullable = False
    )
    updated_at = Column(
        TIMESTAMP(timezone = True),
        server_default = text("now()"),
        onupdate = text("now()"),       
        nullable = False  
    )
    