from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
import datetime

# Backtrack to parent dir to prevent import problems
import os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

from models.base import Base
from models.feedback import Feedback

class Question(Base):
    __tablename__ = "answers"

    # Mappers
    id_ = Column(Integer, primary_key=True)
    # Et cetera

    def __init__(self, id_):
        self.id_ = id_
        # Et cetera

    def __repr__(self):
        return "<Id: {}>".format(self.id_)

    @property
    def serialize(self):
        return {
            'id_' : self.id_,
            # Et cetera
        }
