"""
bbc_ccy

Finding out whether the BBC is less likely to report large positive moves than large negative moves
in a currency rate e.g. GBP/USD
"""

# standard library imports
from pathlib import Path

# third party imports
import pandas as pd
import tweepy
import yaml

CONFIG = yaml.safe_load(open('config.yml', 'r'))


def start_api():
    auth = tweepy.OAuthHandler(consumer_key=CONFIG['twitter_login']['consumer_key'],
                               consumer_secret=CONFIG['twitter_login']['consumer_secret'])
    auth.set_access_token(key=CONFIG['twitter_login']['access_key'],
                          secret=CONFIG['twitter_login']['access_secret'])
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

    api = start_api()
    tweets = api.search(q=' OR '.join(keywords))
    return [tweet for tweet in tweets]


if __name__ == '__main__':
    file = Path('data/GBP_USD Historical Data.csv')
    df = pd.read_csv(open(file, 'r', encoding='utf8'))

    # data cleansing
    df = df.rename(columns={'Change %': 'Change'})
    df['Change'] = df['Change'].str.rstrip('%').astype('float') / 100.0
    df['AbsChange'] = df['Change'].abs()

    threshold = 0.03
    df = df[df['AbsChange'] > threshold]

    df['tweets'] = df['Date'].apply(lambda x: len(search_tweets(x)))
    print(df)
