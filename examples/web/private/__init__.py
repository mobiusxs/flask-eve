from flask import Blueprint

from . import views

routes = Blueprint('private', __name__, url_prefix='/private')

routes.add_url_rule(rule='/', endpoint='index', view_func=views.index)
