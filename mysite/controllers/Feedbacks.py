import os, inspect, datetime

from flask import Flask, render_template, request, redirect, flash, make_response, url_for
from flask import session as flasksession
from sqlalchemy import desc, distinct
from wtforms import Form, StringField, SelectField, DateField, RadioField, TextAreaField, validators

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

routes = []

templates = {'Freeform': 'freeform.html',
            'Text': 'freeform.html',
            'Thumbs': 'thumbs.html',
            'Stars': 'stars.html',
            'Smileys': 'smileys.html',
            'Thankyou': 'survey_lastpage.html',
            'Choices': 'choices.html',
            'Picture': 'picture.html'}

class AnswerFormFree(Form):
    value_ = TextAreaField('', [validators.DataRequired()])

class AnswerFormThumbs(Form):
    value_ = RadioField('', choices=[('thumbsup','(this is up)'),('thumbdown','(this is down)')])

class AnswerFormStars(Form):
    value_ = RadioField('', choices=[(1,'(one star)'),(2,'(two stars)'),(3,'(three stars)'),(4,'(four stars)'),(5,'(five stars)')])

class AnswerFormSmileys(Form):
    value_ = RadioField('', choices=[('sad','(sad)'),('neutral','(neutral'), ('happy', '(happy)')])

class AnswerFormChoices(Form):
    value_ = SelectField('', choices=[])

    def setChoices(self,listOfChoices):
        self.value_.choices.clear()
        [self.value_.choices.append((i,choice.title_)) for i, choice in enumerate(listOfChoices)]
        # i = 0
        # for choice in listOfChoices:
        #     self.value_.choices.append((i,choice.title_))
        #     i += 1

def parse_answer_from_request_form(requestform, existing_ans=None, verbose=False):
    qtype = requestform['question_type']
    parsed_answer = ''

    if 'value_' in requestform.keys():
        parsed_answer = requestform['value_']

    return parsed_answer

def db_answer_to_response(pre_existing_answer, qtype, form, verbose=False):
    form.value_.data = pre_existing_answer.value_
    return form

def get_progress(feedback, verbose=False):
    survey_id = feedback.survey_id_
    questions = session.query(Question).filter_by(survey_id_=survey_id).all()
    answers = session.query(Answer).filter_by(feedback_id_=feedback.id_).all()
    question_ids = set([item.id_ for item in questions])
    optional_question_ids = set([item.id_ for item in questions if bool(item.optional_) == True])
    answered_ids = set([item.question_id_ for item in answers])

    # Proportion of valid answer ids vs questions
    progress = int(len(answered_ids) / float(len(question_ids)) * 100) if len(question_ids) > 0 else 0.0

    # Ids of missing mandatory questions
    missing = list(question_ids.difference(answered_ids))

    return progress, missing

#---------------------------------------------------------------------------------------------------
# ROUTE: NEW FEEDBACK
#---------------------------------------------------------------------------------------------------

# /feedback
def newFeedback():
    # Creates a feedback record
    # Stores the id to that record in a cookie
    # Has respective view that shows the latest active survey

    # Form dict
    qtype_forms = {'Freeform': AnswerFormFree(request.form),
                    'Thumbs': AnswerFormThumbs(request.form),
                    'Stars': AnswerFormStars(request.form),
                    'Smileys': AnswerFormSmileys(request.form),
                    'Choices': AnswerFormChoices(request.form),
                    'Picture': AnswerFormFree(request.form)}

    # From active surveys, get one with greatest id
    survey = session.query(Survey).filter(Survey.end_date_ >= datetime.datetime.now(),Survey.enabled_).order_by(Survey.id_.desc()).first()
    if survey == None:
        return 'No active surveys.'

    # Check if valid cookie exists
    feedback = None
    try:
        cookie = request.cookies['feedback_id']
        if cookie != None:
            # Fetch feedback with id_ == cookie from db
            feedback = session.query(Feedback).filter_by(id_=cookie).one()
    except:
        pass

    # If no valid cookie exists, create new feedback and new cookie with feedback id_ as value
    if feedback == None or cookie==None or len(cookie) == 0:
        feedback = Feedback(survey_id_=survey.id_)
        session.add(feedback)
        session.commit()  # For some reason, feedback.survey_id_ is not yet entered into db. (((WHY)))

        # Workaround to store feedback.survey_id_ into db: query, change, commit
        feedback = session.query(Feedback).order_by(Feedback.id_.desc()).first()
        feedback.survey_id_= survey.id_
        session.add(feedback)
        session.commit()

        # Check that feedback.survey_id_ is now stored in db
        feedback = session.query(Feedback).order_by(Feedback.id_.desc()).first()

    # Get list of survey questions
    q_list = session.query(Question).filter_by(survey_id_=survey.id_).order_by(Question.id_).all()

    # Get first question
    q, response = None, None
    try:
        q = q_list[0]
    except:
        return 'Survey has no questions. Thank you & goodbye.'

    # Show first survey question:
    if q != None:
        template = templates.get(q.type_, 'freeform.html')  # Defaults to show_question_freeform for now
        form = qtype_forms.get(q.type_, AnswerFormFree(request.form))  # Defaults to AnswerFormFree for now
        prev_url = None
        next_url = url_for('controllers.thankYou') if len(q_list) <= 1 else url_for('controllers.showQuestion', question_id=q_list[1].id_)

        progress = 0

        response = make_response(render_template('survey_frontpage.html',
                                                    survey=survey,
                                                    question_id=q.id_,
                                                    feedback=feedback,
                                                    progress=progress
                                                    ))
        # Set cookie to value of feedback.id_
        response.set_cookie('feedback_id', str(feedback.id_))

    return response

