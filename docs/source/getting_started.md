# Getting started

## Introduction

`twittercrawler` is a simple Python crawler on top of the popular [Twython](https://twython.readthedocs.io/en/latest/) package. The main objective during development was to provide an API that ease Twitter data collection for events that span across multiple days. The key features of this package are as follows:

- collect tweets over several days (online or offline)
- respect Twitter API [rate limits](https://developer.twitter.com/en/docs/twitter-api/v1/rate-limits) during search
- search for people
- collect friend or follower network
- easily export search results to multiple output channels (File, Socket, Kafka queues)

## Install

```bash
git clone https://github.com/ferencberes/twitter-crawler.git
cd twitter-crawler
python setup.py install
```

**NOTE:** If you want to push the collected data to Kafka queues then you need to execute a few additional [steps](https://github.com/ferencberes/twitter-crawler/tree/master/resources).

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

## Examples

### a.) Quickstart

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

### b.) Streaming example

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

With a few modifications (e.g. socket programming) the collected Twitter data can be transformed into a **[graph stream](ehttps://github.com/ferencberes/twitter-crawler/tree/master/examples/graph_streamS)**.

## Run tests

Before executing the provided tests make sure to prepare your Twitter API keys.

```bash
python setup.py test
```