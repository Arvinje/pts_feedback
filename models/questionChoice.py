from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

# Backtrack to parent dir to prevent import problems
import os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

from models.base import Base
from models.question import Question
from config.setup import engine


tablename = "questionchoices"

class QuestionChoice(Base):
  __tablename__ = tablename

  # Mappers
  id_ = Column(Integer, primary_key=True)
  title_ = Column(String)

  # Question choice is child of question
  question_id_ = Column(Integer, ForeignKey('questions.id_'))
  questions = relationship("Question", back_populates="questionchoices")

  def __init__(self, title_, question_id_):
    self.title_ = title_
    self.question_id_ = question_id_

  def __repr__(self):
    return "<Id: {}, Title: {}, Question_id: {}>".format(self.id_, self.title_, self.question_id_)

  @property
  def serialize(self):
    return {
      'id_' : self.id_,
      'title_' : self.title_,
      'question_id_' : self.question_id_
    }

if not engine.has_table(tablename):
	Base.metadata.create_all(engine)