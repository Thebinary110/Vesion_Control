from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from database import Base

class Note(Base):
    __tablename__ = "note"
    
    id = Column(Integer, primary_key = True, nullable = False)
    content = Column(String, nullable = False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default = text("now()"),
        nullable = False
    )