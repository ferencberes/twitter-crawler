# Getting started

## Introduction

`twittercrawler` is a simple Python crawler on top of the popular [Twython](https://twython.readthedocs.io/en/latest/) package. The main objective during development was to provide an API that ease Twitter data collection for events that span across several days. The key features of this package are as follows:

- collect tweets over several days (online or offline)
- respect Twitter API [rate limits](https://developer.twitter.com/en/docs/basics/rate-limits) during search
- search for people
- collect friend or follower network
- export search results to MongoDB collections (or files)

## Requirements

This package was developed in Python 3.5 (conda environment) but it works with Python 3.6 and 3.7 as well.

## Install

```bash
git clone https://github.com/ferencberes/twitter-crawler.git
cd twitter-crawler
pip install .
```

## Twitter API keys

In order to use this package you must create a JSON file (called `api_key.json` in the examples) containing your Twitter API credentials.

```
{
  "api_key":"YOUR_API_KEY",
  "api_secret":"YOUR_API_SECRET",
  "access_token":"YOUR_ACCESS_TOKEN",
  "access_token_secret":"YOUR_ACCESS_TOKEN_SECRET"
}
```

You can make your own Twitter API key [here](https://dev.twitter.com/apps/new).

## First example

Execute the following code to see whether your Twitter API key configuration works.


```python
from twittercrawler.crawlers import InteractiveCrawler

# initialize
interactive = InteractiveCrawler()
interactive.authenticate("PATH_TO_API_KEY_JSON")

# set query parameters
search_params = {
    "q":"#BREAKING",
    "result_type":'recent',
    "count":10
}
interactive.set_search_arguments(search_args=search_params)

# search
res = interactive.search()

print("Number of tweets: %i" % len(res["statuses"]))
print(res["statuses"][0]["text"])

# close
interactive.close()
```

If your configuration works then you should proceed to the detailed [documentation](crawler_docs) of implemented crawlers.

## Run tests

**In order to run test scripts you must place the `api_key.json` file in the root of the repository.**

```bash
cd tests
py.test
```