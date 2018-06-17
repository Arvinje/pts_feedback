from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

# Backtrack to parent dir to prevent import problems
import os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

from models.base import Base
from config.setup import engine

tablename = "surveys"

class Survey(Base):
    __tablename__ = tablename

    # Mappers
    id_ = Column(Integer, primary_key=True, autoincrement=True)
    name_ = Column(String(50), nullable=False)
    description_ = Column(String(420), nullable=False)
    start_date_ = Column(DateTime)
    end_date_ = Column(DateTime)
    enabled_ = Column(Boolean)

    # Survey is parent to questions
    questions = relationship("Question", back_populates="surveys")

    # Survey is parent to feedback
    # feedbacks = relationship("Feedback", back_populates="surveys")
    feedbacks = relationship("Feedback")

    # Survey is parent to reward
    rewards = relationship("Reward")

    def __init__(self, name_, description_, start_date_, end_date_, enabled_):
        self.name_ = name_
        self.description_ = description_
        self.start_date_ = start_date_
        self.end_date_ = end_date_
        self.enabled_ = enabled_
        # self.admin_id_ = admin_id_  # WAITING

    def __repr__(self):
        return "<id_: {}, name_: {}, description_: {}, start_date_: {}, end_date_: {}, enabled_: {}>".\
                format(self.id_, self.name_, self.description_, self.start_date_, self.end_date_, self.enabled_)

    @property
    def serialize(self):
        start_date_ = self.start_date_ if self.start_date_ != None else ''
        end_date_ = self.end_date_ if self.end_date_ != None else ''
        return {
        'id_' : self.id_,
        'name_' : self.name_,
        'description_' : self.description_,
        'start_date_' : self.start_date_,
        'end_date_' : self.end_date_,
        'enabled_' : self.enabled_
        }

if not engine.has_table(tablename):
    Base.metadata.create_all(engine)
