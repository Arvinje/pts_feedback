import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# NOTE:
# Db connection requires setting up environment variable, e.g.:
# $ export LLB_POSTGRES_URL="postgresql+psycopg2://<insert_user_name>:somepasswd@localhost:5432/llb"

# Bind SQLAlchemy
postgres_url = os.environ['LLB_POSTGRES_URL']
engine = create_engine(postgres_url, echo=True)      # engine bound to type of database
Base.metadata.bind = engine               # base class (+ my classes) bound to engine
DBSession = sessionmaker(bind=engine)     # session class bound to engine
session = DBSession()                     # instance of session class

