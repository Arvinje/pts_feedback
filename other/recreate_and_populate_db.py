import os, inspect
from sqlalchemy import MetaData

# Backtrack to parent dir to prevent import problems
import os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

# Drop all previously existing tables
from config.setup import engine, session
meta = MetaData(bind=engine)
meta.reflect()
meta.drop_all()

# Create tables again
from models.admin import Admin
from models.feedback import Feedback
from models.survey import Survey
from models.question import Question
from models.answer import Answer
from models.questionChoice import QuestionChoice

# Populate with entries:

# Admins
admin_1 = Admin(id_=1, email_='inka.simola@bla.com', password_='inkapasswd')

# Survey 1
s1 = Survey(id_=1, description_='Emotional survey', start_date_='2018-04-12', end_date_='2018-04-13', admin_id_=1)

# Survey 1 Q1
q1 = Question(id_=1, type_='Multiple choice', title_='Q1: How was the bus ride?', survey_id_=1)
q1_c1 = QuestionChoice(id_=1, title_="I loved it", question_id_=1)

# Survey 1 Q2
q1_c2 = QuestionChoice(id_=2, title_="I hated it", question_id_=1)
q2 = Question(id_=2, type_="Freeform", title_="Q2: Tell us how you feel", survey_id_=1)

# Survey 2
s2 = Survey(id_=2, description_='Technical survey', start_date_='2018-04-13', end_date_='2018-06-30', admin_id_=1)

# Survey 2 Q1
q3 = Question(id_=3, type_='Multiple choice', title_='Q1: Smoothness of ride', survey_id_=2)
q3_c1 = QuestionChoice(id_=3, title_="1", question_id_=3)
q3_c2 = QuestionChoice(id_=4, title_="2", question_id_=3)
q3_c3 = QuestionChoice(id_=5, title_="3", question_id_=3)
q3_c4 = QuestionChoice(id_=6, title_="4", question_id_=3)
q3_c5 = QuestionChoice(id_=7, title_="5", question_id_=3)

# Survey 1 Q2
q4 = Question(id_=4, type_='Smileys', title_="Q2: Air quality", survey_id_=2)
q4_c1 = QuestionChoice(id_=8, title_="frown", question_id_=3)
q4_c2 = QuestionChoice(id_=9, title_="meh", question_id_=3)
q4_c3 = QuestionChoice(id_=10, title_="incredible", question_id_=3)

# Feedbacks
fb_1 = Feedback(id_=1)
fb_2 = Feedback(id_=2)
fb_3 = Feedback(id_=3)
fb_4 = Feedback(id_=4)

# Answers from first feedback (survey was 1)
a_f1_q1 = Answer(id_=1, value_=q1_c1.title_, feedback_id_=1, question_id_=1)
a_f1_q2 = Answer(id_=2, value_='Wow, I feel fabulous, thank you!', feedback_id_=1, question_id_=2)

# Answers from second feedback (survey was 1)
a_f2_q1 = Answer(id_=3, value_=q1_c2.title_, feedback_id_=2, question_id_=1)
a_f2_q2 = Answer(id_=4, value_='I feel miserable. The bus ride ruined my day.', feedback_id_=2, question_id_=2)

# Answers from third feedback (survey was 2)
a_f3_q3 = Answer(id_=5, value_=q3_c4.title_, feedback_id_=3, question_id_=3)
a_f3_q4 = Answer(id_=6, value_=q4_c1.title_, feedback_id_=3, question_id_=4)

# Answers from fourth feedback (survey was 2)
a_f4_q3 = Answer(id_=7, value_=q3_c5.title_, feedback_id_=4, question_id_=3)
a_f4_q4 = Answer(id_=8, value_=q4_c2.title_, feedback_id_=4, question_id_=4)


# Add objects to database
for obj in [admin_1, s1, q1, q1_c1, q1_c2, q2, s2, q3, q3_c1, q3_c2, q3_c3, q3_c4, q3_c5, q4, q4_c1, q4_c2, q4_c3, fb_1, fb_2, fb_3, fb_4, a_f1_q1, a_f1_q2, a_f2_q1, a_f2_q2, a_f3_q3, a_f3_q4, a_f4_q3, a_f4_q4]:
  session.add(obj)
  session.commit()
  session.query(Admin).all()





