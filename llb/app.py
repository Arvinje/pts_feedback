from flask import Flask
from config.db_setup import db

app = Flask(__name__)
app.secret_key = "flask rocks!"