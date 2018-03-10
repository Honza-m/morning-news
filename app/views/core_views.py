import logging
logger = logging.getLogger(__name__)
from app import app
from flask import render_template
from flask_security import login_required, current_user


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dash')
@login_required
def dash():
    return "Welcome, {}".format(current_user.name)
