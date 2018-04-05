# Create a controller named Questions under controllers folder. It has to include following features:
# - A GET /surveys/{survey_id}/questions/new route with respective view which shows a form for creating a question for that specific survey
# - A POST /surveys/{survey_id}/questions route which runs validations on the passed data. On valid data it should create a question associated with the specified survey and render /surveys/{survey_id}/questions/{id} view. On failure, it renders a new question form pre-filled with the invalid data.
# - A GET /surveys/{survey_id}/questions to display all available questions for that specific survey.
# - A GET /surveys/{survey_id}/questions/{id}/edit which renders a form for updating the attributes of the selected question.
# - A PUT /surveys/{survey_id}/questions/{id}/edit which handles the updating the attributes of the selected question, similar to CREATE route.
# - No need for DELETE during this phase.

import os, inspect
from flask import render_template, url_for, request, redirect, flash, jsonify

# Backtrack to parent dir to prevent import problems
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

# Imports
from config.setup import Base, session, postgres_url  # Required by SQLAlchemy
from models.question import Question


routes = []

def new_question(survey_id):
	print('Enter process, method {}'.format(request.method))

	# Do stuff

	return 'Form for creating a new question'

routes.append(dict(
	rule='/surveys/<int:survey_id>/questions/new',
	view_func=new_question))


def questions(survey_id):
	print('Enter process, method {}'.format(request.method))
	if request.method == 'GET':

		# Do stuff

		return 'Displaying all available questions for survey {}'.format(survey_id)

	elif request.method == 'POST':

	    # Do stuff, interact with db using session object

		return 'Validate: if valid, create and add question associated with survey {} to db & render view, else if invalid, render new question form pre-filled with invalid data'.format(survey_id)

	else:
		return 'Not GET or POST'


routes.append(dict(
	rule='/surveys/<int:survey_id>/questions',
	view_func=questions,
	options=dict(methods=['GET', 'POST',])))
