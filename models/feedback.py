from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

# Backtrack to parent dir to prevent import problems
import os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

from models.base import Base
# from models.admin import Admin  # WAITING
from config.setup import engine


tablename = "feedbacks"

class Feedback(Base):
    __tablename__ = tablename

    # Mappers
    id_ = Column(Integer, primary_key=True)

    # Feedback is parent to answers
    answers = relationship("Answer", back_populates="feedbacks")

    def __repr__(self):
        return "<Id: {}>".format(self.id_)

    @property
    def serialize(self):
        return {
            'id_' : self.id_
        }

if not engine.has_table(tablename):
    Base.metadata.create_all(engine)
