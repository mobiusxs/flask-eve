from functools import wraps

from flask import redirect, url_for

from flask_eve import utils


def authentication_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = utils.get_user()
        if user.is_authenticated:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('eve.authorize'))
    return decorated_function
