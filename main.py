from flask import render_template, request

import models.survey
import controllers.surveys

from app import app, db

@app.route('/', methods=['GET', 'POST'])
def index():
	# at first run the next line to create table. Database also has to be created.
	# db.execute("CREATE TABLE survey (id int PRIMARY KEY, description text)")
    return render_template('index.html', form=request.form)