routes.append(dict(rule='/feedback', view_func=newFeedback, options=dict(methods=['GET'])))


#---------------------------------------------------------------------------------------------------
# ROUTE: SHOW QUESTION
#---------------------------------------------------------------------------------------------------

# /feedback/questions/<int:question_id>
def showQuestion(question_id, methods=['GET', 'POST']):
    # Shows the respective question related to the current survey (latest active one).
    # If there already is a feedback id stored in cookie, the controller's action retrieves it and
    #   fills the form/question if there was already an answer to that question.
    # The page has links to next and previous question.
    # Renders a different view based on the question type.

    # Get feedback object
    cookie = request.cookies['feedback_id']
    feedback = session.query(Feedback).filter_by(id_=int(cookie)).one()

    # Form dict - can this be factored out of each function?
    qtype_forms = {'Freeform': AnswerFormFree(request.form), # can this be removed?
                    'Text': AnswerFormFree(request.form),
                    'Thumbs': AnswerFormThumbs(request.form),
                    'Stars': AnswerFormStars(request.form),
                    'Smileys': AnswerFormSmileys(request.form),
                    'Choices': AnswerFormChoices(request.form),
                    'Picture': AnswerFormFree(request.form)}

    progress = 0

    # GET: Show question with prefilled answer
    if request.method == 'GET':
        # Get list of survey questions
        q = session.query(Question).filter_by(id_= question_id).one()
        q_list = session.query(Question).filter_by(survey_id_=q.survey_id_).all()
        q_list_ids = [question.id_ for question in q_list]

        # Figure out next_url and prev_url
        prev_q_ix = q_list_ids.index(q.id_) - 1 if q_list_ids.index(q.id_) - 1 >= 0 else None
        next_q_ix = q_list_ids.index(q.id_) + 1 if q_list_ids.index(q.id_) + 1 < len(q_list) else None
        prev_url = url_for('controllers.showQuestion', question_id=q_list_ids[prev_q_ix]) if prev_q_ix != None else None # <---
        next_url = url_for('controllers.showQuestion', question_id=q_list_ids[next_q_ix]) if next_q_ix != None else url_for('controllers.thankYou')
        is_first = prev_url == None

        # Set up proper template and form_action_url
        template = templates.get(q.type_, 'freeform.html')  # Freeform is default fallback
        form_action_url = '/feedback/questions/' + str(q.id_)

        # Set up question form and fetch possible pre-existing answer
        form = qtype_forms.get(q.type_, AnswerFormFree(request.form))

        # Check for pre-existing answers
        try:
            pre_existing_answer = session.query(Answer).filter_by(question_id_=q.id_, feedback_id_=request.cookies['feedback_id']).order_by(Answer.created_at_.desc()).first()
        except:
            pre_existing_answer = None

        if pre_existing_answer != None:
            # Parse answer in db to response parameters for displaying it
            form.value_.data = pre_existing_answer.value_

        if q.type_ == 'Choices':
            form.setChoices(q.questionchoices)

        # Get progress
        progress, missing = get_progress(feedback)

        response = make_response(render_template(template,
                                                form=form,
                                                form_action_url=form_action_url,
                                                question_id=q.id_,
                                                question_title=q.title_,
                                                question_type=q.type_,
                                                prev_url=prev_url,
                                                next_url=next_url,
                                                is_first=is_first,
                                                progress=progress,
                                                answer=pre_existing_answer
                                                ))

        return response


    # POST: Write answer to database
    elif request.method == 'POST':
        # Get question type
        question = session.query(Question).filter_by(id_=request.form['question_id']).first()

        # Parse new answer from form if it exists
        if request.form.get('value_'):
            new_answer_val = str(request.form['value_'])

        # If mandatory question is missing answer
        elif bool(question.optional_) == False:
            flash('Please answer this question.')
            this_url = url_for('controllers.showQuestion', question_id=question.id_)
            return redirect(this_url)

        # If optional question is missing answer, create empty answer value
        else:
            new_answer_val = ''

        # Get possible pre-existing answer
        answers = session.query(Answer).filter_by(feedback_id_=int(request.cookies['feedback_id']), question_id_=int(request.form['question_id'])).all()

        # If pre-existing answer found, take the answer object for updating
        if len(answers) > 0:
            answer_object = answers[0]
        # If no pre-existing answer found
        else:
            # Add placeholder '' to value_
            answer_object = Answer('', int(request.cookies['feedback_id']), int(request.form['question_id']))

        # Special question type (Picture)
        if question.type_ == 'Picture':
            # user gave a new file:
            if request.files.get('userPicture'):
                file = request.files['userPicture']
                if file:
                    fileName = 'F' + str(answer_object.feedback_id_) + 'A' + str(question.id_) + \
                                '_' + str(datetime.datetime.now().hour) + \
                                '_' + str(datetime.datetime.now().minute) + \
                                '_' + str(datetime.datetime.now().second) + '.PNG'
                    imgPath = '/static/' + fileName
                    file.save(parentdir + imgPath)
                    answer_object.image_source_ = imgPath
                    answer_object.value_ = imgPath
                    session.add(answer_object)
                    session.commit()
        # All other question types:
        else:
            answer_object.value_ = new_answer_val

        session.add(answer_object)
        session.commit()

        #----------------------------------------------------------------------
        # NOTE: Replacing value_ with '' will only removes path to img, img data has to be removed separately
        #----------------------------------------------------------------------

        # Redirect to previous if 'Prev' was clicked
        if 'Previous' in request.form.keys():
            return redirect(request.form['prev_url'])

        # Redirect to next if 'Next' was clicked
        if 'Next' in request.form.keys():
            return redirect(request.form['next_url'])

        return 'POST redirection to next/prev failed'

