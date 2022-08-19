import base64
import json
import secrets
import urllib.parse
import urllib.request

from flask import abort, current_app, make_response, redirect, request, url_for

from flask_eve import models, utils
from flask_eve.decorators import authentication_required


def authorize():
    state = secrets.token_urlsafe(64)
    data = {
        'response_type': 'code',
        'redirect_uri': current_app.config['EVE_CALLBACK_URL'],
        'client_id': current_app.config['EVE_CLIENT_ID'],
        'scope': current_app.config['EVE_SCOPES'],
        'state': state
    }
    location = f'https://login.eveonline.com/v2/oauth/authorize/?{urllib.parse.urlencode(data)}'
    response = make_response(redirect(location=location, code=302))
    response.set_cookie(current_app.config['EVE_STATE_COOKIE_NAME'], state)
    response.set_cookie(current_app.config['EVE_SESSION_COOKIE_NAME'], '', expires=0)
    return response


def callback():
    utils.validate_request_state()
    code = request.args.get('code')
    url, data, headers = build_jwt_request(code)
    jwt = utils.request_jwt(url, data, headers)
    user = utils.user_from_jwt(jwt)
    user.save()
    response = make_response(redirect(url_for(current_app.config['EVE_LOGIN_REDIRECT_URL'])))
    response.set_cookie(current_app.config['EVE_STATE_COOKIE_NAME'], '', expires=0)
    response.set_cookie(current_app.config['EVE_SESSION_COOKIE_NAME'], user.session_id)
    return response


def build_jwt_request(code: str):
    url = 'https://login.eveonline.com/v2/oauth/token'
    data = {
        'grant_type': 'authorization_code',
        'code': code
    }
    auth_string = f"{current_app.config['EVE_CLIENT_ID']}:{current_app.config['EVE_SECRET_KEY']}".encode('utf-8')
    encoded_auth_string = base64.urlsafe_b64encode(auth_string).decode()
    headers = {
        'Authorization': f'Basic {encoded_auth_string}'
    }
    return url, data, headers


@authentication_required
def logout():
    session_id = request.cookies.get(current_app.config['EVE_SESSION_COOKIE_NAME'])
    if session_id:
        db = current_app.extensions['sqlalchemy'].db
        user = db.session.query(models.User).filter_by(session_id=session_id).first()
        if user:
            user.delete()
    response = make_response(redirect(url_for(current_app.config['EVE_LOGOUT_REDIRECT_URL'])))
    response.set_cookie(current_app.config['EVE_STATE_COOKIE_NAME'], '', expires=0)
    response.set_cookie(current_app.config['EVE_SESSION_COOKIE_NAME'], '', expires=0)
    return response
