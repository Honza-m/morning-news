import logging
logger = logging.getLogger(__name__)

from app import app
from flask import render_template
from flask_security import login_required, current_user

@app.route('/')
def index():
    from app import tools
    try:
        articles = tools.get_news()
        weather = tools.get_weather()
    except Exception as e:
        return str(e)

    return render_template('index.html',
                           articles=articles,
                           weather=weather,
                           weather_city='Edinburgh') #This is to change according to user settings

@app.route('/dash')
@login_required
def dash():
    return "Welcome, {}".format(current_user.name)
