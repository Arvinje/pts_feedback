import os, inspect
from flask import render_template, request, redirect
from wtforms import Form, StringField, SelectField, BooleanField, validators

# Backtrack to parent dir to prevent import problems
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

from config.setup import session
from models.question import Question
from models.questionChoice import QuestionChoice

from controllers.Functions import checkThatFieldIsNotOnlyWhiteSpace

class QuestionForm(Form):
	type_ = SelectField("Type", choices=[("Text","Text"),("Stars","Stars"),\
										("Picture","Picture"),("Choices","Choices"),\
										("Smileys","Smileys"),("Thumbs","Thumbs")])
	title_ = StringField("Title", [validators.Length(min=1, max=250),
								checkThatFieldIsNotOnlyWhiteSpace])
	optional_ = BooleanField("Optional")

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
		filter(Question.survey_id_ == survey_id, Question.id_ == question_id).\
		all())

routes.append(dict(
	rule='/surveys/<int:survey_id>/questions/<int:question_id>',
	view_func=question))

# Function for retrieving all the added questions of a survey:
def questions(survey_id):
	form = QuestionForm(request.form)
	if (request.method == 'GET'):
		return render_template('questions.html',survey_id=survey_id,
			questions=session.query(Question).order_by(Question.id_).filter(Question.survey_id_ == survey_id).all())

	if (request.method == 'POST') and (form.validate()):
		newQuestion = Question(form.type_.data,form.title_.data, survey_id, form.optional_.data)

		session.add(newQuestion)
		session.commit()
		return redirect("/surveys/" + str(survey_id) + "/questions")
	else:
		return render_template('edit_question.html', form=form)

routes.append(dict(
	rule='/surveys/<int:survey_id>/questions',
	view_func=questions,
	options=dict(methods=['GET', 'POST',])))

# Function for editing a single question:
def editQuestion(survey_id,question_id):
	form = QuestionForm(request.form)
	questionToBeEdited = session.query(Question).filter(Question.id_==question_id,Question.survey_id_==survey_id).one()

	if request.method == 'GET':
		# pre-filling the form:
		form.type_.data = questionToBeEdited.type_
		form.title_.data = questionToBeEdited.title_
		form.optional_.data = questionToBeEdited.optional_

		return render_template('edit_question.html', form=form, survey_id=survey_id, question_id=question_id)
	elif (request.method == 'POST') and (form.validate()):
		# editing the question:
		questionToBeEdited.type_ = form.type_.data
		questionToBeEdited.title_ = form.title_.data
		questionToBeEdited.optional_ = form.optional_.data

		session.add(questionToBeEdited)
		session.commit()
		return redirect("/surveys/" + str(survey_id) + "/questions")
	else:
		return render_template('edit_question.html', form=form, survey_id=survey_id, question_id=question_id)
routes.append(dict(rule='/surveys/<int:survey_id>/questions/<int:question_id>/edit',
					view_func=editQuestion,
					options=dict(methods=['GET','POST'])))

# Function for removing a single question:
def deleteQuestion(survey_id,question_id):
	form = QuestionForm(request.form)
	questionToBeDeleted = session.query(Question).filter(Question.id_==question_id,Question.survey_id_==survey_id).one()

	if request.method == 'GET':
		return render_template('delete_question.html',
			type_ = questionToBeDeleted.type_,
			title_ = questionToBeDeleted.title_)
	elif (request.method == 'POST'):
		# deleting all the questionChoices of question:
		for questionChoiceToBeDeleted in session.query(QuestionChoice).filter_by(question_id_=question_id).all():
			session.delete(questionChoiceToBeDeleted)
		session.delete(questionToBeDeleted)
		session.commit()
		return redirect("/surveys/" + str(survey_id) + "/questions")
	else:
		return render_template('delete_question.html', form=form)

routes.append(dict(rule='/surveys/<int:survey_id>/questions/<int:question_id>/delete',
					view_func=deleteQuestion,
					options=dict(methods=['GET','POST'])))