routes.append(dict(rule='/feedback/questions/<int:question_id>', view_func=showQuestion, options=dict(methods=['GET', 'POST'])))


#---------------------------------------------------------------------------------------------------
# ROUTE: THANK YOU
#---------------------------------------------------------------------------------------------------

# /feedback/thankyou
def thankYou():
    # Shows an award and thank you message ONLY IF the survey is completed.
    # This should be checked when this action gets called.
    # The cookie should also be deleted.
    session.rollback()
    session.flush()

    feedback_id = request.cookies['feedback_id']
    feedback = session.query(Feedback).filter_by(id_=feedback_id).one()

    # Check that answer entries have been created for each survey question
    progress, missing = get_progress(feedback)

    response = make_response(render_template('survey_lastpage.html'))
    # response = make_response(render_template('survey_lastpage.html', gift_file=gift_file))
    response.set_cookie('feedback_id', '', expires=0)  # Delete cookie
    return response

routes.append(dict(rule='/feedback/thankyou', view_func=thankYou, options=dict(methods=['GET'])))


# /feedback
def newFeedbackForSurvey(surveyID):
    # Creates a feedback record
    # Stores the id to that record in a cookie
    # Has respective view that shows the latest active survey

    # Form dict
    qtype_forms = {'Freeform': AnswerFormFree(request.form),
                    'Thumbs': AnswerFormThumbs(request.form),
                    'Stars': AnswerFormStars(request.form),
                    'Smileys': AnswerFormSmileys(request.form),
                    'Choices': AnswerFormChoices(request.form),
                    'Picture': AnswerFormFree(request.form)}

    # From active surveys, get one with greatest id
    survey = session.query(Survey).filter(Survey.id_ == surveyID,Survey.enabled_).first()
    if survey == None:
        return 'No active surveys.'

    # Check if valid cookie exists
    feedback = None
    try:
        cookie = request.cookies['feedback_id']
        if not (cookie == None or (request.cookies['survey_id'] != surveyID)):
            # Fetch feedback with id_ == cookie from db
            feedback = session.query(Feedback).filter_by(id_=cookie).one()
    except:
        pass

    # If no valid cookie exists, create new feedback and new cookie with feedback id_ as value
    if feedback == None or cookie==None or len(cookie) == 0:
        feedback = Feedback(survey_id_=survey.id_)
        session.add(feedback)
        session.commit()  # For some reason, feedback.survey_id_ is not yet entered into db. (((WHY)))

        # Workaround to store feedback.survey_id_ into db: query, change, commit
        feedback = session.query(Feedback).order_by(Feedback.id_.desc()).first()
        feedback.survey_id_= survey.id_
        session.add(feedback)
        session.commit()

        # Check that feedback.survey_id_ is now stored in db
        feedback = session.query(Feedback).order_by(Feedback.id_.desc()).first()

    # Get list of survey questions
    q_list = session.query(Question).filter_by(survey_id_=survey.id_).order_by(Question.id_).all()

    # Get first question
    q, response = None, None
    try:
        q = q_list[0]
    except:
        return 'Survey has no questions. Thank you & goodbye.'

    # Show first survey question:
    if q != None:
        template = templates.get(q.type_, 'freeform.html')  # Defaults to show_question_freeform for now
        form = qtype_forms.get(q.type_, AnswerFormFree(request.form))  # Defaults to AnswerFormFree for now
        prev_url = None
        next_url = url_for('controllers.thankYou') if len(q_list) <= 1 else url_for('controllers.showQuestion', question_id=q_list[1].id_)

        progress = 0

        response = make_response(render_template('survey_frontpage.html',
                                                    survey=survey,
                                                    question_id=q.id_,
                                                    feedback=feedback,
                                                    progress=progress
                                                    ))
        # Set cookie to value of feedback.id_
        response.set_cookie('feedback_id', str(feedback.id_))

    return response

routes.append(dict(rule='/feedback/<int:surveyID>', view_func=newFeedbackForSurvey, options=dict(methods=['GET'])))
