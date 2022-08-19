from flask import Blueprint

from . import views

routes = Blueprint('public', __name__, url_prefix='/')

routes.add_url_rule(rule='/', endpoint='index', view_func=views.index)
