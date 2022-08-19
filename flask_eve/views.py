from base64 import urlsafe_b64encode
from secrets import token_urlsafe
from urllib.parse import urlencode

from flask import abort
from flask import current_app
from flask import make_response
from flask import redirect
from flask import request
from flask import url_for
from requests import post

from flask_eve import models
from flask_eve import utils
from flask_eve.decorators import authentication_required


def authorize():
    state = token_urlsafe(64)
    data = {
        'response_type': 'code',
        'redirect_uri': current_app.config['EVE_CALLBACK_URL'],
        'client_id': current_app.config['EVE_CLIENT_ID'],
        'scope': current_app.config['EVE_SCOPES'],
        'state': state
    }
    location = f'https://login.eveonline.com/v2/oauth/authorize/?{urlencode(data)}'
    response = make_response(redirect(location=location, code=302))
    response.set_cookie(current_app.config['EVE_STATE_COOKIE_NAME'], state)
    response.set_cookie(current_app.config['EVE_SESSION_COOKIE_NAME'], '', expires=0)
    return response


def callback():
    validate_request_state()
    jwt = request_jwt()
    user = utils.user_from_jwt(jwt)
    user.save()
    response = make_response(redirect(url_for(current_app.config['EVE_LOGIN_REDIRECT_URL'])))
    response.set_cookie(current_app.config['EVE_STATE_COOKIE_NAME'], '', expires=0)
    response.set_cookie(current_app.config['EVE_SESSION_COOKIE_NAME'], user.session_id)
    return response


def validate_request_state():
    returned_state = request.args.get('state')
    sent_state = request.cookies.get(current_app.config['EVE_STATE_COOKIE_NAME'])
    if returned_state != sent_state:
        abort(400)


def request_jwt():
    code = request.args.get('code')
    data = {
        'grant_type': 'authorization_code',
        'code': code
    }
    auth_string = f"{current_app.config['EVE_CLIENT_ID']}:{current_app.config['EVE_SECRET_KEY']}".encode('utf-8')
    encoded_auth_string = urlsafe_b64encode(auth_string).decode()
    headers = {
        'Authorization': f'Basic {encoded_auth_string}'
    }
    sso_response = post(url='https://login.eveonline.com/v2/oauth/token', data=data, headers=headers)
    sso_response.raise_for_status()
    return sso_response.json()


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
