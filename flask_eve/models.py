from base64 import urlsafe_b64encode
from time import time

from flask import current_app
from requests import post
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    modified = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def save(self):
        db = current_app.extensions['sqlalchemy'].db
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db = current_app.extensions['sqlalchemy'].db
        db.session.delete(self)
        db.session.commit()


class User(BaseModel):
    session_id = Column(String(512))
    expires_at = Column(Integer)
    token_type = Column(String(512))
    refresh_token = Column(String(512))
    access_token = Column(String(512))
    name = Column(String(512))
    character_id = Column(Integer)

    @property
    def is_authenticated(self):
        return bool(self.session_id)

    def portrait_url(self, size=512):
        if size not in [64, 128, 256, 512]:
            raise ValueError("Portrait size must be one of [64, 128, 256, 512]")
        return f'https://images.evetech.net/characters/{self.character_id}/portrait?tenant=tranquility&size={size}'

    def refresh_access_token(self):
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'scope': current_app.config['EVE_SCOPES'],
        }
        auth_string = f"{current_app.config['EVE_CLIENT_ID']}:{current_app.config['EVE_SECRET_KEY']}".encode('utf-8')
        encoded_auth_string = urlsafe_b64encode(auth_string).decode()
        headers = {
            'Authorization': f'Basic {encoded_auth_string}',
        }
        sso_response = post(url='https://login.eveonline.com/v2/oauth/token', data=data, headers=headers)
        sso_response.raise_for_status()
        jwt = sso_response.json()
        self.expires_at = int(time()) + jwt['expires_in']
        self.token_type = jwt['token_type']
        self.access_token = jwt['access_token']
        self.refresh_token = jwt['refresh_token']

    def get_auth_header(self):
        if self.expires_at < time():
            self.refresh_access_token()
        return {
            'Authorization': f'Bearer {self.access_token}'
        }
