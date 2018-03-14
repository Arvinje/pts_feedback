from sqlalchemy import Column, ForeignKey, Integer, String, Date
# from sqlalchemy.ext.declarative import declarative_base
import datetime

from config.helper import Base

class Survey(Base):
    __tablename__ = "surveys"

    # Mappers
    id_ = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)

    def __init__(self, id_, description_):
        self.id_ = id_
        self.description = description_

    def __repr__(self):
        return "<Question: {}>".format(self.description)

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
