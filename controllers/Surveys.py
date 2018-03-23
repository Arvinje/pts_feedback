import os, inspect
from flask import render_template, url_for, request, redirect, flash, jsonify

# Backtrack to parent dir to prevent import problems
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

# Imports
from config.setup import Base, session, postgres_url  # Required by SQLAlchemy
from models.survey import Survey # importing the class
from wtforms import Form, IntegerField, StringField, DateTimeField # form uses these

routes = []

# surveyForm-wtforms-class is used to send and retrieve
# survey-class values to html-views. The fields have
# name (here for example: id_), type (IntegerField/etc) and
# caption that is shown in view ("ID", "Description" etc) 
class surveyForm(Form):
    id_ = IntegerField("ID")
    description = StringField("Description")
    start_date = DateTimeField("Start date (YYYY-MM-DD HH:MM:SS)")
    end_date = DateTimeField("End date (YYYY-MM-DD HH:MM:SS)")

# Function for retrieving all the added surveys:
def surveys():
    # the query returns list of all surveys and sends
    # the list to the view:
    return render_template('surveys.html', surveys=session.query(Survey).all())

routes.append(dict(
  rule='/surveys',
  view_func=surveys,))

# Running this function edits
# Survey with id given as a parameter.
def editSurvey(id):
    # first we find the record to be edited:
    surveyToBeEdited = session.query(Survey).filter_by(id_=id).one()
    
    # form fields are initialized
    # with values from the record to be edited:
    form = surveyForm(request.form, 
                      id_ = surveyToBeEdited.id_,
                      description = surveyToBeEdited.description,
                      start_date = surveyToBeEdited.start_date,
                      end_date = surveyToBeEdited.end_date)

    if request.method == 'POST' and form.validate():
      # POST-method. Survey field are updated with fields
      # retrieved from the html-form:
      surveyToBeEdited.id_ = request.form['id_']
      surveyToBeEdited.description = request.form['description']
      surveyToBeEdited.start_date = request.form['start_date']
      surveyToBeEdited.end_date = request.form['end_date']

      # edited survey is updated to database:
      session.add(surveyToBeEdited)
      session.commit()

      # after edit, we display route /surveys:
      return redirect('/surveys')

    # GET-method:
    return render_template('edit_survey.html', form=form)

routes.append(dict(
    rule='/surveys/<id>/edit',
    view_func=editSurvey,
    options=dict(methods=['GET','POST'])))

# Running this function makes
# table Survey to database. Returns
# error, if table exists already.
def createSurveysTable():
    session.execute('CREATE TABLE surveys(id_ INT,'
                    'description VARCHAR(100),'
                    'start_date DATE,'
                    'end_date DATE,'
                    'PRIMARY KEY (id_))')
    
    session.commit()

    return "surveys-table created"

routes.append(dict(
    rule='/surveys/create_surveys_table',
    view_func=createSurveysTable))

# Function for inserting
# new survey-records:
def new_survey():
    # form is used to send and retrieve values from views:
    form = surveyForm(request.form)

    if request.method == 'POST' and form.validate():
      # POST-method:
      surveyToBeAdded = Survey(request.form['id_'], request.form['description'],request.form['start_date'], request.form['end_date'])
      session.add(surveyToBeAdded) #adding record to database
      session.commit() #commiting addition
      return ("Added survey with id " + 
              str(surveyToBeAdded.id_) + " " + 
              surveyToBeAdded.description + ".")

    # GET-method:
    return render_template('new_survey.html', form=form)

routes.append(dict(
    rule='/surveys/new',
    view_func=new_survey,
    options=dict(methods=['GET','POST'])))