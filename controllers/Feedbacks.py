import os, inspect, datetime

from flask import Flask, render_template, request, redirect, flash, make_response, url_for
from flask import session as flasksession
from sqlalchemy import desc, distinct
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

# Form-class helps data processing
# with html-files and it has useful validation-methods:
class SurveyForm(Form):
    description = StringField('Description', [validators.Length(min=4, max=25),
                                            checkThatFieldIsNotOnlyWhiteSpace])
    start_date_ = DateField('Start date (YYYY-MM-DD)', [validators.DataRequired()])
    end_date_ = DateField('End date (YYYY-MM-DD)', [validators.DataRequired()])

class AnswerFormFree(Form):
    # description = StringField('Description', [validators.Length(min=0, max=1000),
    #                     checkThatFieldIsNotOnlyWhiteSpace])
    value_ = StringField('Answer', [validators.DataRequired()])

class AnswerFormThumb(Form):
    # description = StringField('Description', [validators.Length(min=4, max=1000),
    #                     checkThatFieldIsNotOnlyWhiteSpace])
    value_ = StringField('Answer', [validators.DataRequired()])

class AnswerFormStar(Form):
    # description = StringField('Description', [validators.Length(min=4, max=1000),
    #                     checkThatFieldIsNotOnlyWhiteSpace])
    value_ = StringField('Answer', [validators.DataRequired()])

class AnswerFormSmiley(Form):
    # description = StringField('Description', [validators.Length(min=4, max=1000),
    #                     checkThatFieldIsNotOnlyWhiteSpace])
    value_ = StringField('Answer', [validators.DataRequired()])


routes = []

templates = {'Freeform': 'show_question_freeform.html',
            'Thumbs': 'show_question_thumbs.html',
            'Stars': 'show_question_stars.html',
            'Smileys': 'show_question_smileys.html',
            'Thankyou': 'thankyou.html'}
print('---TEMPLATE DICT: {}'.format(templates))
# templates = {'Freeform': 'show_question_freeform.html',
#       'Thumbs': 'show_question_thumbs.html',
#       'Stars': 'show_question_stars.html',
#       'Smileys': 'show_question_smileys.html',
#       'Thankyou': 'thankyou.html'}


#---------------------------------------------------------------------------------------------------
# NEW FEEDBACK
#---------------------------------------------------------------------------------------------------

# /feedback
def newFeedback():
    # creates a feedback record
    # stores the id to that record in a cookie
    # has respective view that shows the latest active survey

    print('\n--- ENTERING newFeedback, method: {}'.format(request.method))

    qtype_forms = {'Freeform': AnswerFormFree(request.form),
            'Thumbs': AnswerFormThumb(request.form),
            'Stars': AnswerFormStar(request.form),
            'Smileys': AnswerFormSmiley(request.form)}
    print('---FORM DICT: {}'.format(qtype_forms))

    # From active surveys, get one with greatest id
    survey = session.query(Survey).filter(Survey.end_date_ >= datetime.datetime.now()).order_by(Survey.id_.desc()).first()
    if survey != None:
        print('--- FOUND SURVEY ID {}, TITLE {}'.format(survey.id_, survey.description_))
    else:
        return 'No active surveys.'

    # Check if valid cookie exists
    feedback = None
    try:
        cookie = request.cookies['feedback_id']
        if cookie == None:
            print('---FOUND COOKIE WITH VALUE None')
        else:
            # Fetch feedback with id_ == cookie from db
            feedback = session.query(Feedback).filter_by(id_=cookie).one()
            if feedback.survey_id_ == survey.id_:
                print('---FOUND VALID COOKIE WITH FEEDBACK_ID {} CONNECTED TO SURVEY {}'.format(cookie, survey.id_))
            else:
                print('---FOUND INVALID COOKIE FOR THIS SURVEY:')
    except:
        pass

    # If no valid cookie exists, create new feedback and new cookie with feedback id_ as value
    if feedback == None:
        print('--- NO COOKIE FOUND. CREATING NEW FEEDBACK RECORD FOR THIS SURVEY...')
        feedback = Feedback(survey_id_=survey.id_)
        session.add(feedback)
        session.commit()  # For some reason, feedback.survey_id_ is not entered into db via this

        # Workaround to store feedback.survey_id_ into db: query, change, commit
        feedback = session.query(Feedback).order_by(Feedback.id_.desc()).first()
        feedback.survey_id_= survey.id_
        session.add(feedback)
        session.commit()

        # Check that feedback.survey_id_ is now stored in db
        feedback = session.query(Feedback).order_by(Feedback.id_.desc()).first()
        print('---CREATED FEEDBACK ENTRY {}'.format(feedback.serialize))
        print('--- COOKIE / SESSION ID WILL BE SET TO: {}'.format(feedback.id_))

    # Get list of survey questions
    q_list = session.query(Question).filter_by(survey_id_=survey.id_).order_by(Question.id_).all()
    print('---QUESTIONS FOR SURVEY {}: {}, len {}'.format(survey.id_, q_list, len(q_list)))

    # Get first question
    q, response = None, None
    try:
        q = q_list[0]
    except:
        return 'Survey has no questions. Thank you & goodbye.'
        pass

    # Show first survey question:
    if q != None:
        question_id = int(q.id_)
        question_title = q.title_
        template = templates.get(q.type_, 'show_question_freeform.html')
        form = qtype_forms.get(q.type_, AnswerFormFree(request.form))
        prev_url = None
        next_url = url_for('controllers.thankYou') if len(q_list) <= 1 else url_for('controllers.showQuestion', question_id=q_list[1].id_)

        print('---QUESTION TYPE: {}'.format(q.type_))
        flash('---TEMPLATE: {}, {}'.format(type(template), template))
        flash('---FORM: {}, {}'.format(type(form), form))
        print('---FIRST QUESTION_ID: {}, {}'.format(type(question_id), question_id))
        print('---QUESTION_TITLE: {}, {}'.format(type(question_title), question_title))
        print('---NEXT_URL: {}, {}'.format(type(next_url), next_url))
        print('---PREV_URL: {}, {}'.format(type(prev_url), prev_url))

        response = make_response(render_template('feedback.html',
                                                    survey=survey,
                                                    question_id=q.id_,
                                                    question_title=q.title_,
                                                    feedback=feedback))

        # Set cookie to value of feedback.id_
        response.set_cookie('feedback_id', str(feedback.id_))

        print('---RESPONSE CREATED. EXITING newFeedback AND RENDERING feedback.html: {}'.format(response))

    return response

