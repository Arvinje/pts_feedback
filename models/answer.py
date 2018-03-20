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
# from models.question import Question # UPDATE!

class Answer(Base):
    __tablename__ = "answers"

    # Mappers
    id_ = Column(Integer, primary_key=True)
    value = Column(String)
    created_at = Column(DateTime, nullable=False)
    feedback_id = Column(Integer, ForeignKey('feedback.id_')) # UPDATE!
    feedback_ = relationship("Feedback")
    # question = relationship(Question)
    # question_id = Column(Integer, ForeignKey('question.id_')) # UPDATE!

    # def __init__(self, id_, value_, question_id_, feedback_id_): # UPDATE!
    def __init__(self, id_, value_, feedback_id_):
        self.id_ = id_
        self.value =  value_
        self.created_at = datetime.datetime.now()
        self.feedback_id = feedback_id_
        # self.question_id = question_id_

    def __repr__(self):
        # return "<Id: {}, Created_at: '{}', Question_id: {}, Feedback_id {}, Value: '{}'>".format(self.id_, self.created_at, self.question_id, self.feedback_id, self.value)
        return "<Id: {}, Created_at: '{}', Feedback_id: {}, Value: '{}'>".format(self.id_, self.created_at, self.feedback_id, self.value) # UPDATE!

    @property
    def serialize(self):
        return {
            'id_' : self.id_,
            'value' : self.value,
            'created_at' : self.created_at.isoformat(),
            # 'question_id' : self.question_id,
            'feedback_id' : self.feedback_id
        }
