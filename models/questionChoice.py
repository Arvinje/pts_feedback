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


tablename = "questionChoices"

class QuestionChoice(Base):
	__tablename__ = tablename

	#Mappers
	id_ = Column(Integer, primary_key=True)
	title = Column(String)
	question_id = Column(Integer, ForeignKey('question.id_'))
    questions = relationship("Question", back_populates="questionchoices")

	def __init__(self, id_, title, question_id):
		self.id_ = id_
		self.title = title
		self.question_id = question_id

	def __repr__(self):
		return "<Id: {}, Title: {}, Question_id: {}>".format(self.id_, self.title, self.question_id)

	@property
	def serialize(self):
		return {
			'id_' : self.id_,
			'title' : self.title,
			'question_id' : self.question_id
		}

if not engine.has_table(tablename):
    Base.metadata.create_all(engine)
