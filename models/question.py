from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
import datetime

# Backtrack to parent dir to prevent import problems
# made by Saija, not sure if working properly 29.3.2018
import os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

from models.base import Base
from models.feedback import Feedback
from config.setup import engine

tablename = "questions"

class Question(Base):
    __tablename__ = "questions"


    id_ = Column(Integer, primary_key=True)
    type = Column(String)
    title = Column(String)
    survey_id = Column(Integer, ForeignKey('survey.id_'))
    survey = relationship("Survey", back_populates="questions")

    def __init__(self, id_, type, title, survey_id):
        self.id_ = id_
        self.type = type
        self.title = title
        self.survey_id = survey_id

    def __repr__(self):
        return "<Id: {},Type: '{}', Title: '{}', Survey_id {}>".format(self.id_, self.type, self.title, self.survey_id)

    @property
    def serialize(self):
        return {
            'id_' : self.id_,
            'type' : self.type,
            'title' : self.title,
            'survey' : self.survey
        }

if not engine.has_table(tablename):
    Base.metadata.create_all(engine)
