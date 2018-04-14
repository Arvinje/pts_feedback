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


routes = []


#---------------------------------------------------------------------------------------------------


def newFeedback():
  # with respective view
  # shows the latest active survey
  # creates a feedback record
  # stores the id to that record in a cookie
  pass

routes.append(dict(rule='/feedback', view_func=newFeedback, options=dict(methods['GET'])))


#---------------------------------------------------------------------------------------------------


def showQuestion():
  # Shows the respective question related to the current survey (latest active one).
  #   If there already is a feedback id stored in cookie, the controller's action would retrieve it and
  #   fills the form/question if there was already an answer to that question.
  #   *tip: query EXIST if an answer record exists with question_id and feedback_id*
  #   NOTE: The page should have links to next and previous question.
  #   NOTE: It renders a different view based on the question type.
  # A `POST /feedback/questions/{question_id}/?q={next|back}` to create an answer for the question.
  #   The query indicates if the user wants to retrieve the previous or next question.
  #   If the user taps next on the last question, it'll redirect to next route.
  #   If there's an error (validations), it'll retrieve the current question.
  pass

routes.append(dict(rule='/feedback/questions/<int:question_id>', view_func=showQuestion, options=dict(methods['GET'])))


#---------------------------------------------------------------------------------------------------


def answerQuestion():
  # Create an answer for the question.
  # The query indicates if the user wants to retrieve the previous or next question.
  # If the user taps next on the last question, it'll redirect to next route.
  # If there's an error (validations), it'll retrieve the current question.
  pass

routes.append(dict(rule='/feedback/questions/<int:question_id>/?q=<direction>', view_func=answerQuestion, options=dict(methods['POST'])))


#---------------------------------------------------------------------------------------------------


def thankYou():
  # Shows an award and thank you message ONLY IF the survey is completed.
  # This should be checked when this action gets called.
  # The cookie should also be deleted.
  pass

routes.append(dict(rule='/feedback/thankyou', view_func=thankYou, options=dict(methods['GET'])))


