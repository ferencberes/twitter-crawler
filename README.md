# twitter-crawler
 
 [![Documentation Status](https://readthedocs.org/projects/twittercrawler/badge/?version=latest)](https://twittercrawler.readthedocs.io/en/latest/?badge=latest)

`twittercrawler` is a simple Python crawler on top of the popular [Twython](https://twython.readthedocs.io/en/latest/) package. The main objective during development was to provide an API that ease Twitter data collection for events that span across several days. The key features of this package are as follows:

- collect tweets over several days (online or offline)
- respect Twitter API [rate limits](https://developer.twitter.com/en/docs/basics/rate-limits) during search
- search for people
- collect friend or follower network
- export search results to MongoDB collections (or files)
   
**Detailed documentation:** https://twittercrawler.readthedocs.io/en/latest/

# How to deploy?

## Requirements

This package was developed in Python 3.5 (conda environment) but it works with Python 3.6 and 3.7 as well.

## Install

```bash
pip install .
```

## Twitter API keys

In order to run examples and test scripts you must create a JSON file (named "api_key.json") in the root of the repository with following content:

```
{
  "api_key":"YOUR_API_KEY",
  "api_secret":"YOUR_API_SECRET",
  "access_token":"YOUR_ACCESS_TOKEN",
  "access_token_secret":""YOUR_ACCESS_TOKEN_SECRET"
}
```
You can make your own Twitter API key [here](https://dev.twitter.com/apps/new).

## Run Tests

```bash
cd tests
py.test
```

# Examples

- [Recursive search](examples/recursive.py)
- [Stream search](examples/stream.py)
- [People search](examples/people.py)
