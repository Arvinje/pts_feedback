from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

# Backtrack to parent dir to prevent import problems
import os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

from models.base import Base

class Feedback(Base):
    __tablename__ = "feedback"

    # Mappers
    id_ = Column(Integer, primary_key=True)
    # answers_ = relationship("Answer")
    # answers = relationship("Answer", back_populates="answers")

    def __init__(self, id_):
        self.id_ = id_

    def __repr__(self):
        return "<Id: {}>".format(self.id_)

    @property
    def serialize(self):
        return {
            'id_' : self.id_
        }
