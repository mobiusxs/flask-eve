from flask import Blueprint

from flask_eve import models
from flask_eve import utils
from flask_eve import views


class Eve:
    def __init__(self, app=None, db=None):
        if app is not None and db is not None:
            self.init_app(app, db)

    def init_app(self, app, db=None):
        app.extensions['eve'] = self
        if not db:
            sqlalchemy = app.extensions.get('sqlalchemy')
            if not sqlalchemy:
                raise ValueError("Flask-SQLAlchemy instance required")
            db = sqlalchemy.db
        self.init_models(db)
        self.init_views(app)
        self.init_context(app)

    @staticmethod
    def init_models(db):
        db.metadata._add_table('user', None, models.User.__table__)

    @staticmethod
    def init_views(app):
        bp = Blueprint('eve', __name__, url_prefix=app.config['EVE_URL_PREFIX'])
        bp.add_url_rule(rule='/authorize', endpoint='authorize', view_func=views.authorize)
        bp.add_url_rule(rule='/callback', endpoint='callback', view_func=views.callback)
        bp.add_url_rule(rule='/logout', endpoint='logout', view_func=views.logout)
        app.register_blueprint(bp)

    @staticmethod
    def init_context(app):
        def inject_user():
            return dict(user=utils.get_user())
        app.template_context_processors[None].append(inject_user)
