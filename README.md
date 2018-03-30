# Feedback Gathering Tool for Public Transportation Services

This is a web app for feedback gathering on [Living Lab Bus](http://livinglabbus.fi) platform. Currently, it's being developed by a group of students at University of Tampere, Finland.


#### Requirements

• Python 3
• Flask, SQLAlchemy, python-dotenv
• PostgreSQL running.

#### Run the app

1) Install postgresql

2) In psql prompt create a database called `llb`:
```sql
CREATE DATABASE llb LC_COLLATE 'fi_FI.ISO8859-15' LC_CTYPE 'fi_FI.ISO8859-15' ENCODING LATIN9 TEMPLATE template0;
```

3) Create a file named `.env` (yeah, with a dot in the beginning) at the root of the `pts_feedback` directory (same level as `app.py`) and include the following line. Remember to put your username in place of `<insert_user_name>`.
```
LLB_POSTGRES_URL=postgresql+psycopg2://<insert_user_name>:somepasswd@localhost:5432/llb
```

4)  From the command line run `python app.py`

5) Check that the app works: navigate to `http://localhost:5000/`in a browser and you should see the text *App home*. Check these as well:

```
http://localhost:5000/surveys
http://localhost:5000/surveys/new
http://localhost:5000/surveys/1/questions
http://localhost:5000/surveys/1/questions/new
```



#### Manipulate database

When adding functionality to controller files, the database can be manipulated using the SQLAlchemy `session` object.

SQLAlchemy examples:

```python
# Create entries
s = Survey(1, 'Magnificent survey')
f = Feedback(1)
a = Answer(2, 'bla', 2)

# Add to db
session.add(s)
session.commit() # Persisted in db only after commit

# Get list of all surveys
session.query(Survey).all()

# Get first survey
first_survey = session.query(Survey).first()

# Get survey with greatest id_:
from sqlalchemy import desc
latest_survey = session.query(Survey).order_by(Survey.id_.desc()).first()

# Filter surveys by id
survey_1 = session.query(Survey).filter_by(id_=1).one()  # .one() ensures only one entry is returned

# Update survey_1
survey_1 = session.query(Survey).filter_by(id_=1).one()
survey_1.description = 'Even more magnificent survey'
session.add(survey_1) # This effectively updates
session.commit()

# Delete
survey_1 = session.query(Survey).filter_by(id_=1).one()
session.delete(survey_1)
session.commit()
```
