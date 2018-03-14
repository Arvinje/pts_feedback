from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship, sessionmaker

from config.helper import Base

# Classes
from models.survey import Survey
from models.feedback import Feedback
from models.answer import Answer

# Configuration code again
postgres_url = 'postgresql+psycopg2://insi:somepasswd@localhost:5432/llb'
engine = create_engine(postgres_url)

Base.metadata.create_all(engine)

# Testing
s = Survey(1, 'This survey is magnificent.')
f = Feedback(1)
a = Answer(2, 'blaa', 2) # UPDATE!

