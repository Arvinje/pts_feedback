class Feedback:
    __tablename__ = "feedback"

    id_ = int()

    def __init__(self, id_):
        self.id_ = id_

    def __repr__(self):
        return "<Id: {}>".format(self.id_)
