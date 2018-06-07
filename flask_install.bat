python -m venv venv
pip install virtualenv
pip install flask
pip install wtforms
pip install sqlalchemy
pip install psycopg2
pip install flask_bootstrap
set LLB_POSTGRES_URL=postgresql+psycopg2://postgres:Pulla123@localhost:5432/llb
set FLASK_APP=app.py
virtualenv venv
venv\scripts\activate
