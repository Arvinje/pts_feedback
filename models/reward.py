from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

# Backtrack to parent dir to prevent import problems
import os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

from models.base import Base
from config.setup import engine

tablename = "rewards"

class Reward(Base):
    __tablename__ = tablename

    # Mappers
    id_ = Column(Integer, primary_key=True, autoincrement=True)
    value_ = Column(String(250), nullable=False)

    # Reward is child of survey
    survey_id_ = Column(Integer, ForeignKey('surveys.id_'))
    surveys = relationship("Survey", back_populates='rewards')

    # Reward is child of feedback
    feedback_id_ = Column(Integer, ForeignKey('feedbacks.id_'))
    feedbacks = relationship("Feedback", back_populates='rewards')

    def __init__(self, value_, survey_id_, feedback_id_):
        self.value_ = value_
        self.survey_id_ = survey_id_

    def __repr__(self):
        return "<id_: {}, value_: {}, survey_id_: {}, feedback_id_: {}>".format(self.id_, self.value_, self.survey_id_, self.feedback_id_)

    @property
    def serialize(self):
        return {
        'id_' : self.id_,
        'value_' : self.value_,
        'survey_id_' : self.survey_id_,
        'feedback_id_' : self.feedback_id_
        }

if not engine.has_table(tablename):
    Base.metadata.create_all(engine)
