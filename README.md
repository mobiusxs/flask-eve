# Flask Eve

Eve Online SSO authentication extension for Flask

## Installation

```shell
pip install flask-eve
```

## Requires
1. Python >= 3.7
1. Flask
1. SQLAlchemy
1. Requests

## Quickstart

app.py

```python
from flask import Flask
from flask_eve import Eve
from flask_sqlalachemy import SQLAlchemy

app = Flask(__name__)
app.config.update({
    'EVE_CLIENT_ID': '<your client id>',
    'EVE_SCOPES': '<your scopes>',
    'EVE_SECRET_KEY': '<your secret key>',
})
db = SQLAlchemy(app)
eve = Eve(app, db)
```

index.html

```html
{% if user.is_authenticated %}
  <a href="{{ url_for('eve.logout') }}">Logout</a>
{% else %}
  <a href="{{ url_for('eve.authorize') }}">Authorize</a>
{% endif %}
```
