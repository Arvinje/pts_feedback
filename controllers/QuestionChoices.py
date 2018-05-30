import os, inspect
from flask import render_template, request, redirect
from wtforms import Form, StringField, validators

# Backtrack to parent dir to prevent import problems
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

from config.setup import session
from models.questionChoice import QuestionChoice

from controllers.Functions import checkThatFieldIsNotOnlyWhiteSpace

class QuestionChoiceForm(Form):
	title_ = StringField("Title", [validators.Length(min=1, max=250),
								checkThatFieldIsNotOnlyWhiteSpace])

routes = []

# Function for naking a new questionChoice:
def new_questionchoice(survey_id,question_id):
    return render_template('new_questionchoice.html',
    	form=QuestionChoiceForm(request.form),
		survey_id=survey_id,
		question_id=question_id)

routes.append(dict(
	rule='/surveys/<int:survey_id>/questions/<int:question_id>/questionChoices/new',
	view_func=new_questionchoice))

# Function for printing a single questionChoice:
def questionChoice(survey_id,question_id,questionChoice_id):
	return render_template('questionChoice.html',survey_id=survey_id,\
		questionChoices=session.query(QuestionChoice).order_by(QuestionChoice.id_).\
		filter(QuestionChoice.survey_id_ == survey_id, QuestionChoice.question_id_ == question_id,\
				QuestionChoice.id_ == questionChoice_id).\
			one())

routes.append(dict(
	rule='/surveys/<int:survey_id>/questions/<int:question_id>/questionChoices/<int:questionChoice_id>',
	view_func=questionChoice))

# Function for retrieving all the added questionChoices of a question:
def questionChoices(survey_id,question_id):
	form = QuestionChoiceForm(request.form)
	if (request.method == 'GET'):
		return render_template('questionChoices.html',survey_id=survey_id,question_id=question_id,
			questionChoices=session.query(QuestionChoice).order_by(QuestionChoice.id_).filter\
							(QuestionChoice.question_id_ == question_id).all())

	if (request.method == 'POST') and (form.validate()):
		newQuestionChoice = QuestionChoice(form.title_.data, question_id)
		session.add(newQuestionChoice)
		session.commit()
		return redirect("/surveys/" + str(survey_id) + "/questions")
	else:
		return render_template('new_questionChoice.html', form=form,survey_id=survey_id,question_id=question_id)

routes.append(dict(
	rule='/surveys/<int:survey_id>/questions/<int:question_id>/questionChoices',
	view_func=questionChoices,
	options=dict(methods=['GET', 'POST',])))

# Function for editing a single questionChoice:
def editQuestionChoice(survey_id,question_id,questionChoice_id):
	form = QuestionChoiceForm(request.form)
	questionChoiceToBeEdited = session.query(QuestionChoice).filter(QuestionChoice.id_==questionChoice_id).one()

	if request.method == 'GET':
		# pre-filling the form:
		form.title_.data = questionChoiceToBeEdited.title_

		return render_template('edit_questionChoice.html', form=form)
	elif (request.method == 'POST') and (form.validate()):
		# editing the question:
		questionChoiceToBeEdited.title_ = form.title_.data

		session.add(questionChoiceToBeEdited)
		session.commit()
		return redirect("/surveys/" + str(survey_id) + "/questions")
	else:
		return render_template('edit_questionChoice.html', form=form)
routes.append(dict(rule='/surveys/<int:survey_id>/questions/<int:question_id>/questionChoices/<int:questionChoice_id>/edit',
					view_func=editQuestionChoice,
					options=dict(methods=['GET','POST'])))

# Function for removing a single questionChoice
def deleteQuestionChoice(survey_id,question_id,questionChoice_id):
	questionChoiceToBeDeleted = session.query(QuestionChoice).filter(QuestionChoice.id_==questionChoice_id,\
				QuestionChoice.question_id_==question_id).one()

	if request.method == 'GET':
		return render_template('delete_questionChoice.html', title=questionChoiceToBeDeleted.title_,\
			survey_id=survey_id,question_id=question_id)
	elif (request.method == 'POST'):
		session.delete(questionChoiceToBeDeleted)
		session.commit()
		return redirect("/surveys/" + str(survey_id) + "/questions")

routes.append(dict(rule='/surveys/<int:survey_id>/questions/<int:question_id>/questionChoices/<int:questionChoice_id>/delete',
					view_func=deleteQuestionChoice,
					options=dict(methods=['GET','POST'])))
