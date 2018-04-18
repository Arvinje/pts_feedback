import os, inspect, time
from flask import Flask, render_template
from config.setup import session # for SQL-connection

from models.survey import Survey
from models.question import Question

# Backtrack to parent dir to prevent import problems
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

routes = []

# Function for retrieving all the added surveys from the past and their results:
def surveyResultList():
  return render_template('survey_result_list.html', surveys=session.query(Survey).order_by(Survey.id_).\
    filter(Survey.start_date_ <= (time.strftime('%Y') + '-' + time.strftime('%m') + '-' + time.strftime('%d'))).all())
routes.append(dict(rule='/results/surveys',view_func=surveyResultList))

# Function for retrieving the results of a survey:
def surveyResults(survey_id):
  return render_template('survey_results.html', 
    survey = session.query(Survey).filter_by(id_=survey_id).one())
routes.append(dict(rule='/results/surveys/<int:survey_id>',view_func=surveyResults,
                   options=dict(methods=['GET'])))

# Function for retrieving the results of a survey:
def surveyQuestionResults(survey_id,question_id):
  return render_template('survey_question_results.html',
    question = session.query(Question).filter_by(survey_id_=survey_id,id_=question_id).one(),
    survey = session.query(Survey).filter_by(id_=survey_id).one())
routes.append(dict(rule='/results/surveys/<int:survey_id>/questions/<int:question_id>',view_func=surveyQuestionResults))