# BBC CCY

Does BBC News reporting affect currency moves?

## Quick start

1. Create `.env` and provide the required keys etc - see below.
2. Run `uv run bbc-ccy`

## .env requirements

```shell
# fixer.io API key
FIXER_KEY=add_your_key_here
# twitter API credentials (deprecated?)
TWITTER_CONSUMER_KEY=add_your_key_here
TWITTER_CONSUMER_SECRET=add_your_key_here
TWITTER_ACCESS_KEY=add_your_key_here
TWITTER_ACCESS_SECRET=add_your_key_here
# Google Programmable Search API key, and ID for custom search of bbc.com
GOOGLE_CUSTOM_SEARCH_KEY=add_your_key_here
GOOGLE_CUSTOM_SEARCH_ID=add_your_key_here
```
