import os, inspect
from flask import Flask, render_template, request, redirect, url_for
from config.setup import session # for SQL-connection
from models.survey import Survey # importing the class

# Backtrack to parent dir to prevent import problems
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

routes = []

# Function for inserting new survey-records:
def newSurvey():
    return render_template('new_survey.html')

routes.append(dict(rule='/surveys/new',view_func=newSurvey,
                   options=dict(methods=['GET'])))

# Function for retrieving all the added surveys:
def surveys():
    if request.method == 'GET':
      # the query returns list of all surveys and sends
      # the list to the view:
      return render_template('surveys.html', surveys=session.query(Survey).all())
    elif request.method == 'POST':
      surveyToBeAdded = Survey(request.form['id_'], request.form['description'],
                               request.form['start_date'], request.form['end_date'])
      session.add(surveyToBeAdded) #adding record to database
      session.commit() #commiting addition

      return redirect('/surveys')

routes.append(dict(rule='/surveys',view_func=surveys,
                   options=dict(methods=['GET','POST'])))

# Running this function edits
# Survey with id given as a parameter.
def editSurvey(id):
    if request.method == 'GET':
      # the query returns the survey and sends it to the view:
      return render_template('edit_survey.html', survey=session.query(Survey).filter_by(id_=id).one())
    elif request.method == 'POST':
      surveyToBeEdited = session.query(Survey).filter_by(id_=id).one()
      surveyToBeEdited.id_ = request.form['id_']
      surveyToBeEdited.description = request.form['description']
      surveyToBeEdited.start_date = request.form['start_date']
      surveyToBeEdited.end_date = request.form['end_date']
      session.add(surveyToBeEdited) # this updates the database
      session.commit()

      return redirect('/surveys')

routes.append(dict(rule='/surveys/<int:id>/edit',view_func=editSurvey,
                   options=dict(methods=['GET','POST'])))