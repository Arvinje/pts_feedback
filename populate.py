import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.db_setup import Base, Survey, Feedback, Answer

if __name__ == '__main__':

	if len(sys.argv) < 2:
		print('Usage: python populate.py <postgres_url>')
		print('Example postgres_url: postgresql+psycopg2://insi:somepasswd@localhost:5432/llb')
		sys.exit()

	else:
		postgres_url = sys.argv[1]
		try:
			engine = create_engine(postgres_url)      # engine bound to type of database
			Base.metadata.bind = engine               # base class (+ my classes) bound to engine
			DBSession = sessionmaker(bind=engine)     # session class bound to engine
			session = DBSession()                     # instance of session class

			# Note:

			# Session not persisted into db until:
			# session.commit()

			# If needed to revert all changes back to the last commit, call:
			# session.rollback()


			# Create entries
			s = Survey(1, 'Magnificent survey')
			f = Feedback(1)
			a = Answer(2, 'bla', 2)

			# Add to db
			session.add(s)
			session.commit()

			# Get list of all surveys
			session.query(Survey).all()

			# Get first survey
			first_survey = session.query(Survey).first()

			# Filter by description
			survey_1 = session.query(Survey).filter_by(id_=1).one()

			# Update
			survey_1 = session.query(Survey).filter_by(id_=1).one() # ensure only one is returned
			survey_1.description = 'Even more magnificent survey'
			session.add(survey_1) # This effectively updates
			session.commit()

			# # Delete
			# survey_1 = session.query(Survey).filter_by(id_=1).one()
			# session.delete(survey_1)
			# session.commit()

		except:
			print('Cannot bind to database')