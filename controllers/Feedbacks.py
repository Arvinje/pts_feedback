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

    if verbose:
        print('\n{}'.format(90 * '*'))
        print('---- PARSING ANSWER VALUE FROM REQUEST FORM:')
        print('--- request.form.keys():')
        for item in request.form.keys():
            print('key: {} request.form[key]: {}'.format(item, request.form[item]))
        print('--- QUESTION TYPE: {}'.format(qtype))
        print('\n{}'.format(90 * '*'))

    if 'value_' in requestform.keys():
        parsed_answer = requestform['value_']

    print('---QUESTION TYPE WAS {}, parsed_answer is {}'.format(requestform['question_type'], parsed_answer))

    return parsed_answer


def db_answer_to_response(pre_existing_answer, qtype, form, verbose=False):
    if verbose:
        print('--- CREATING RESPONSE PARAMS FROM PRE-EXISTING ANSWER:')
        print('--- PRE-EXISTING ANSWER: {}, QTYPE: {}, FORM.VALUE_: {}'.format(pre_existing_answer.value_, qtype, form.value_))
    form.value_.data = pre_existing_answer.value_
    return form


def get_progress(feedback, verbose=False):
    survey_id = feedback.survey_id_
    questions = session.query(Question).filter_by(survey_id_=survey_id).all()
    answers = session.query(Answer).filter_by(feedback_id_=feedback.id_).all()
    print('---GET_PROGRESS FINDS ANSWERS {}'.format(answers))

    question_ids = set([item.id_ for item in questions])
    answer_ids = set([item.question_id_ for item in answers if len(item.value_) > 0])
    print('---GET_PROGRESS ACCEPTS ANSWER IDS {}'.format(answer_ids))

    missing = question_ids.difference(answer_ids)
    progress = int(len(answer_ids) / float(len(question_ids)) * 100) if len(question_ids) > 0 else 0.0

    missing_mandatory = []
    for item in questions:
        if verbose:
            print(item.id_, item.title_)
            print('OPTIONAL: {}'.format(item.optional_))
            print('IN MISSING: {}'.format(item.id_ in missing))
        if not bool(item.optional_) and item.id_ in missing:
            print('---MISSING MANDATORY QUESTION WITH ID {}: {}'.format(item.id_, item.title_))
            missing_mandatory.append(item.title_)

    return progress, missing, missing_mandatory


routes = []

templates = {'Freeform': 'freeform.html',
            'Text': 'freeform.html',
            'Thumbs': 'thumbs.html',
            'Stars': 'stars.html',
            'Smileys': 'smileys.html',
            'Thankyou': 'survey_lastpage.html',
            'Choices': 'choices.html',
            'Picture': 'picture.html'}

#---------------------------------------------------------------------------------------------------
# ROUTE: NEW FEEDBACK
#---------------------------------------------------------------------------------------------------

