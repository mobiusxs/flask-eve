import pytest
from flask import Flask
from flask_eve import Eve
from flask_eve.models import User
from flask_sqlalchemy import SQLAlchemy


@pytest.fixture()
def app():
    app = Flask(__name__)
    app.config.from_object('tests.settings')
    db = SQLAlchemy()
    eve = Eve()

    db.init_app(app)
    eve.init_app(app, db)
    return app


@pytest.fixture()
def db(app):
    return app.extensions['sqlalchemy'].db


@pytest.fixture()
def user():
    def override_refresh_access_token():
        return None
    user = User(
        session_id='session_id',
        expires_at=99999999999,
        token_type='token_type',
        refresh_token='refresh_token',
        access_token='access_token',
        name='name',
        character_id=1234567890,
    )
    user.refresh_access_token = override_refresh_access_token
    return user
