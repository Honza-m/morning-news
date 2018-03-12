import logging
logger = logging.getLogger(__name__)

from app import app
from flask import render_template
from flask_security import login_required, current_user

import requests, os

@app.route('/')
def index():
    params = {
        'apiKey': os.environ['NEWSAPI'],
        'country': 'gb'
    }
    r = requests.get("https://newsapi.org/v2/top-headlines", params=params)
    articles = [x for x in r.json().get('articles',[])]
    for article in articles:
        if article.get('publishedAt'):
            article['publishedAt'] = datetime.strptime(
                            article.get('publishedAt'),
                            '%Y-%m-%dT%H:%M:%SZ').strftime('%d %B %Y - %H:%M')

    return render_template('index.html', articles=articles)

@app.route('/dash')
@login_required
def dash():
    return "Welcome, {}".format(current_user.name)
