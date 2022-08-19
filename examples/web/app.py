from flask import Flask


def create_app(config: str = 'web.settings'):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    return app


def register_extensions(app: Flask):
    from .extensions import db, eve, migrate
    db.init_app(app)
    migrate.init_app(app, db)
    eve.init_app(app, db)


def register_blueprints(app: Flask):
    from . import private
    from . import public
    app.register_blueprint(private.routes)
    app.register_blueprint(public.routes)
