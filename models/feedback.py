from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

# Backtrack to parent dir to prevent import problems
import os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

from models.base import Base
from config.setup import engine


tablename = "feedbacks"

class Feedback(Base):
    __tablename__ = tablename

    # Mappers
    id_ = Column(Integer, primary_key=True, autoincrement=True)

    # Feedback is child of survey
    survey_id_ = Column(Integer, ForeignKey('surveys.id_'))  # Nullable because of bug (?), must be added afterwards
    # surveys = relationship("Survey", back_populates="feedbacks")

    # Feedback is parent to answers
    answers = relationship("Answer", back_populates="feedbacks")

    # Feedback is parent to reward
    rewards = relationship("Reward")

    def __init__(self, survey_id_):
        survey_id_ = survey_id_

    def __repr__(self):
        return "<id_: {}, survey_id_: {}>".format(self.id_, self.survey_id_)

    @property
    def serialize(self):
        return {
            'id_' : self.id_,
            'survey_id_' : self.survey_id_
        }

if not engine.has_table(tablename):
    Base.metadata.create_all(engine)
