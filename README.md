# twitter-crawler

[![Documentation Status](https://readthedocs.org/projects/twittercrawler/badge/?version=latest)](https://twittercrawler.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/ferencberes/twitter-crawler/branch/master/graph/badge.svg?token=KS3I66GFLB)](https://codecov.io/gh/ferencberes/twitter-crawler)

`twittercrawler` is a simple Python crawler on top of the popular [Twython](https://twython.readthedocs.io/en/latest/) package. The main objective during development was to provide an API that ease Twitter data collection for events that span across several days. The key features of this package are as follows:

- collect tweets over several days (online or offline)
- respect Twitter API [rate limits](https://developer.twitter.com/en/docs/basics/rate-limits) during search
- search for people
- collect friend or follower network
- easily export search results to multiple output channels
   
**Detailed documentation:** https://twittercrawler.readthedocs.io/en/latest/

# How to deploy?

## Requirements

This package was developed in Python 3.5 (conda environment) but it works with Python 3.6 and 3.7 as well.

## Install

```bash
git clone https://github.com/ferencberes/twitter-crawler.git
cd twitter-crawler
python setup.py install
```

## Twitter API keys

You must provide your Twitter API credentials to collect data from Twitter. First, generate your Twitter API keys on the [Twitter developer portal](https://developer.twitter.com). Then, choose from the available options to configure your crawler. 

### a.) Environmental variables

- Set the following environmental variables:

```bash
export API_KEY="YOUR_API_KEY";
export API_SECRET="YOUR_API_SECRET";
export ACCESS_TOKEN="YOUR_ACCESS_TOKEN";
export ACCESS_TOKEN_SECRET="YOUR_ACCESS_TOKEN_SECRET";
```

- Authenticate your crawler:

```python
from twittercrawler.crawlers import StreamCrawler
crawler = StreamCrawler()
crawler.authenticate()
...
```

### b.) JSON configuration file

- Create a JSON file (e.g. "api_key.json") in the root folder with the following content:

```
{
  "api_key":"YOUR_API_KEY",
  "api_secret":"YOUR_API_SECRET",
  "access_token":"YOUR_ACCESS_TOKEN",
  "access_token_secret":"YOUR_ACCESS_TOKEN_SECRET"
}
```

- Authenticate your crawler:

```python
from twittercrawler.crawlers import StreamCrawler
crawler = StreamCrawler()
crawler.authenticate("PATH_TO_JSON_FILE")
...
```

## Run Tests

```bash
pip install .[test]
python setup.py test
```

# Examples

## Notebook

- [Quick example](examples/SimpleSearch.ipynb)

## Scripts
- [Recursive search](examples/recursive.py)
- [Stream search](examples/stream.py)
- [People search](examples/people.py)
