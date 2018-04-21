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


# Arvin [6:23 PM]
# I just noticed a bug in the plan. We’re gonna need to create one-to-many relationship between survey
# and feedback.

# Recap: So let’s say we want to render the first page (welcome page):
# 1. controller checks the cookie:
# 1.1 if there’s already one and then it just renders the welcome page.
# 1.2 if the cookie was not there or it was not valid, it creates new feedback record and a new cookie
# that stores feedback_id.
# How to know it’s a valid cookie? if the feedback record (which we can get via the feedback_id in the cookie)
# belongs to the current active survey, then it’s valid.

# 2.controller passes a variable to the view that contains the link to the first question (ordered by id).
# 3. The view creates a link with href value equal to that variable.

# Now what about the question rendering? The controller passes two variable containing urls for next and previous question to the view. if the controller wants to render first question, there is no ‘previous’ link.

routes = []

# Form-class helps data processing
# with html-files and it has useful validation-methods:
# class SurveyForm(Form):
# 	description = StringField('Description', [validators.Length(min=4, max=25),
# 											checkThatFieldIsNotOnlyWhiteSpace])
# 	start_date_ = DateField('Start date (YYYY-MM-DD)', [validators.DataRequired()])
# 	end_date_ = DateField('End date (YYYY-MM-DD)', [validators.DataRequired()])

class AnswerFormFree(Form):
	description = StringField('Description', [validators.Length(min=0, max=1000),
											checkThatFieldIsNotOnlyWhiteSpace])
	value_ = StringField('Answer', [validators.DataRequired()])

class AnswerFormThumb(Form):
	description = StringField('Description', [validators.Length(min=4, max=1000),
											checkThatFieldIsNotOnlyWhiteSpace])
	value_ = StringField('Answer', [validators.DataRequired()])

class AnswerFormStar(Form):
	description = StringField('Description', [validators.Length(min=4, max=1000),
											checkThatFieldIsNotOnlyWhiteSpace])
	value_ = StringField('Answer', [validators.DataRequired()])

class AnswerFormSmiley(Form):
	description = StringField('Description', [validators.Length(min=4, max=1000),
											checkThatFieldIsNotOnlyWhiteSpace])
	value_ = StringField('Answer', [validators.DataRequired()])


#---------------------------------------------------------------------------------------------------
# NEW FEEDBACK
#---------------------------------------------------------------------------------------------------

def newFeedback():
	# creates a feedback record
	# stores the id to that record in a cookie
	# has respective view that shows the latest active survey

	print('\n--- ENTERING newFeedback, method: {}'.format(request.method))

	# From active surveys, get one with greatest id
	survey = session.query(Survey).filter(Survey.end_date_ >= datetime.datetime.now()).order_by(Survey.id_.desc()).first()
	if survey != None:
		print('--- survey id {}, title: {}'.format(survey.id_, survey.description_))
	else:
		return 'No active surveys.'

	# Check if valid cookie exists
	feedback = None
	try:
		feedback_id = request.cookies['feedback_id']
		if feedback_id != None:
			feedback = session.query(Feedback).filter_by(survey_id_=survey.id_).one()
			if feedback.id_ == feedback_id:
				print('---FOUND VALID COOKIE FOR THIS SURVEY: FEEDBACK {}'.format(feedback_id))
	except:
		pass

	# If no valid cookie exists, create new feedback and cookie from its id
	if feedback == None:
		print('--- NO COOKIE FOUND. CREATING NEW FEEDBACK RECORD FOR THIS SURVEY...')
		fb = Feedback(survey_id_=survey.id_)
		print('---CREATED FEEDBACK ENTRY {}'.format(fb.serialize))
		session.add(fb)
		session.commit()
		feedback = session.query(Feedback).order_by(Feedback.id_.desc()).first()
		feedback.survey_id_= survey.id_
		session.add(feedback)
		session.commit()
		feedback_id = feedback.id_
		print('---QUERIED DB, ADDED FEEDBACK {}'.format(feedback.serialize))
		print('--- COOKIE / SESSION ID WILL BE SET TO: {}'.format(feedback_id))

	# Build url for page with first survey question
	questions = session.query(Question).filter_by(survey_id_=survey.id_).order_by(Question.id_).all()
	print('---QUESTIONS FOR SURVEY {}: {}'.format(survey.id_, questions))

	q, response = None, None
	print('Q: {}'.format(q))
	try:
		q = questions[0]
	except:
		return 'Survey has no questions. Thank you & goodbye.\n[digital flower]\nGo away.'
		pass
	print('Q: {}'.format(q))

	if q != None:
		response = make_response(render_template('feedback.html',
													survey=survey,
													question_id=q.id_,
													question_title=q.title_,
													feedback=feedback))
		response.set_cookie('feedback_id', str(feedback_id))
		print('---PRINTING RESPONSE AFTER SETTING COOKIE: {}'.format(response))

	return response

routes.append(dict(rule='/feedback', view_func=newFeedback, options=dict(methods=['GET'])))


#---------------------------------------------------------------------------------------------------
# SHOW QUESTION
#---------------------------------------------------------------------------------------------------

