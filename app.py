import sys
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import Base, Survey, Answer, Feedback

# Flask
app = Flask(__name__)
app.secret_key = "flask rocks!"
app.debug = True


# Bind SQLAlchemy
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Put routes here for now
@app.errorhandler(404)
def page_not_found(error):
    print('Enter page_not_found:')
    return "404 Page not found"


@app.errorhandler(405)
def method_not_found(error):
    print('Enter method_not_found:')
    return "405 Method not found"


@app.errorhandler(500)
def internal_server_error(error):
    print('Enter internal_server_error:')
    return '500 Internal server error *'


@app.errorhandler(Exception)
def exception_handler(error):
    print('Enter exceptionHandler:')
    print(error)
    return 'Unspecified error: not 404, 405 or 500'


@app.route('/')
def hello():
    return "Hello world!"


if __name__ == '__main__':

    try:
        app.run()

    except Exception as e:
        print(e)
