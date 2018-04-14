from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
import datetime

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
    id_ = Column(Integer, primary_key=True,autoincrement=True)
    description_ = Column(String, nullable=False)
    start_date_ = Column(DateTime)
    end_date_ = Column(DateTime)

    # Survey is child of admin
    admin_id_ = Column(Integer, ForeignKey('admins.id_'))
    admins = relationship("Admin", back_populates='surveys')

    # Survey is parent to questions
    questions = relationship("Question", back_populates="surveys")

    def __init__(self, id_, description_, start_date_, end_date_, admin_id_):
        self.id_ = id_
        self.description_ = description_
        self.start_date_ = start_date_
        self.end_date_ = end_date_
        self.admin_id_ = admin_id_

    def __repr__(self):
        return "<Id_: {}, Survey: {}, Start date: {}, End date: {}>".format(self.id_, self.description_, self.start_date_, self.end_date_)

    @property
    def serialize(self):
        start_date_ = self.start_date_ if self.start_date_ != None else ''
        end_date_ = self.end_date_ if self.end_date_ != None else ''
        return {
        'id' : self.id_,
        'description' : self.description_,
        'start_date' : self.start_date_,
        'end_date' : self.end_date_
        }

if not engine.has_table(tablename):
    Base.metadata.create_all(engine)