def showQuestion(question_id, methods=['GET', 'POST']):
	# Shows the respective question related to the current survey (latest active one).
	#   If there already is a feedback id stored in cookie, the controller's action would retrieve it and
	#   fills the form/question if there was already an answer to that question.
	#   *tip: query EXIST if an answer record exists with question_id and feedback_id*
	#   NOTE: The page should have links to next and previous question.
	#   NOTE: It renders a different view based on the question type.

	print('\n--- COOKIE / SESSION ID:')
	print(request.cookies['feedback_id'])
	fb = session.query(Feedback).filter_by(id_=int(request.cookies['feedback_id'])).one()
	print('---FEEDBACK: {}'.format(fb.serialize))

	# SHOW QUESTION
	if request.method == 'GET':
		print('\n---ENTERING WITH GET')
		print(request.form)


		print('\n--- ENTERING showQuestion with question_id: {}, method: {}'.format(question_id, request.method))

		templates = {'Freeform': 'show_question_freeform.html',
					'Thumbs': 'show_question_thumbs.html',
					'Stars': 'show_question_stars.html',
					'Smileys': 'show_question_smileys.html',
					'Thankyou': 'thankyou.html'}
		forms = {'Freeform': AnswerFormFree(request.form),
				'Thumbs': AnswerFormThumb(request.form),
				'Stars': AnswerFormStar(request.form),
				'Smileys': AnswerFormSmiley(request.form)}

		q = session.query(Question).filter_by(id_= question_id).one()
		q_list = session.query(Question).filter_by(survey_id_=q.survey_id_).all()
		q_list_ids = [question.id_ for question in q_list]
		print('---LIST OF QUESTION IDS: {}'.format(q_list_ids))

		prev_q_ix = q_list_ids.index(q.id_) - 1
		next_q_ix = q_list_ids.index(q.id_) + 1 if q_list_ids.index(q.id_) + 1 < len(q_list) else None

		prev_url = url_for('controllers.showQuestion', question_id=q_list_ids[prev_q_ix]) if prev_q_ix >= 0 else None
		next_url = url_for('controllers.thankYou') if next_q_ix == None else url_for('controllers.showQuestion', question_id=q_list_ids[next_q_ix])
		is_first = prev_url == None
		not_first = prev_url != None
		print('is first {}, not first {}'.format(is_first, not_first))

		answerform = forms.get(q.type_, AnswerFormFree(request.form))
		try:
			pre_existing_answers = session.query(Answer).filter_by(question_id_=q.id_, feedback_id_=request.cookies['feedback_id']).one()
		except:
			pre_existing_answers = None

		if pre_existing_answers != None:
			answerform.description = pre_existing_answers.value_
			print('---PRE-EXISTING ANSWER FOUND WITH VALUE {}'.format(answerform.description))
		else:
			print('---NO PRE-EXISTING ANSWER FOUND.')


		print('---QUESTION: {}, {}'.format(type(q), q))

		template = templates.get(q.type_, 'Freeform')  # Freeform is default fallback
		question_id = int(q.id_)
		question_title = q.title_

		print('---TEMPLATE: {}, {}'.format(type(template), template))
		print('---ANSWERFORM: {}, {}'.format(type(answerform), answerform))
		print('---IS_FIRST: {}, {}'.format(type(is_first), is_first))
		print('---NOT_FIRST: {}, {}'.format(type(not_first), not_first))
		print('---QUESTION_ID: {}, {}'.format(type(question_id), question_id))
		print('---QUESTION_TITLE: {}, {}'.format(type(question_title), question_title))
		print('---NEXT_URL: {}, {}'.format(type(next_url), next_url))
		print('---PREV_URL: {}, {}'.format(type(prev_url), prev_url))

		# question_type = q.type_
		# template = templates[question_type]
		# print('---TEMPLATE: {}'.format(template))

		response = render_template(template, form=answerform, is_first=is_first, not_first=not_first, question_id=question_id, question_title=question_title, prev_url=prev_url, next_url=next_url)
		# response = render_template('bla.html', form=answerform, is_first=is_first, not_first=not_first, question_id=question_id, question_title=question_title, prev_url=prev_url, next_url=next_url)
		# response = render_template(template, form=answerform)
		# response = render_template('bla.html', form=answerform, is_first=True, not_first=False)
		print('okkkkk')
		print(response)
		return response

	#----------------
	# POST QUESTION:
	#----------------
	elif request.method == 'POST':
		print('\n---ENTERING WITH POST')
		print(request.form)

		# Create answer and commit to db
		answer = Answer(request.form['description'], int(request.cookies['feedback_id']), int(request.form['question_id']))
		print(answer.serialize)

		session.add(answer)
		session.commit()

		# Redirect to next if 'Next' was clicked
		if 'Next' in request.form.keys():
			return redirect(request.form['next_url'])

		# Redirect to prev if 'Prev' was clicked
		if 'Prev' in request.form.keys():
			return redirect(request.form['prev_url'])

		return 'Returning'


routes.append(dict(rule='/feedback/questions/<int:question_id>', view_func=showQuestion, options=dict(methods=['GET', 'POST'])))


#---------------------------------------------------------------------------------------------------


def thankYou():
	# Shows an award and thank you message ONLY IF the survey is completed.
	# This should be checked when this action gets called.
	# The cookie should also be deleted.
	print(request.form)

	gifts = {0: 'gift_1.png', 1: 'gift_2.png', 2: 'gift_3.png'}
	gift_ix = int(request.cookies['feedback_id']) % len(gifts)
	# gift_file = url_for('static', filename='imgs/{}'.format(gifts[gift_ix]))
	gift_file = '/static/imgs/{}'.format(gifts[gift_ix])
	print('---GIFT FILE: {}'.format(gift_file))

	# gift_file = '/static/imgs/gift_1.png'
	# gift_file = '/static/imgs/{}'.format(gifts[gift_ix])
	# gift_file = 'gift_3.png'
	# gift_file = url_for('static', filename='imgs/llb_logo.png')

	response = render_template('thankyou.html', gift_file=gift_file)
	return response

routes.append(dict(rule='/feedback/thankyou', view_func=thankYou, options=dict(methods=['GET'])))


