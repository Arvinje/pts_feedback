import os, inspect, time
from flask import Flask, render_template, request, redirect, flash
from config.setup import session # for SQL-connection
from wtforms import Form, StringField, DateField, validators 

from models.survey import Survey
from models.question import Question

from controllers.Functions import startDateIsBeforeToday
from controllers.Functions import checkThatFieldIsNotOnlyWhiteSpace

# Backtrack to parent dir to prevent import problems
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

# Form-class helps data processing
# with html-files and it has useful validation-methods:
class SurveyForm(Form):
    description = StringField('Description', [validators.Length(min=4, max=25), 
                                            checkThatFieldIsNotOnlyWhiteSpace])
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
      # the query returns list of all surveys and sends the list to the view:
      return render_template('surveys.html', surveys=session.query(Survey).order_by(Survey.id_).all())
    if (request.method == 'POST') and (form.validate()):
      if form.start_date.data < form.end_date.data:
        surveyToBeAdded = Survey(form.description.data,form.start_date.data, form.end_date.data)
        session.add(surveyToBeAdded) #adding record to database
        session.commit() #commiting addition

        return redirect("/surveys/" + str(surveyToBeAdded.id_) + "/questions")
      else:
        flash("Survey creation error: start_date is after end_date.")
        return render_template('new_survey.html', form=form)
    else:
      return render_template('new_survey.html', form=form)
routes.append(dict(rule='/surveys',view_func=surveys,
                   options=dict(methods=['GET','POST'])))

# Running this function edits Survey with id given as a parameter.
def editSurvey(id):
    form = SurveyForm(request.form)
    surveyToBeEdited = session.query(Survey).filter_by(id_=id).one()

    if request.method == 'GET':
      # the query returns the survey:

      form.description.data = surveyToBeEdited.description_
      form.start_date.data = surveyToBeEdited.start_date_
      form.end_date.data = surveyToBeEdited.end_date_

      return render_template('edit_survey.html', form=form)
    if (request.method == 'POST'):
      if (form.validate()):
        if form.start_date.data < form.end_date.data:
          surveyToBeEdited.description_ = form.description.data
          surveyToBeEdited.start_date_ = form.start_date.data
          surveyToBeEdited.end_date_ = form.end_date.data
          session.add(surveyToBeEdited) # this updates the database
          session.commit()
          return redirect('/surveys')
        else:
          flash("Survey creation error: start_date is after end_date.")
          return render_template('edit_survey.html', form=form)
      else:
        return render_template('edit_survey.html', form=form)

routes.append(dict(rule='/surveys/<int:id>/edit',view_func=editSurvey,
                   options=dict(methods=['GET','POST'])))

# Running this function deletes Survey with id given as a parameter.
def deleteSurvey(id):
    form = SurveyForm(request.form)
    surveyToBeDeleted = session.query(Survey).filter_by(id_=id).one()

    if request.method == 'GET':
      return render_template('delete_survey.html', id_=surveyToBeDeleted.id_, description=surveyToBeDeleted.description_)
    elif (request.method == 'POST'):
      if (startDateIsBeforeToday(surveyToBeDeleted.start_date_)):        
        # deleting all the questions of survey:
        for questionToBeDeleted in session.query(Question).filter_by(survey_id_=id).all():
          session.delete(questionToBeDeleted)

        session.delete(surveyToBeDeleted)
        session.commit()

        return redirect('/surveys')
      else:
        flash("Survey deletion error: start_date is not in the future.")
        return render_template('delete_survey.html', id_=surveyToBeDeleted.id_, description=surveyToBeDeleted.description_)
    else:
      return render_template('delete_survey.html', id_=surveyToBeDeleted.id_, description=surveyToBeDeleted.description_)
routes.append(dict(rule='/surveys/<int:id>/delete',view_func=deleteSurvey,
                   options=dict(methods=['GET','POST'])))

def startDateIsBeforeToday(date):
  dayToday = int(time.strftime('%d'))
  monthToday = int(time.strftime('%m'))
  yearToday = int(time.strftime('%Y'))

  if (yearToday < date.year):
    return True
  if ((yearToday == date.year) & (monthToday < date.month)):
    return True
  if ((monthToday == date.month) & (dayToday < date.day)):
    return True
  return False