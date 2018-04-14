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

    id_ = Column(Integer, primary_key=True,autoincrement=True)
    type_ = Column(String)
    title = Column(String)
    survey_id = Column(Integer, ForeignKey('surveys.id_'))
    survey = relationship("Survey", back_populates="questions")
    questionChoices = relationship("QuestionChoice", back_populates="question")

    def __init__(self, type_, title, survey_id):
        self.type_ = type_
        self.title = title
        self.survey_id = survey_id

    def __repr__(self):
        return "<Id: {},Type: '{}', Title: '{}', Survey_id {}>".format(self.id_, self.type_, self.title, self.survey_id)

    @property
    def serialize(self):
        return {
            'id_' : self.id_,
            'type_' : self.type_,
            'title' : self.title,
            'survey' : self.survey
        }

if not engine.has_table(tablename):
    Base.metadata.create_all(engine)