# /feedback
def newFeedback():
    # Creates a feedback record
    # Stores the id to that record in a cookie
    # Has respective view that shows the latest active survey
    print('\n--- ENTERING newFeedback, method: {}'.format(request.method))

    # Form dict
    qtype_forms = {'Freeform': AnswerFormFree(request.form),
                    'Thumbs': AnswerFormThumbs(request.form),
                    'Stars': AnswerFormStars(request.form),
                    'Smileys': AnswerFormSmileys(request.form),
                    'Choices': AnswerFormChoices(request.form),
                    'Picture': AnswerFormFree(request.form)}

    # From active surveys, get one with greatest id
    survey = session.query(Survey).filter(Survey.end_date_ >= datetime.datetime.now(),Survey.enabled_).order_by(Survey.id_.desc()).first()
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
    if feedback == None or cookie==None or len(cookie) == 0:
        print('--- NO COOKIE FOUND. CREATING NEW FEEDBACK RECORD FOR THIS SURVEY...')
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
        print('---CREATED FEEDBACK ENTRY {}'.format(feedback.serialize))
        print('--- COOKIE / SESSION ID WILL BE SET TO: {}'.format(feedback.id_))
    else:
        print('---FEEDBACK WAS NOT NONE, IT\'S: {}'.format(feedback.serialize))

    # Get list of survey questions
    q_list = session.query(Question).filter_by(survey_id_=survey.id_).order_by(Question.id_).all()
    print('---QUESTIONS FOR SURVEY {}: {}, len {}'.format(survey.id_, q_list, len(q_list)))

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

        # Debug statements
        print('---QUESTION TYPE: {}'.format(q.type_))
        print('---TEMPLATE: {}, {}'.format(type(template), template))
        print('---FORM: {}, {}'.format(type(form), form))
        print('---FIRST QUESTION_ID: {}, {}'.format(type(q.id_), q.id_))
        print('---QUESTION_TITLE: {}, {}'.format(type(q.title_), q.title_))
        print('---NEXT_URL: {}, {}'.format(type(next_url), next_url))
        print('---PREV_URL: {}, {}'.format(type(prev_url), prev_url))

        response = make_response(render_template('survey_frontpage.html',
                                                    survey=survey,
                                                    question_id=q.id_,
                                                    feedback=feedback,
                                                    progress=progress
                                                    ))
        # Set cookie to value of feedback.id_
        response.set_cookie('feedback_id', str(feedback.id_))
        print('---RESPONSE CREATED. EXITING newFeedback AND RENDERING survey_frontpage.html: {}'.format(response))

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

    print('\n--- ENTERING showQuestion WITH METHOD {}: {}'.format(request.method, 70 * '*'))

    # Get feedback object
    cookie = request.cookies['feedback_id']
    feedback = session.query(Feedback).filter_by(id_=int(cookie)).one()
    print('\n--- COOKIE / SESSION ID: {}'.format(cookie))
    print('---FEEDBACK: {}'.format(feedback.serialize))

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
        print('GET')
        print('request.form: {}'.format(request.form))

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
        print('Chose template {} from templates: {}'.format(template, templates))
        form_action_url = '/feedback/questions/' + str(q.id_)

        # Set up question form and fetch possible pre-existing answer
        form = qtype_forms.get(q.type_, AnswerFormFree(request.form))
        print('Chose form {} from qtype_forms'.format(form))
        print('---FORM.value_: {}'.format(form.value_))
        print('---FORM.value_.data: {}'.format(form.value_.data))
        flash('Feedback_id == Cookie == {}'.format(feedback.id_))
        flash('form.value_.data: {}'.format(form.value_.data))

        # Check for pre-existing answers
        try:
            print('---CHECK FOR PRE-EXISTING ANSWER:')
            pre_existing_answer = session.query(Answer).filter_by(question_id_=q.id_, feedback_id_=request.cookies['feedback_id']).order_by(Answer.created_at_.desc()).first()
            print('---FOUND PRE-EXISTING ANSWER:', pre_existing_answer)
        except:
            pre_existing_answer = None

        if pre_existing_answer != None:
            print('---PRE-EXISTING ANSWER FOUND WITH VALUE {}'.format(pre_existing_answer.value_))

            # Parse answer in db to response parameters for displaying it
            print('--- CREATING RESPONSE PARAMS FROM PRE-EXISTING ANSWER:')
            print('--- PRE-EXISTING ANSWER: {}, QTYPE: {}, FORM.VALUE_.DATA: {}'.format(pre_existing_answer.value_, q.type_, form.value_.data))
            form.value_.data = pre_existing_answer.value_
            print('form.value_.data is now {} "{}"'.format(type(form.value_.data), form.value_.data))
        else:
            print('---NO PRE-EXISTING ANSWER FOUND.')

        if q.type_ == 'Choices':
            form.setChoices(q.questionchoices)


        # Debug statements
        print('---TEMPLATE: {}, {}'.format(type(template), template))
        print('---FORM: {}, {}'.format(type(form), form))
        print('---FORM.VALUE_: {}'.format(form.value_))
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

        # Get progress
        progress, missing, missing_mandatory = get_progress(feedback)

        # print('---PROGRESS {}'.format(progress))
        # print('---MISSING {}'.format(missing))
        # print('---MISSING MANDATORY {}'.format(missing_mandatory))
        # flash('progress: {}'.format(progress))
        # flash('missing: {}'.format(missing))
        # flash('missing_mandatory: {}'.format(missing_mandatory))


        #
        #--------- DEBUG HERE Thumbs form!!!
        # form = qtype_forms.get('Thumb', AnswerFormFree(request.form))
        print('form.value_: "{}"'.format(form.value_))
        print('form.value_.data: "{}"'.format(form.value_.data))
        if q.type_ not in ['Freeform', 'Text', 'Picture', 'Thankyou']:
            print('form.value_.choices: "{}"'.format(form.value_.choices))


        print('---FORM: {}'.format(form))
        print('---FORM.VALUE_.DATA: {}'.format(form.value_.data))

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

        print('---RESPONSE CREATED. EXITING showQuestion AND RENDERING {}'.format(template))

        return response


    # POST: Write answer to database
    elif request.method == 'POST':
        print('POST')
        print('request.form: {}'.format(request.form))
        print('request.cookies: {}'.format(request.cookies))

        # Get question type
        question = session.query(Question).filter_by(id_=request.form['question_id']).first()

        # Parse new answer from form if it exists
        if request.form.get('value_'):
            new_answer_val = str(request.form['value_'])
        # Replace with placeholder otherwise (this will be denied entry to db later)
        else:
            new_answer_val = ''
        print('---GOT new_answer_val FROM FORM: {}'.format(new_answer_val))

        # Only proceed with non-picture answers if value_ is not empty
        if len(new_answer_val) > 0 or question.type_ == 'Picture':

            # Get possible pre-existing answer
            print('---GET POSSIBLE PRE-EXISTING ANSWER')
            answers = session.query(Answer).filter_by(feedback_id_=int(request.cookies['feedback_id']), question_id_=int(request.form['question_id'])).all()
            print('len(answer_object): {}'.format(len(answers)))

            # If pre-existing answer found, take the answer object for updating
            if len(answers) > 0:
                answer_object = answers[0]
                print('---FOUND PRE-EXISTING ANSWER: {}'.format(answer_object))
                print('---PRE-EXISTING answer.value_: {}'.format(answer_object.value_))
            # If no pre-existing answer found
            else:
                print('---NO PRE-EXISTING ANSWER FOUND!')
                # Add placeholder '' to value_
                answer_object = Answer('', int(request.cookies['feedback_id']), int(request.form['question_id']))
                print('---CREATED NEW ANSWER OBJECT:')

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

            elif question.type_ == 'Choices':
                questionchoiceTitles = []
                for choice in question.questionchoices:
                    questionchoiceTitles.append(choice.title_)
                answer_object.value_ = questionchoiceTitles[int(new_answer_val)]

            # All other choices:
            else:
                answer_object.value_ = new_answer_val

            print('answer.serialize {}'.format(answer_object.serialize))
            print('---ANSWER_OBJECT.value_ type: {}, len {} value_ {}'.format(type(answer_object.value_), len(answer_object.value_), answer_object.value_, ))

            # # Validate: answer_object added/updated to db only if lenght > 0
            # if len(answer_object.value_) > 0:
            # Validate: answer_object added/updated to db only if the answer value has been edited
            # NOTE: Allow for zero length answer if user wants to remove answer.
            # NOTE: This only removes path to pic, not pic data
            if len(answer_object.value_) > 0:
                session.add(answer_object)
                session.commit()

        # Redirect to previous if 'Prev' was clicked
        if 'Previous' in request.form.keys():
            print('---EXITING showQuestion [POST], REDIRECTING TO PREV: {}'.format(request.form['prev_url']))
            return redirect(request.form['prev_url'])

        # Redirect to next if 'Next' was clicked
        if 'Next' in request.form.keys():
            print('---EXITING showQuestion [POST], REDIRECTING TO NEXT: {}'.format(request.form['next_url']))
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
    print('\n--- ENTERING thankYou, method: {}'.format(request.method))

    session.rollback()
    session.flush()

    feedback_id = request.cookies['feedback_id']
    feedback = session.query(Feedback).filter_by(id_=feedback_id).one()

    # Check that answer entries have been created for each survey question
    print('-----in thank you------')
    progress, missing, missing_mandatory = get_progress(feedback)
    print('---PROGRESS! {}'.format(progress))
    print('---MISSING! {}'.format(missing))
    print('---MISSING MANDATORY! {}'.format(missing_mandatory))
    # flash('progress: {}'.format(progress))
    # flash('missing: {}'.format(missing))
    # flash('missing_mandatory: {}'.format(missing_mandatory))
    # flash('Feedback_id == Cookie == {}'.format(feedback.id_))





    # WIP: this check should be unnecessary!
    # Add forcing on mandatory questions as e.g. flash message per mandatory question
    # If no mandatory answers missing




    # if len(missing_mandatory) == 0:

    #     # This is a placeholder for actual gift
    #     gifts = {0: 'gift_1.png', 1: 'gift_2.png', 2: 'gift_3.png'}
    #     gift_ix = int(request.cookies['feedback_id']) % len(gifts)
    #     gift_file = '/static/imgs/{}'.format(gifts[gift_ix])

    #     response = make_response(render_template('survey_lastpage.html', gift_file=gift_file))
    #     response.set_cookie('feedback_id', '', expires=0)  # Delete cookie
    #     print('---RESPONSE CREATED. EXITING thankYou AND RENDERING survey_lastpage.html: {}'.format(response))
    #     return response

    # # If answers missing
    # elif len(missing_mandatory) == 1:
    #     print('len(missing) == 1')
    #     return '<h3>Please fill in the following question:</h3><h4>{}</h4>'.format(list(missing_mandatory)[0])
    # else:
    #     print('len(missing) > 1')
    #     return '<h3>Please fill in the following questions:</h3><h4>{}</h4>'.format('<br>'.join(list(missing_mandatory)))


