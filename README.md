# twitter-crawler

[![Documentation Status](https://readthedocs.org/projects/twittercrawler/badge/?version=latest)](https://twittercrawler.readthedocs.io/en/latest/?badge=latest)
![build](https://github.com/ferencberes/twitter-crawler/actions/workflows/main.yml/badge.svg)
[![codecov](https://codecov.io/gh/ferencberes/twitter-crawler/branch/master/graph/badge.svg?token=KS3I66GFLB)](https://codecov.io/gh/ferencberes/twitter-crawler)
![PyPI - Python Version](https://img.shields.io/badge/python-3.6%20|%203.7%20|%203.8%20|%203.9-blue.svg)

`twittercrawler` is a simple Python crawler on top of the popular [Twython](https://twython.readthedocs.io/en/latest/) package. The main objective during development was to provide an API that ease Twitter data collection for events that span across multiple days. The key features of this package are as follows:

- collect tweets over several days (online or offline)
- respect Twitter API [rate limits](https://developer.twitter.com/en/docs/twitter-api/v1/rate-limits) during search
- search for people
- collect friend or follower network
- easily export search results to multiple output channels (File, Socket, Kafka queues)

# How to deploy?

## Install

```bash
git clone https://github.com/ferencberes/twitter-crawler.git
cd twitter-crawler
python setup.py install
```

**NOTE:** If you want to push the collected data to Kafka queues then you need to execute a few additional [steps](resources/).

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
crawler.authenticate("PATH_TO_API_KEY_JSON")
...
```

# Examples

## Tweet streaming example

- Initialize and authenticate the crawler:

```python
from twittercrawler.crawlers import StreamCrawler
stream = StreamCrawler()
stream.authenticate("PATH_TO_API_KEY_JSON")
```

- Connect a FileWriter that will export the collected tweets:

```python
from twittercrawler.data_io import FileWriter
stream.connect_output([FileWriter("stream_results.txt")])
```

- Set search parameters:

```python
search_params = {
    "q":"#bitcoin OR #ethereum OR blockchain",
    "result_type":"recent",
    "lang":"en",
    "count":100
}
stream.set_search_arguments(search_args=search_params)
```

- Initialize a termination function that will collect tweets from the last 5 minutes:

```python
from twittercrawler.search import get_time_termination
import datetime

now = datetime.datetime.now()
time_str = (now-datetime.timedelta(seconds=300)).strftime("%a %b %d %H:%M:%S +0000 %Y")
time_terminator =  get_time_termination(time_str)
```

- Run search:
   - First, tweets from the last 5 minutes are collected
   - Then, new tweets are collected for every 15 seconds
   
```python
try:
    stream.search(15, time_terminator)
except:
    raise
finally:
    stream.close()
```

With a few modifications (e.g. socket programming) the collected Twitter data can be transformed into a **[graph stream](examples/graph_stream)**.

## Load collected data

- Load collected data into a Pandas dataframe

```python
from twittercrawler.data_io import FileReader
results_df = FileReader("stream_results.txt").read()
print(results_df.head())
```

## Crawlers

In this package you can find crawlers for various Twitter data collection tasks. Before executing the provided sample scripts make sure to prepare your Twitter API keys.

- [Recursive search](examples/recursive.py)
- [Stream search](examples/stream.py)
- [People search](examples/people.py)

## Tests

Before executing the provided tests make sure to prepare your Twitter API keys. 

```bash
python setup.py test
```
