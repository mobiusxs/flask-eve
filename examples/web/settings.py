from os import environ

SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
SQLALCHEMY_TRACK_MODIFICATIONS = False

EVE_URL_PREFIX = '/auth'
EVE_SESSION_COOKIE_NAME = 'eve_session'
EVE_STATE_COOKIE_NAME = 'eve_state'
EVE_CALLBACK_URL = 'http://localhost/auth/callback'
EVE_CLIENT_ID = environ['EVE_CLIENT_ID']
EVE_SCOPES = environ['EVE_SCOPES']
EVE_SECRET_KEY = environ['EVE_SECRET_KEY']
EVE_LOGIN_REDIRECT_URL = 'private.index'
EVE_LOGOUT_REDIRECT_URL = 'public.index'