routes.append(dict(rule='/feedback/thankyou', view_func=thankYou, options=dict(methods=['GET'])))


# /feedback
def newFeedbackForSurvey(surveyID):
    # Creates a feedback record
    # Stores the id to that record in a cookie
    # Has respective view that shows the latest active survey
    print('\n--- ENTERING newFeedback, method: {}'.format(request.method))

    # Form dict
    qtype_forms = {'Freeform': AnswerFormFree(request.form),
                    'Thumbs': AnswerFormThumbs(request.form),
                    'Stars': AnswerFormStars(request.form),
                    'Smileys': AnswerFormSmileys(request.form),
                    'Choices': AnswerFormChoices(request.form),
                    'Picture': AnswerFormFree(request.form)}

    # From active surveys, get one with greatest id
    survey = session.query(Survey).filter(Survey.id_ == surveyID,Survey.enabled_).first()
    if survey != None:
        print('--- FOUND SURVEY ID {}, TITLE {}'.format(survey.id_, survey.description_))
    else:
        return 'No active surveys.'

    # Check if valid cookie exists
    feedback = None
    try:
        cookie = request.cookies['feedback_id']
        if cookie == None or (request.cookies['survey_id'] != surveyID):
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
    if feedback == None or cookie==None or len(cookie) == 0:
        print('--- NO COOKIE FOUND. CREATING NEW FEEDBACK RECORD FOR THIS SURVEY...')
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
        print('---CREATED FEEDBACK ENTRY {}'.format(feedback.serialize))
        print('--- COOKIE / SESSION ID WILL BE SET TO: {}'.format(feedback.id_))
    else:
        print('---FEEDBACK WAS NOT NONE, IT\'S: {}'.format(feedback.serialize))

    # Get list of survey questions
    q_list = session.query(Question).filter_by(survey_id_=survey.id_).order_by(Question.id_).all()
    print('---QUESTIONS FOR SURVEY {}: {}, len {}'.format(survey.id_, q_list, len(q_list)))

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

        # Debug statements
        print('---QUESTION TYPE: {}'.format(q.type_))
        print('---TEMPLATE: {}, {}'.format(type(template), template))
        print('---FORM: {}, {}'.format(type(form), form))
        print('---FIRST QUESTION_ID: {}, {}'.format(type(q.id_), q.id_))
        print('---QUESTION_TITLE: {}, {}'.format(type(q.title_), q.title_))
        print('---NEXT_URL: {}, {}'.format(type(next_url), next_url))
        print('---PREV_URL: {}, {}'.format(type(prev_url), prev_url))

        response = make_response(render_template('survey_frontpage.html',
                                                    survey=survey,
                                                    question_id=q.id_,
                                                    feedback=feedback,
                                                    progress=progress
                                                    ))
        # Set cookie to value of feedback.id_
        response.set_cookie('feedback_id', str(feedback.id_))
        print('---RESPONSE CREATED. EXITING newFeedback AND RENDERING survey_frontpage.html: {}'.format(response))

    return response

routes.append(dict(rule='/feedback/<int:surveyID>', view_func=newFeedbackForSurvey, options=dict(methods=['GET'])))
