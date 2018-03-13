from app import app, db
from flask import flash, render_template, request, redirect
from wtforms import Form, IntegerField, StringField
from models.survey import surveyForm

@app.route('/addNewSurvey', methods=['GET', 'POST'])
def addNewSurvey():
    form = surveyForm(request.form)

    if request.method == 'POST' and form.validate():
        new_survey = db.prepare("INSERT INTO survey VALUES ($1, $2)")
        with db.xact():
        	new_survey(form.id.data, form.description.data)
        
        flash("Survey " + str(form.id.data) + " " +  \
            form.description.data + " saved successfully!")
        return redirect('/')

    return render_template('new_survey.html', form=form)

@app.route('/printSurveys', methods=['GET', 'POST'])
def printSurveys():
    surveys = []
    form = surveyForm(request.form)

    all_the_surveys = db.prepare("SELECT * FROM survey")
    
    with db.xact():
      for survey in all_the_surveys():
        surveys.append(survey[1])
    
    return render_template('surveys.html', surveys=surveys)