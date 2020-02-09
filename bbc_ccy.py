"""
bbc_ccy

Finding out whether the BBC is less likely to report large positive moves than large negative moves
in a currency rate e.g. GBP/USD
"""

# standard library imports
import csv
import datetime as dt
import json
import logging
from pathlib import Path

# third party imports
import pandas as pd
import requests
import tweepy
import yaml

CONFIG = yaml.safe_load(open('config.yml', 'r'))


def analyse_rate_history():
    df = load_rate_data()
    df = cleanse(df)
    df = filter_data(df)
    df['tweets'] = df['Date'].apply(lambda x: len(search_tweets(x)))
    print(df)


def cleanse(df_in):
    # data cleansing
    df_out = df_in.rename(columns={'Change %': 'Change'})
    df_out['Change'] = df_out['Change'].str.rstrip('%').astype('float') / 100.0
    df_out['AbsChange'] = df_out['Change'].abs()
    return df_out


def load_rate_data():
    file = Path('data/GBP_USD Historical Data.csv')
    df_raw = pd.read_csv(open(file, 'r', encoding='utf8'))
    return df_raw


def filter_data(df_in):
    threshold = 0.03
    df_out = df_in[df_in['AbsChange'] > threshold]
    return df_out


def inter_day_change(date_1):
    date_0 = date_1 + dt.timedelta(days=-1)

    rates = {}
    for date in [date_0, date_1]:
        params = {'key': CONFIG['fixer.io']['key'],
                  'symbols': 'GBP',
                  'date': date.strftime('%Y-%m-%d')}
        uri = 'http://data.fixer.io/api/{date}?access_key={key}&symbols={symbols}&format=1'
        r = requests.get(uri.format(**params))
        if r.status_code != 200:
            raise requests.HTTPError(r.json()['message'])
        content = r.json()
        rates[date] = 1 / content['rates']['GBP']

    change = rates[date_1] - rates[date_0]
    logging.info(f'{date_0} to {date_1} {rates[date_1]:0.5f}-{rates[date_0]:0.5f} = {change:0.5f}')
    return change


def twitter_api():
    auth = tweepy.OAuthHandler(consumer_key=CONFIG['twitter']['consumer_key'],
                               consumer_secret=CONFIG['twitter']['consumer_secret'])
    auth.set_access_token(key=CONFIG['twitter']['access_key'],
                          secret=CONFIG['twitter']['access_secret'])
    return tweepy.API(auth)


def search_tweets():
    """
    Searches for tweets on a given date - but the API only goes back 7 days so this needs
    to be changed to screen scraping
    :return: a list of tweets
    """
    handle = 'BBCBusiness'
    keywords = ['GBP', 'Pound', 'Sterling']

    api = twitter_api()
    tweets = api.search(q=' OR '.join(keywords))
    return [tweet for tweet in tweets]


def search_stories():
    search_words = ['pound', 'euro']
    params = {'key': CONFIG['google']['key'],
              'cx': CONFIG['google']['cx'],
              'q': ' '.join([f'"{word}"' for word in search_words]),
              'dateRestrict': 'd2'
              }
    param_str = '&'.join([f'{k}={v}' for k, v in params.items()])
    uri = 'https://www.googleapis.com/customsearch/v1/siterestrict?' + param_str
    print(uri)
    r = requests.get(uri)
    if r.status_code != 200:
        raise requests.HTTPError(r.json()['message'])
    hits = r.json()
    json.dump(hits, open('data.json', 'w'))
    stories = hits.get('items', [])
    for story in stories:
        if 'Market data: FTSE 100, Pound/\nDollar, Pound/Euro, US markets, Oil prices.' in story['snippet']:
            score = sum(story['title'].lower().count(word) for word in search_words)
            if score == 0:
                stories.remove(story)
    return stories


if __name__ == '__main__':
    logging.basicConfig(filename='bbc_ccy.log', level=logging.DEBUG)

    results = {'date': dt.date.today(),
               'rate_change': inter_day_change(dt.date.today() + dt.timedelta(days=-1)),
               'stories_count': len(search_stories())}

    writer = csv.DictWriter(open('bbc_ccy.csv', 'w+'), fieldnames=results.keys())
    writer.writerow(results)
