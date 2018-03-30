from flask import Flask
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__, template_folder="views")
app.secret_key = "flask rocks!"
app.debug = True

# Initialize db
from models.feedback import Feedback
from models.survey import Survey
from models.question import Question
from models.answer import Answer

# Import routes
from controllers import mod
app.register_blueprint(mod, url_prefix='')

# Error routes (either here or imported)
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

if __name__ == '__main__':
    try:
        app.run()

    except Exception as e:
        print(e)
