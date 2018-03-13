import datetime

class Answer:
    __tablename__ = "answers"

    id_ = int()
    value = str()
    created_at = datetime.datetime
    question_id = int()
    feedback_id = int()

    def __init__(self, id_, value_, question_id_, feedback_id_):
        self.id_ = id_
        self.value =  value_
        self.created_at = datetime.datetime.now()
        self.question_id = question_id_
        self.feedback_id = feedback_id_

    def __repr__(self):
        return "<Id: {}, Created_at: '{}', Question_id: {}, Feedback_id {}, Value: '{}'>".format(self.id_, self.created_at, self.question_id, self.feedback_id, self.value)

