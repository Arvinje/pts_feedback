from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

# Classes

class Survey(Base):
    __tablename__ = "surveys"

    # Mappers
    id_ = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    def __init__(self, id_, description_):
        self.id = id_
        self.description = description_

    def __repr__(self):
        return "<Question: {}>".format(self.description)

    @property
    def serialize(self):
        return {
            'id_' : self.id_,
            'description' : self.description,
            'start_date' : self.start_date,
            'end_date' : self.end_date,
        }



class Feedback(Base):
    __tablename__ = "feedback"

    # Mappers
    id_ = Column(Integer, primary_key=True)

    def __init__(self, id_):
        self.id_ = id_

    def __repr__(self):
        return "<Id: {}>".format(self.id_)

    @property
    def serialize(self):
        return {
            'id_' : self.id_
        }


import datetime
class Answer(Base):
    __tablename__ = "answers"

    # Mappers
    id_ = Column(Integer, primary_key=True)
    value = Column(String)
    created_at = Column(Date, nullable=False)
    feedback_id = Column(Integer, ForeignKey('feedback.id_')) # UPDATE!
    feedback = relationship(Feedback)
    # question_id = Column(Integer, ForeignKey('question.id_')) # UPDATE!
    # question = relationship(Question)

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

# # Testing
# s = Survey(1, 'This survey is magnificent.')
# f = Feedback(1)
# a = Answer(1, 'blaa', 1) # UPDATE!

# Configuration code again
postgres_url = 'postgresql+psycopg2://insi:somepasswd@localhost:5432/llb'
# engine = create_engine('postgresql:///llb.db')
engine = create_engine(postgres_url)
Base.metadata.create_all(engine)
