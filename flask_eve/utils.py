import base64
import json
import secrets
import time
import urllib.parse
import urllib.request

from flask import abort, current_app, request

from flask_eve import models


class AnonymousUser:
    name = 'Anonymous'
    character_id = 1

    @property
    def is_authenticated(self):
        return False

    @staticmethod
    def portrait_url(size=512):
        if size not in [64, 128, 256, 512]:
            raise ValueError("Portrait size must be one of [64, 128, 256, 512]")
        return f'https://images.evetech.net/characters/1/portrait?tenant=tranquility&size={size}'


def get_user():
    """Return anonymous user if no session_id or dangling session_id"""

    session_id = request.cookies.get(current_app.config['EVE_SESSION_COOKIE_NAME'])
    if not session_id:
        return AnonymousUser()
    db = current_app.extensions['sqlalchemy'].db
    user = db.session.query(models.User).filter_by(session_id=session_id).first()
    if not user:
        return AnonymousUser()
    return user


def user_from_jwt(jwt, session_id: str = None):
    session_id = session_id or secrets.token_urlsafe(64)
    name, character_id = parse_access_token(jwt['access_token'])
    user = models.User(
        expires_at=int(time.time()) + jwt['expires_in'],
        token_type=jwt['token_type'],
        refresh_token=jwt['refresh_token'],
        access_token=jwt['access_token'],
        name=name,
        character_id=character_id,
        session_id=session_id,
    )
    return user


def parse_access_token(access_token):
    header, payload, signature = access_token.split('.')
    payload = base64.b64decode(payload + '==')
    payload = json.loads(payload)
    character_name = payload['name']
    character_id = payload['sub'].split(':')[2]
    return character_name, character_id


def request_jwt(url, data, headers):
    r = urllib.request.Request(
        url=url,
        data=urllib.parse.urlencode(data).encode(),
        headers=headers,
        method='POST'
    )
    response = urllib.request.urlopen(r)
    content = json.loads(response.read())
    response.close()
    return content


def validate_request_state():
    returned_state = request.args.get('state')
    sent_state = request.cookies.get(current_app.config['EVE_STATE_COOKIE_NAME'])
    if returned_state != sent_state:
        abort(400)
