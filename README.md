# Feedback Gathering Tool for Public Transportation Services

This is a web app for feedback gathering on [Living Lab Bus](http://livinglabbus.fi) platform. Currently, it's being developed by a group of students at University of Tampere, Finland.


#### Requirements

• Python 3
• Flask, SQLAlchemy
• PostgreSQL running.

#### Running the app

1) Install postgresql

2) In psql prompt create a database called `llb`:
```sql
CREATE DATABASE llb LC_COLLATE 'fi_FI.ISO8859-15' LC_CTYPE 'fi_FI.ISO8859-15' ENCODING LATIN9 TEMPLATE template0;
```

3) Figure out the value for `POSTGRES_URL` in your case. If you created a db called `llb`as in the above example, and your username is `insi`, and port number `5432`, the url is 
```
postgresql+psycopg2://insi:somepasswd@localhost:5432/llb
```

and you can insert anything in place of `somepasswd`. You can check the port number and username from Postgres.app (where the database `llb` should now exist), from under `Server settings...`.

4) From the command line, create an environment variable that holds the value of the `POSTGRES_URL` variable:
```bash
export LLB_POSTGRES_URL="postgresql+psycopg2://<insert_user_name>:somepasswd@localhost:5432/llb"
```

5)  From the command line run `python app.py`

#### Check that it works

Navigate to `http://localhost:5000/`in a browser and you should see the text 'App home'. Do the same for these:

```
http://localhost:5000/surveys/
http://localhost:5000/surveys/new
http://localhost:5000//surveys/<int:survey_id>/questions
http://localhost:5000//surveys/<int:survey_id>/questions/new
```





#### Add functionalities

When adding functionality to controller files, the database can be manipulated using the SQLAlchemy `session` object.

