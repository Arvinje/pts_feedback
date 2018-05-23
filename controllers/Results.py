import os, inspect, time
import csv
import io
from flask import Flask, render_template, make_response, send_file
from config.setup import session # for SQL-connection

from models.answer import Answer
from models.survey import Survey
from models.question import Question
from models.feedback import Feedback
from flask import Response
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

def exportSurveyResultsToCSVFile(survey_id):
    si = io.StringIO()
    outputWriter = csv.writer(si)

    #printing question titles as a header:
    questions=session.query(Question).order_by(Question.id_).filter(Question.survey_id_ == survey_id).all()
    questionIDs = ["feedback_id"]
    for question in questions:
        questionIDs.append(question.title_)
    outputWriter.writerow(questionIDs)
    outputWriter.writerow("")

    #searching for all the feedback of survey:
    feedbacks=session.query(Feedback).filter(Feedback.survey_id_ == survey_id).all()
    for feedback in feedbacks:
        answers = [str(feedback.id_)]
        #searching an answer for each question:
        for question in questions:
            answer=session.query(Answer).filter(Answer.feedback_id_ == feedback.id_,Answer.question_id_ == question.id_).first()

            # if no answer is given, empty value is printed
            if answer == None:
                answers.append("empty")
            else:
                answers.append(answer.value_)

        outputWriter.writerow(answers)

    #exporting file:
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=feedback_export.csv"
    output.headers["Content-type"] = "text/csv"

    return output

routes.append(dict(rule='/results/surveys/<int:survey_id>/export',view_func=exportSurveyResultsToCSVFile,
                   options=dict(methods=['GET'])))

# Function for retrieving the results of a survey:
def exportSurveyQuestionResultsToCSVFile(survey_id,question_id):
    si = io.StringIO()
    outputWriter = csv.writer(si)

    #printing question title as a header:
    question=session.query(Question).filter(Question.id_ == question_id).one()
    outputWriter.writerow(["Feedback ID",question.title_])
    outputWriter.writerow("")

    #searching for all the feedback of survey:
    feedbacks=session.query(Feedback).order_by(Feedback.id_).filter(Feedback.survey_id_ == survey_id).all()
    for feedback in feedbacks:
        #searching an answer for each question:
        answer=session.query(Answer).filter(Answer.feedback_id_ == feedback.id_,Answer.question_id_ == question_id).first()

        # if no answer is given, empty value is printed
        if answer == None:
            outputWriter.writerow([feedback.id_,"empty"])
        else:
            outputWriter.writerow([feedback.id_,answer.value_])

    #exporting file:
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=feedback_export.csv"
    output.headers["Content-type"] = "text/csv"

    return output

routes.append(dict(rule='/results/surveys/<int:survey_id>/questions/<int:question_id>/export',view_func=exportSurveyQuestionResultsToCSVFile))
