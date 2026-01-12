import sys
import os

sys.path.append(os.path.abspath(os.getcwd()))


from database import Base
from models import User, Note, NoteVersion

target_metadata = Base.metadata
