from flask import render_template

from flask_eve import authentication_required


@authentication_required
def index():
    return render_template('private/index.html')
