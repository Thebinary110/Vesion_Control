from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from database import Base


class NoteVersion(Base):
    __tablename__ = "note_versions"

    id = Column(Integer, primary_key=True, nullable=False)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    version_number = Column(Integer, nullable = False)
    
    title = Column(String, nullable = False)
    content = Column(String, nullable = False)
    
    edited_by = Column(Integer, ForeignKey("users.id", ondelete = "CASCADE"), nullable = False) 
    created_at = Column(DateTime(timezone = True), server_default = text("now()"), nullable = False)
    
