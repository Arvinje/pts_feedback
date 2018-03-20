# Create a controller named Surveys under controllers folder. It has to include following features:
# - A GET /surveys/new route with respective view which shows a form for creating a survey to the user
# - A POST /surveys route which runs validations on the passed data. On valid data it should create a survey and render /surveys/{id}/questions view. On failure, it renders a new survey form pre-filled with the invalid data.
# - A GET /surveys to display all available surveys.
# - A GET /surveys/{id}/edit which renders a form for updating the attributes of the selected survey.
# - A PUT /surveys/{id} which handles the updating the attributes of the selected survey, similar to CREATE route.
# - No need for DELETE during this phase.

import os, inspect
from flask import render_template, url_for, request, redirect, flash, jsonify

# Backtrack to parent dir to prevent import problems
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

# Imports
from config.setup import Base, session, postgres_url  # Required by SQLAlchemy
from models.survey import Survey


routes = []

def new_survey():
    print('Enter process, method {}'.format(request.method))

    # Do stuff

    return 'Form for creating a survey'

routes.append(dict(
    rule='/surveys/new',
    view_func=new_survey))


def surveys():
  if request.method == 'GET':

    # Do stuff
    latest_survey = session.query(Survey).order_by(Survey.id_.desc()).first()
    print(latest_survey)

    return 'Displaying all available surveys'

  elif request.method == 'POST':

    # Do stuff, interact with db using session object

    return 'Validate: if valid, create and add survey to db & render view, else if invalid, render new survey form pre-filled with invalid data'

  else:
    return 'Not GET or POST'

routes.append(dict(
  rule='/surveys',
  view_func=surveys,
  options=dict(methods=['GET', 'POST',])))


