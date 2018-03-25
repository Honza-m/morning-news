import logging
logger = logging.getLogger(__name__)

import requests, os, math
from datetime import datetime
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError

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

class News:
    def __init__(self):
        self.articles_per_page = 25
        self.ALLOWED_ENDPOINTS = ['top-headlines','everything']
        self.ALLOWED = {'country': ['ae','ar','at','au','be','bg','br',
                                     'ca','ch','cn','co','cu','cz','de',
                                     'eg','fr','gb','gr','hk','hu','id',
                                     'ie','il','in','it','jp','kr','lt',
                                     'lv','ma','mx','my','ng','nl','no',
                                     'nz','ph','pl','pt','ro','rs','ru',
                                     'sa','se','sg','si','sk','th','tr',
                                     'tw','ua','us','ve','za',None],
                        'category': ['business','entertainment','general',
                                     'health','science','sports',
                                     'technology',None],
                        'language': ['ar','de','en','es','fr','he','it',
                                     'nl','no','pt','ru','se','ud','zh',
                                     None],
                        'sort': ['relevancy','popularity','publishedAt',
                                 None]
                       }


    def _execute(self, endpoint, params):
        #argcheck
        if endpoint not in self.ALLOWED_ENDPOINTS:
            raise ValueError("Endpoint '{}' not allowed. "
                             "Choose from these: '{}'".format(
                              endpoint, ", ".join(self.ALLOWED_ENDPOINTS)))
        for param in ['country','category','language']:
            if params.get('param') not in self.ALLOWED[param]:
                raise ValueError("'{}' not allowed for {} parameter. "
                                 "Choose from '{}'".format(
                                 params[param],
                                 ", ".join(self.ALLOWED[param])
                                 ))

        #add max available page size
        params = {'pageSize': self.articles_per_page, **params}
        params = {x: params[x] for x in params if x}

        #execute
        repeat_counter = 0
        while True:
            try:
                r = requests.get("https://newsapi.org/v2/{}".format(endpoint),
                                 headers={'x-api-key': os.environ['NEWSAPI']},
                                 params=params)
                r.raise_for_status()
                break

            except HTTPError as e:
                if r.status_code in [429,500]:
                    #repeat
                    if repeat_counter < 3:
                        repeat_counter += 1
                        continue
                    else:
                        raise e
                elif r.status_code == 400:
                    #bad request
                    raise ValueError("{}".format(r.json().get('message')))
                else:
                    raise e

        total_pages = math.ceil(r.json().get(
                                    'totalResults',0) / self.articles_per_page)
        if total_pages * self.articles_per_page >= 10000:
            total_pages = math.floor(9999/self.articles_per_page)
        articles = [x for x in r.json().get('articles',[])]
        for article in articles:
            if article.get('publishedAt'):
                try:
                    article['publishedAt'] = datetime.strptime(
                            article.get('publishedAt'),
                            '%Y-%m-%dT%H:%M:%SZ').strftime('%d %B %Y - %H:%M')
                except:
                    article['publishedAt'] = None

        self.result = {'articles': articles,
                       'page_n': params.get('page',1),
                       'total_pages': total_pages}

    def top_headlines(self,
                      country=None,
                      category=None,
                      sources=None,
                      q=None,
                      page=1):
        #argcheck
        if (country and sources) or (category and sources):
            raise TypeError("Sources parameter can't be mixed with "
                            "country or category parameters.")
        if not country and not category and not sources:
            raise ValueError("Please provide a country argument if other "
                             "arguments are left empty.")
        if not isinstance(page, int):
            raise TypeError("The page argument must be an integer.")

        self._execute("top-headlines",
                      {'country': country,
                       'category': category,
                       'sources': sources,
                       'q': q,
                       'page': page}
                     )
        return self.result

    def everything(self,
                   q,
                   sources=None,
                   domains=None,
                   from_time=None,
                   to_time=None,
                   language=None,
                   sort_by=None,
                   page=1):

        #CREATE ARGCHECK HERE
        self._execute("everything",
                      {'q': q,
                       'sources': sources,
                       'domains': domains,
                       'from': from_time,
                       'to': to_time,
                       'language': language,
                       'sortBy': sort_by,
                       'page': page})
        return self.result
