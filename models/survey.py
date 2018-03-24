from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
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
    __tablename__ = "surveys"

    # Mappers
    id_ = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    def __init__(self, id_, description_):
        self.id_ = id_
        self.description = description_

    def __repr__(self):
        return "<Id_: {}, Question: {}>".format(self.id_, self.description)

    @property
    def serialize(self):
        start_date = self.start_date if self.start_date != None else ''
        end_date = self.end_date if self.end_date != None else ''
        return {
        'id_' : self.id_,
        'description' : self.description,
        'start_date' : start_date,
        'end_date' : end_date,
        }

if not engine.has_table(tablename):
    Base.metadata.create_all(engine)
