from sqlalchemy import Column, ForeignKey, Integer, String, Date
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from config.helper import Base
# from models.answer import Answer

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
