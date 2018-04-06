import os, inspect
from flask import render_template, url_for, request, redirect, flash, jsonify
from wtforms import Form, IntegerField, StringField, validators 

# Backtrack to parent dir to prevent import problems
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

from config.setup import Base, session, postgres_url
from models.question import Question

class QuestionForm(Form):
	type_ = StringField("Type", [validators.Length(min=1, max=20)])
	title = StringField("Title", [validators.Length(min=1, max=20)])

routes = []

# Function for naking a new question:
def new_question(survey_id):
    return render_template('new_question.html', form=QuestionForm(request.form), survey_id=survey_id)

routes.append(dict(
	rule='/surveys/<int:survey_id>/questions/new',
	view_func=new_question))

# Function for printing a single question:
def question(survey_id,question_id):
	return render_template('questions.html',survey_id=survey_id,
		questions=session.query(Question).order_by(Question.id_).\
		filter(Question.survey_id == survey_id, Question.id_ == question_id).\
		all())

routes.append(dict(
	rule='/surveys/<int:survey_id>/questions/<int:question_id>',
	view_func=question))

# Function for retrieving all the added questions of a survey:
def questions(survey_id):
	form = QuestionForm(request.form)
	if (request.method == 'GET'):
		return render_template('questions.html',survey_id=survey_id,
			questions=session.query(Question).order_by(Question.id_).filter(Question.survey_id == survey_id).all())

	if (request.method == 'POST') and (form.validate()):
		newQuestion = Question(form.type_.data,form.title.data, survey_id)
		session.add(newQuestion)
		session.commit()
		return redirect("/surveys/" + str(survey_id) + "/questions/" + str(newQuestion.id_))
	else:
		return str(form.errors)

routes.append(dict(
	rule='/surveys/<int:survey_id>/questions',
	view_func=questions,
	options=dict(methods=['GET', 'POST',])))

# Function for editing a single question:
def editQuestion(survey_id,question_id):
	form = QuestionForm(request.form)
	questionToBeEdited = session.query(Question).filter(Question.id_==question_id,Question.survey_id==survey_id).one()

	if request.method == 'GET':
		# pre-filling the form:
		form.type_.data = questionToBeEdited.type_
		form.title.data = questionToBeEdited.title

		return render_template('edit_question.html', form=form)
	elif (request.method == 'POST') and (form.validate()):
		# editing the question:
		questionToBeEdited.type_ = form.type_.data
		questionToBeEdited.title = form.title.data

		session.add(questionToBeEdited)
		session.commit()
		return redirect("/surveys/" + str(survey_id) + "/questions/" + str(question_id))
	else:
		return str(form.errors)
routes.append(dict(rule='/surveys/<int:survey_id>/questions/<int:question_id>/edit',
					view_func=editQuestion,
					options=dict(methods=['GET','POST'])))