from flask import Blueprint


mod = Blueprint('controllers', __name__)

@mod.route('/')
def home():
    return 'App home'


from .Questions import routes as question_routes
from .Surveys import routes as survey_routes


routes = (
    question_routes +
    survey_routes)

for r in routes:
    mod.add_url_rule(
        r['rule'],
        endpoint=r.get('endpoint', None),
        view_func=r['view_func'],
**r.get('options', {}))

