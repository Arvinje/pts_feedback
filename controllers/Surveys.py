import os, inspect
from flask import Flask, render_template, request, redirect, url_for
from config.setup import session # for SQL-connection
from models.survey import Survey # importing the class
from wtforms import Form, IntegerField, StringField, DateField, validators 

# Backtrack to parent dir to prevent import problems
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

# Form-class helps data processing
# with html-files and it has useful validation-methods:
class SurveyForm(Form):
    description = StringField('Description', [validators.Length(min=4, max=25)])
    start_date = DateField('Start date (YYYY-MM-DD)', [validators.DataRequired()])
    end_date = DateField('End date (YYYY-MM-DD)', [validators.DataRequired()])

#list that includes function routes:
routes = []

# Function for inserting new survey-records:
def newSurvey():
    return render_template('new_survey.html', form=SurveyForm(request.form))
routes.append(dict(rule='/surveys/new',view_func=newSurvey,
                   options=dict(methods=['GET'])))

# Function for retrieving all the added surveys:
def surveys():
    form = SurveyForm(request.form)
    if request.method == 'GET':
      # the query returns list of all surveys and sends
      # the list to the view:
      return render_template('surveys.html', surveys=session.query(Survey).all())
    if (request.method == 'POST') and (form.validate()):
      session.add(Survey(form.description.data,form.start_date.data, form.end_date.data)) #adding record to database
      session.commit() #commiting addition

      return redirect('/surveys')
    else:
      return str(form.errors)
routes.append(dict(rule='/surveys',view_func=surveys,
                   options=dict(methods=['GET','POST'])))

# Running this function edits
# Survey with id given as a parameter.
def editSurvey(id):
    form = SurveyForm(request.form)
    surveyToBeEdited = session.query(Survey).filter_by(id_=id).one()

    if request.method == 'GET':
      # the query returns the survey:

      form.description.data = surveyToBeEdited.description
      form.start_date.data = surveyToBeEdited.start_date
      form.end_date.data = surveyToBeEdited.end_date

      return render_template('edit_survey.html', form=form)
    elif (request.method == 'POST') and (form.validate()):
      surveyToBeEdited.description = form.description.data
      surveyToBeEdited.start_date = form.start_date.data
      surveyToBeEdited.end_date = form.end_date.data
      session.add(surveyToBeEdited) # this updates the database
      session.commit()

      return redirect('/surveys')
    else:
      return str(form.errors)
routes.append(dict(rule='/surveys/<int:id>/edit',view_func=editSurvey,
                   options=dict(methods=['GET','POST'])))

# Running this function deletes
# Survey with id given as a parameter.
def deleteSurvey(id):
    form = SurveyForm(request.form)
    surveyToBeDeleted = session.query(Survey).filter_by(id_=id).one()

    if request.method == 'GET':
      return render_template('delete_survey.html', id_=surveyToBeDeleted.id_, description=surveyToBeDeleted.description)
    elif (request.method == 'POST'):
      session.delete(surveyToBeDeleted) # this updates the database
      session.commit()

      return redirect('/surveys')
    else:
      return str(form.errors)
routes.append(dict(rule='/surveys/<int:id>/delete',view_func=deleteSurvey,
                   options=dict(methods=['GET','POST'])))