routes.append(dict(rule='/feedback', view_func=newFeedback, options=dict(methods=['GET'])))


#---------------------------------------------------------------------------------------------------
# SHOW QUESTION
#---------------------------------------------------------------------------------------------------

# /feedback/questions/<int:question_id>
def showQuestion(question_id, methods=['GET', 'POST']):
    # Shows the respective question related to the current survey (latest active one).
    #   If there already is a feedback id stored in cookie, the controller's action would retrieve it and
    #   fills the form/question if there was already an answer to that question.
    #   *tip: query EXIST if an answer record exists with question_id and feedback_id*
    #   NOTE: The page should have links to next and previous question.
    #   NOTE: It renders a different view based on the question type.

    cookie = request.cookies['feedback_id']
    print('\n--- COOKIE / SESSION ID: {}'.format(cookie))
    feedback = session.query(Feedback).filter_by(id_=int(cookie)).one()
    print('---FEEDBACK: {}'.format(feedback.serialize))

    # Form dict
    qtype_forms = {'Freeform': AnswerFormFree(request.form),
            'Thumbs': AnswerFormThumb(request.form),
            'Stars': AnswerFormStar(request.form),
            'Smileys': AnswerFormSmiley(request.form)}
    print('---FORM DICT: {}'.format(qtype_forms))

    #-------------------
    # GET: SHOW QUESTION
    #-------------------
    if request.method == 'GET':
        print('\n--- ENTERING showQuestion with question_id: {}, method: {}'.format(question_id, request.method))

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


        # Set up proper template
        template = templates.get(q.type_, 'Freeform')  # Freeform is default fallback
        flash('Chose template {} from templates: {}'.format(template, templates))

        form_action_url = '/feedback/questions/' + str(q.id_)

        # Set up question form and fetch possible pre-existing answer
        form = qtype_forms.get(q.type_, AnswerFormFree(request.form))
        flash('Chose form from qtype_forms: {}'.format(form))

        try:
            print('XXXX', type(q.id_), q.id_, type(request.cookies['feedback_id']), request.cookies['feedback_id'])
            pre_existing_answers = session.query(Answer).filter_by(question_id_=q.id_, feedback_id_=request.cookies['feedback_id']).order_by(Answer.created_at_.desc()).first()
            print('YYY', pre_existing_answers)
        except:
            pre_existing_answers = None


        if pre_existing_answers != None:
            print('form.value_.data == {}'.format(form.value_.data))
            print('---PRE-EXISTING ANSWER FOUND WITH VALUE {}'.format(pre_existing_answers.value_))
            form.value_.data = pre_existing_answers.value_
            # form.value_ = pre_existing_answers.value_
            print('form.value_.data == {} {}'.format(type(form.value_.data), form.value_.data))
        else:
            print('---NO PRE-EXISTING ANSWER FOUND.')

        form


        # Debug statements
        flash('---TEMPLATE: {}, {}'.format(type(template), template))
        flash('---FORM: {}, {}'.format(type(form), form))
        print('---FORM.VALUE_.DATA: {}'.format(form.value_.data))
        print('---FORM_ACTION_URL: {}, {}'.format(type(form_action_url), form_action_url))

        print('---LIST OF QUESTION IDS: {}'.format(q_list_ids))
        print('---QUESTION: {}, {}'.format(type(q), q))
        print('---QUESTION TYPE: {}, {}'.format(type(q.type_), q.type_))
        print('---IS_FIRST: {}, {}'.format(type(is_first), is_first))
        print('---QUESTION_ID: {}, {}'.format(type(q.id_), q.id_))
        print('---QUESTION_TITLE: {}, {}'.format(type(q.title_), q.title_))
        print('---NEXT_URL: {}, {}'.format(type(next_url), next_url))
        print('---PREV_URL: {}, {}'.format(type(prev_url), prev_url))

        response = make_response(render_template(template,
                                                form=form,
                                                form_action_url=form_action_url,
                                                question_id=q.id_,
                                                question_title=q.title_,
                                                prev_url=prev_url,
                                                next_url=next_url,
                                                is_first=is_first))
        # response = make_response(render_template('show_question_freeform.html', form_action_url=form_action_url, question_id=q.id_))
        # response = render_template(template, form_action_url=form_action_url, is_first=is_first, not_first=not_first, question_id=q.id_, question_title=q.title_, prev_url=prev_url, next_url=next_url)
        # response = render_template(template, form=form, is_first=is_first, not_first=not_first, question_id=question_id, question_title=question_title, prev_url=prev_url, next_url=next_url)
        # print(response)
        print('---RESPONSE CONTENT:')
        print(response.get_data())
        print('---RESPONSE CREATED. EXITING showQuestion AND RENDERING {}'.format(template))

        return response

    #----------------
    # POST QUESTION:
    #----------------
    elif request.method == 'POST':
        print('\n---ENTERING WITH POST')
        print(request.form)

        # Replace possible pre-existing answer
        try:
            print('---COMPARING POSTED ANSWER TO POSSIBLY PRE-EXISTING ANSWER')
            answer = session.query(Answer).filter_by(feedback_id_=request.cookies['feedback_id'], question_id_=request.form['question_id'])[0]
            print('ok type {} content {}'.format(type(answer), answer))
            flash('answer.serialize {}'.format(answer.serialize))
            if answer.value_ != request.form['value_']:
                print('---CHANGING PRE-EXISTING ANSWER')
                answer.value_ = request.form['value_']
                print('---REPLACED VALUE OF PRE-EXISTING ANSWER, ANSWER NOW:')
                print(answer.serialize)
            else:
                flash('Scrolling through, did not change answer')
        except:
            # Create new answer object
            answer = Answer(request.form['value_'], int(request.cookies['feedback_id']), int(request.form['question_id']))
            flash('---CREATED NEW ANSWER OBJECT:')
            flash('answer.serialize {}'.format(answer.serialize))
            print('---ANSWER.value_: {} {} len {}'.format(type(answer.value_), answer.value_, len(answer.value_)))
        if len(answer.value_) > 0:
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

