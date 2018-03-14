import sys
from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship, sessionmaker

from config.helper import Base

# Classes
from models.survey import Survey
from models.feedback import Feedback
from models.answer import Answer

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print('Usage: python db_setup.py <postgres_url>')
        print('Example postgres_url: postgresql+psycopg2://insi:somepasswd@localhost:5432/llb')
        sys.exit()

    else:
        postgres_url = sys.argv[1]
        try:
            engine = create_engine(postgres_url)
            Base.metadata.create_all(engine)
        except:
            'Cannot bind to database'
