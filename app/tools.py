import logging
logger = logging.getLogger(__name__)

import requests, os
from datetime import datetime
from bs4 import BeautifulSoup

def get_news():
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

    return articles

def get_weather(city_url="https://www.yr.no/place/United_Kingdom/Scotland/Edinburgh/forecast.xml"):
    """Gets forecast data dict for city_url (from https://www.yr.no/.*/forecast.xml)"""

    r = requests.get(city_url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    forecast = soup.findAll('time')
    data = {}
    for i in range(4): ## Change depending on time of pull (range(1,5) for 6AM today till 6AM tomorrow?)
        x = forecast[i]
        date_from = datetime.strptime(x['from'], "%Y-%m-%dT%H:%M:%S")
        date_to = datetime.strptime(x['to'], "%Y-%m-%dT%H:%M:%S")
        date = "{}".format(date_from.strftime("%I %p")).lstrip("0")
        data[date] = {
            'symbol': x.find('symbol')['name'],
            'icon': x.find('symbol')['var'],
            'precip': x.find('precipitation')['value'],
            'temp': x.find('temperature')['value'],
            'wind': x.find('windspeed')['name'],
            'pressure': x.find('pressure')['value']
        }
    return data
