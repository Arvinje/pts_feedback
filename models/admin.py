from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

# Backtrack to parent dir to prevent import problems
import os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

from models.base import Base
from config.setup import engine


tablename = "admins"

class Admin(Base):
    __tablename__ = tablename

    # Mappers
    id_ = Column(Integer, primary_key=True)
    email_ = Column(String, nullable=False)
    password_ = Column(String, nullable=False)

    # Admin is parent to surveys
    surveys = relationship("Survey", back_populates="admins")

    def __init__(self, id_, email_, password_):
        self.id_ = id_
        self.email_ = email_
        self.password_ = password_

    def __repr__(self):
        return "<Id: {}, Email: {}, Password: {}>".format(self.id_, self.email_, self.password_)

    @property
    def serialize(self):
        return {
            'id' : self.id_,
            'email' : self.email_,
            'password' : self.password_
        }

if not engine.has_table(tablename):
    Base.metadata.create_all(engine)
