import os, inspect, datetime

from flask import Flask, render_template, request, redirect, flash, make_response, url_for
from flask import session as flasksession
from sqlalchemy import desc
from wtforms import Form, StringField, DateField, validators

from models.feedback import Feedback
from models.survey import Survey
from models.question import Question
from models.answer import Answer
from models.questionChoice import QuestionChoice

from config.setup import session
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
	start_date_ = DateField('Start date (YYYY-MM-DD)', [validators.DataRequired()])
	end_date_ = DateField('End date (YYYY-MM-DD)', [validators.DataRequired()])


class AnswerForm(Form):
	description = StringField('Description', [validators.Length(min=4, max=25),
											checkThatFieldIsNotOnlyWhiteSpace])
	value_ = StringField('Answer', [validators.DataRequired()])

routes = []


def newFeedback():
	# creates a feedback record
	# stores the id to that record in a cookie
	# has respective view that shows the latest active survey

	print('\n--- ENTERING newFeedback, method: {}'.format(request.method))

	# From active surveys, get one with greatest id
	survey = session.query(Survey).filter(Survey.end_date_ >= datetime.datetime.now()).order_by(Survey.id_.desc()).first()
	survey_title = survey.description_
	survey_id = survey.id_
	print('--- survey_title: {}'.format(survey_title))

	feedback_id = request.cookies.get('feedback_id')
	print('--- COOKIE / SESSION ID: {}'.format(feedback_id))
	if feedback_id == None:
		# Create feedback record
		fb = Feedback()
		session.add(fb)
		session.commit()
		feedback_id = session.query(Feedback).order_by(Feedback.id_.desc()).first().id_
		print('--- COOKIE / SESSION ID SET TO: {}'.format(feedback_id))

	# Build url for page with first survey question
	q1_url = url_for('controllers.showQuestion', question_id=1, survey_id=survey_id)

	# response = make_response(render_template('feedback.html', form=AnswerForm(request.form), survey_title=survey_title, feedback_id=feedback_id, q1_url=q1_url))
	response = make_response(render_template('feedback.html', survey_title=survey_title, feedback_id=feedback_id, q1_url=q1_url))
	response.set_cookie('feedback_id', str(feedback_id))
	print('---PRINTING RESPONSE AFTER SETTING COOKIE: {}'.format(response))

	return response

routes.append(dict(rule='/feedback', view_func=newFeedback, options=dict(methods=['GET'])))


#---------------------------------------------------------------------------------------------------


def showQuestion(question_id):
	# Shows the respective question related to the current survey (latest active one).
	#   If there already is a feedback id stored in cookie, the controller's action would retrieve it and
	#   fills the form/question if there was already an answer to that question.
	#   *tip: query EXIST if an answer record exists with question_id and feedback_id*
	#   NOTE: The page should have links to next and previous question.
	#   NOTE: It renders a different view based on the question type.

	print('\n--- ENTERING showQuestion with question_id: {}, method: {}'.format(question_id, request.method))

	# Find out feedback id either from cookie or by creating a new one
	missing_cookie = False

	if request.cookies['feedback_id'] == None:
		print('--- NO COOKIE FOUND. CREATING NEW FEEDBACK RECORD...')
		fb = Feedback()
		session.add(fb)
		session.commit()
		feedback_id = session.query(Feedback).order_by(Feedback.id_.desc()).first().id_
		missing_cookie = True
	else:
		feedback_id = request.cookies['feedback_id']

	print('--- COOKIE / SESSION ID:')
	print(request.cookies['feedback_id'])

	pre_existing_answers = session.query(Answer).filter_by(question_id_=question_id, feedback_id_=feedback_id).first()
	if pre_existing_answers != None and pre_existing_answers.count() > 0:
		answer = pre_existing_answers[0]
	else:
		answer = None
	print('---PRE-EXISTING ANSWER: {}'.format(answer))



	if missing_cookie:
		response.set_cookie('feedback_id', str(feedback_id))

	return str(question_id)

routes.append(dict(rule='/feedback/questions/<int:question_id>', view_func=showQuestion, options=dict(methods=['GET'])))


#---------------------------------------------------------------------------------------------------


def answerQuestion():
	# POST
	# Create an answer for the question.
	# The query indicates if the user wants to retrieve the previous or next question.
	# If the user taps next on the last question, it'll redirect to next route.
	# If there's an error (validations), it'll retrieve the current question.
	pass

routes.append(dict(rule='/feedback/questions/<int:question_id>/?q=<direction>', view_func=answerQuestion, options=dict(methods=['POST'])))


#---------------------------------------------------------------------------------------------------


def thankYou():
	# Shows an award and thank you message ONLY IF the survey is completed.
	# This should be checked when this action gets called.
	# The cookie should also be deleted.
	pass

routes.append(dict(rule='/feedback/thankyou', view_func=thankYou, options=dict(methods=['GET'])))


