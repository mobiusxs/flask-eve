from base64 import b64decode
from json import loads
from secrets import token_urlsafe
from time import time

from flask import current_app
from flask import request

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
    session_id = session_id or token_urlsafe(64)
    name, character_id = parse_access_token(jwt['access_token'])
    user = models.User(
        expires_at=int(time()) + jwt['expires_in'],
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
    payload = b64decode(payload + '==')
    payload = loads(payload)
    character_name = payload['name']
    character_id = payload['sub'].split(':')[2]
    return character_name, character_id
