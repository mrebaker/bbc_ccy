"""
bbc_ccy

Finding out whether the BBC is less likely to report large positive moves than large negative moves
in a currency rate e.g. GBP/USD
"""

# standard library imports
import datetime as dt
import json
from pathlib import Path

# third party imports
import pandas as pd
import requests
import tweepy
import yaml

CONFIG = yaml.safe_load(open('config.yml', 'r'))


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


def twitter_api():
    auth = tweepy.OAuthHandler(consumer_key=CONFIG['twitter']['consumer_key'],
                               consumer_secret=CONFIG['twitter']['consumer_secret'])
    auth.set_access_token(key=CONFIG['twitter']['access_key'],
                          secret=CONFIG['twitter']['access_secret'])
    return tweepy.API(auth)


def search_tweets(date):
    """
    Searches for tweets on a given date - but the API only goes back 7 days so this needs
    to be changed to screen scraping
    :param date:
    :return: a list of tweets
    """
    handle = 'BBCBusiness'
    keywords = ['GBP', 'Pound', 'Sterling']

    api = twitter_api()
    tweets = api.search(q=' OR '.join(keywords))
    return [tweet for tweet in tweets]


def search_stories(search_date):
    params = {'key': CONFIG['google']['key'],
              'cx': CONFIG['google']['cx'],
              'q': 'Pound+sterling',
              'before': search_date + dt.timedelta(days=2),
              'after': search_date + dt.timedelta(days=-1)
              }
    param_str = '&'.join([f'{k}={v}' for k, v in params.items()])
    uri = 'https://www.googleapis.com/customsearch/v1/siterestrict?' + param_str
    print(uri)
    r = requests.get(uri)
    if r.status_code != 200:
        raise requests.HTTPError(r.json()['message'])
    hits = r.json()
    json.dump(hits, open('data.json', 'w'))
    for hit in hits:
        print(hit)


if __name__ == '__main__':
    search_stories(dt.date(2017, 1, 17))
    # df = load_rate_data()
    # df = cleanse(df)
    # df = filter_data(df)
    # df['tweets'] = df['Date'].apply(lambda x: len(search_tweets(x)))
    # print(df)