# /feedback/thankyou
def thankYou():
    # Shows an award and thank you message ONLY IF the survey is completed.
    # This should be checked when this action gets called.
    # The cookie should also be deleted.
    print('\n--- ENTERING thankYou, method: {}'.format(request.method))
    print(request.form)

    # Check that answer entries have been created for each survey question
    feedback_id = request.cookies['feedback_id']
    feedback = session.query(Feedback).filter_by(id_=feedback_id).one()
    survey_id = feedback.survey_id_
    questions = session.query(Question).filter_by(survey_id_=survey_id).all()
    answers = session.query(Answer).filter_by(feedback_id_=feedback_id).all()
    q_ids = set([item.id_ for item in questions])
    a_ids = set([item.question_id_ for item in answers if len(item.value_) > 0])
    print('---QUESTIONS: {}'.format(q_ids))
    print('---ANSWERS: {}'.format(a_ids))
    missing = q_ids.difference(a_ids)


    flash('---QUESTIONS {} OUT OF {} ANSWERED, MISSING: {}'.format(a_ids, q_ids, missing))

    # If no answers missing
    if len(missing) == 0:
        gifts = {0: 'gift_1.png', 1: 'gift_2.png', 2: 'gift_3.png'}
        gift_ix = int(request.cookies['feedback_id']) % len(gifts)
        gift_file = '/static/imgs/{}'.format(gifts[gift_ix])

        print('---GIFT FILE: {}'.format(gift_file))

        response = render_template('thankyou.html', gift_file=gift_file)
        return response

    # If answers missing
    elif len(missing) == 1:
        return 'Please fill in question {}'.format(list(missing)[0])
    else:
        return 'Please fill in questions {}'.format(list(missing))


routes.append(dict(rule='/feedback/thankyou', view_func=thankYou, options=dict(methods=['GET'])))


