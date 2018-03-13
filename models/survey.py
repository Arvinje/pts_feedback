import datetime

from app import app, db
from flask import flash, render_template, request, redirect
from wtforms import Form, IntegerField, StringField

class Survey:
    __tablename__ = "surveys"
 
    id = int()
    description = str()
    start_date = datetime.date
    end_date = datetime.date

    def __init__(self, id_, description_):
        self.id = id_
        self.description = description_

    def __repr__(self):
        return "<Survey: {}>".format(self.id)

class surveyForm(Form):
    id = IntegerField("ID")
    description = StringField("Description")