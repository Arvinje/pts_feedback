import os, inspect
from sqlalchemy import MetaData

# Backtrack to parent dir to prevent import problems
import os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

# Drop all previously existing tables
from config.setup import engine, session
# meta = MetaData(bind=engine)
# meta.reflect()
# meta.drop_all()

# Create tables again
# from models.admin import Admin
from models.feedback import Feedback
from models.survey import Survey
from models.question import Question
from models.answer import Answer
from models.questionChoice import QuestionChoice

# Populate with entries:

# Admins
# admin_1 = Admin(id_=1, email_='inka.simola@bla.com', password_='inkapasswd')
# admin_1 = Admin(email_='inka.simola@bla.com', password_='inkapasswd')

# Survey 1
s1 = Survey(description_='Emotional survey', start_date_='2018-04-12', end_date_='2018-12-01')
# s1 = Survey(description_='Emotional survey', start_date_='2018-04-12', end_date_='2018-04-13', admin_id='1')
session.add(s1)
session.commit()

# # Survey 2
# s2 = Survey(description_='Technical survey', start_date_='2018-04-13', end_date_='2018-12-01')
# # s2 = Survey(id_=2, description_='Technical survey', start_date_='2018-04-13', end_date_='2018-06-30', admin_id_=1)
# session.add(s2)
# session.commit()

# Survey 1 Q1 (freeform)
q1 = Question(type_='Freeform', title_="Q1: Tell us how you feel", survey_id_=1)
session.add(q1)
session.commit()

# Survey 1 Q2
q2 = Question(type_='Thumbs', title_='Q2: How was the bus ride?', survey_id_=1)
session.add(q2)
session.commit()

# Survey 1 Q3
q3 = Question(type_='Stars', title_='Q3: Smoothness of ride', survey_id_=1)
session.add(q3)
session.commit()

# Survey 1 Q4
q4 = Question(type_='Smileys', title_='Q4: Pleasantness of ride', survey_id_=1)
session.add(q4)
session.commit()


# Question choices
qc_1 = QuestionChoice(title_="thumbs up", question_id_=2)
qc_2 = QuestionChoice(title_="thumbs down", question_id_=2)

qc_3 = QuestionChoice(title_="1 star", question_id_=3)
qc_4 = QuestionChoice(title_="2 star", question_id_=3)
qc_5 = QuestionChoice(title_="3 star", question_id_=3)
qc_6 = QuestionChoice(title_="4 star", question_id_=3)
qc_7 = QuestionChoice(title_="5 star", question_id_=3)

qc_8 = QuestionChoice(title_="smile", question_id_=4)
qc_9 = QuestionChoice(title_="meh", question_id_=4)
qc_10 = QuestionChoice(title_="frown", question_id_=4)

for item in [qc_1, qc_2, qc_3, qc_4, qc_5, qc_6, qc_7, qc_8, qc_9, qc_10]:
  session.add(item)
  session.commit()

# # Survey 1 Q2
# q4 = Question(type_='Smileys', title_="Q2: Air quality", survey_id_=2)
# session.add(q4)
# session.commit()
# q4_c1 = QuestionChoice(title_="frown", question_id_=3)
# q4_c2 = QuestionChoice(title_="meh", question_id_=3)
# q4_c3 = QuestionChoice(title_="incredible", question_id_=3)

# for item in [q4_c1, q4_c2, q4_c3]:
#   session.add(item)
#   session.commit()



# # Feedbacks
# fb_1 = Feedback(survey_id_=1)
# fb_2 = Feedback(survey_id_=1)
# fb_3 = Feedback(survey_id_=2)
# fb_4 = Feedback(survey_id_=2)

# for fb in [fb_1, fb_2, fb_3, fb_4]:
#   session.add(fb)
#   session.commit()

# fb_1, fb_2, fb_3, fb_4 = session.query(Feedback).order_by(Feedback.id_).all()
# fb_1.survey_id_ = 1
# fb_2.survey_id_ = 2
# fb_3.survey_id_ = 3
# fb_4.survey_id_ = 4

# # Answers from first feedback (survey was 1)
# a_f1_q1 = Answer(value_=q1_c1.title_, feedback_id_=1, question_id_=1)
# a_f1_q2 = Answer(value_='Wow, I feel fabulous, thank you!', feedback_id_=1, question_id_=2)

# # Answers from second feedback (survey was 1)
# a_f2_q1 = Answer(value_=q1_c2.title_, feedback_id_=2, question_id_=1)
# a_f2_q2 = Answer(value_='I feel miserable. The bus ride ruined my day.', feedback_id_=2, question_id_=2)

# # Answers from third feedback (survey was 2)
# a_f3_q3 = Answer(value_=q3_c4.title_, feedback_id_=3, question_id_=3)
# a_f3_q4 = Answer(value_=q4_c1.title_, feedback_id_=3, question_id_=4)

# # Answers from fourth feedback (survey was 2)
# a_f4_q3 = Answer(value_=q3_c5.title_, feedback_id_=4, question_id_=3)
# a_f4_q4 = Answer(value_=q4_c2.title_, feedback_id_=4, question_id_=4)


# # Add objects to database
# # for obj in [admin_1, s1, q1, q1_c1, q1_c2, q2, s2, q3, q3_c1, q3_c2, q3_c3, q3_c4, q3_c5, q4, q4_c1, q4_c2, q4_c3, fb_1, fb_2, fb_3, fb_4, a_f1_q1, a_f1_q2, a_f2_q1, a_f2_q2, a_f3_q3, a_f3_q4, a_f4_q3, a_f4_q4]:
# for obj in [s1, q1, q1_c1, q1_c2, q2, s2, q3, q3_c1, q3_c2, q3_c3, q3_c4, q3_c5, q4, q4_c1, q4_c2, q4_c3, fb_1, fb_2, fb_3, fb_4, a_f1_q1, a_f1_q2, a_f2_q1, a_f2_q2, a_f3_q3, a_f3_q4, a_f4_q3, a_f4_q4]:
#   session.add(obj)
#   session.commit()
