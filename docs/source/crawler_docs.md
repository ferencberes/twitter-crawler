# Crawler documentation

The general Twitter Search API provides several [endpoints](https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/overview) that can be used for data collection. However you must take care of [windowing](https://developer.twitter.com/en/docs/tweets/timelines/guides/working-with-timelines) and [rate limits](https://developer.twitter.com/en/docs/twitter-api/v1/rate-limits) if you intend to crawl tweets for several days. Here is where `twittercrawler`  comes in. It provides multiple crawler objects that are designed to ease your Twitter data collection.

## a.) Search for events

### RecursiveCrawler

`RecursiveCrawler` is the best choice for collecting tweets from a specific time in the past up to the current timestamp. It is important to note that your accessibility to past tweets is based on your [Twitter API pricing plan](https://developer.twitter.com/en/pricing/search-30day).

In the example below all tweets are collected from the last 5 minutes that contain the #bitcoin or #ethereum hashtags. The collected data is exported to `recursive_results.txt`.

```python
from twittercrawler.crawlers import RecursiveCrawler
from twittercrawler.data_io import FileWriter, FileReader
from twittercrawler.search import get_time_termination, get_id_termination
import datetime, time

# initialize
file_path = "recursive_results.txt"
recursive = RecursiveCrawler()
recursive.authenticate("PATH_TO_API_KEY_JSON")
recursive.connect_output([FileWriter(file_path, clear=True)])

# query
search_params = {
    "q":"#bitcoin OR #ethereum",
    "result_type":'recent',
    "count":100
}
recursive.set_search_arguments(search_args=search_params)

# termination (collect tweets from the last 5 minutes)
now = datetime.datetime.now()
time_str = (now-datetime.timedelta(seconds=300)).strftime("%a %b %d %H:%M:%S +0000 %Y")
print(time_str)
time_terminator =  get_time_termination(time_str)

# run search
success, max_id, latest_id, cnt = recursive.search(term_func=time_terminator)
print(success, max_id, latest_id, cnt)

# close
recursive.close()

# load results
results_df = FileReader(file_path).read()
print("\nTotal hits:", len(results_df))
print(results_df.loc[0])
```

### Terminating the search

In the previous example thehttps://developer.twitter.com/en/pricing/search-30day `RecursiveCrawler` terminated when it collected every tweet from the last 5 minutes. But termination can be linked to a given tweet (based on its id) as well.

In the next example there are two stages. The first stage is identical to the previous example (terminate by time using the `get_time_termination` function). Then after a 5 minute pause, the second stage collects only the new tweets using the `get_id_termination` function. Note that `latest_id` variable contains the latest tweet's id from the first stage.

```python
from twittercrawler.crawlers import RecursiveCrawler
from twittercrawler.data_io import FileWriter, FileReader
from twittercrawler.search import get_time_termination, get_id_termination
import datetime, time

# initialize
file_path = "recursive_results.txt"
recursive = RecursiveCrawler()
recursive.authenticate("PATH_TO_API_KEY_JSON")
recursive.connect_output([FileWriter(file_path, clear=True)])

# query
search_params = {
    "q":"#bitcoin OR #ethereum OR blockchain",
    "result_type":"recent",
    "lang":"en",
    "count":100
}
recursive.set_search_arguments(search_args=search_params)

# termination (collect tweets from the last 5 minutes)
now = datetime.datetime.now()
time_str = (now-datetime.timedelta(seconds=300)).strftime("%a %b %d %H:%M:%S +0000 %Y")
print(time_str)
time_terminator =  get_time_termination(time_str)

# run search - FIRST STAGE
success, max_id, latest_id, cnt = recursive.search(term_func=time_terminator)
print("\nFirst stage report:")
print(success, max_id, latest_id, cnt)

# wait for 5 minutes
print("\nSleeping for 5 minutes...")
time.sleep(5*60)

# NEW termination (collect only new tweets)
id_terminator =  get_id_termination(latest_id)

# NEW search - SECOND STAGE
success, new_max_id, new_latest_id, new_cnt = recursive.search(term_func=id_terminator)
print("\nSecond stage report:")
print(success, new_max_id, new_latest_id, new_cnt)

# close
recursive.close()

# load results
results_df = FileReader(file_path).read()
print("\nTotal hits:", len(results_df))
print(results_df.loc[0])
```

### StreamCrawler

`StreamCrawler` provides a much more sophisticated way to collect data online rather than calling `RecursiveCrawler` repeatedly with different termination functions.

```python
from twittercrawler.crawlers import StreamCrawler
from twittercrawler.data_io import FileWriter, SocketWriter
from twittercrawler.search import get_time_termination
import datetime

# prepare writers
file_path = "stream_results.txt"
fw = FileWriter(file_path, clear=True)
sw = SocketWriter(7000, include_mask=["created_at","full_text"])
```

This example shows that it is possible to connect multiple data writers to the same crawler. For example you might want to read retweets and mentions in different sockets or Kafka queues. In our case we export
- the original tweets, with all meta data, to a file AND
- send only the timestamp and the tweet text to a socket

**It is important to** note that in case of sockets, the program execution only moves forward if you **create a client** that receives the messages. For example, you can observe the collected tweets in a console:

```bash
telnet localhost 7000
```

Data collection will commence after the socket connection is ready. In this example `StreamCrawler` collects tweets from the last minute then continues the search online. Note that manual termination is needed for this crawler object.

```python
# initialize crawler
stream = StreamCrawler()
stream.authenticate("PATH_TO_API_KEY_JSON")
stream.connect_output([fw, sw])

# query
search_params = {
    "q":"#bitcoin OR #ethereum OR blockchain OR crypto",
    "result_type":"recent",
    "lang":"en",
    "count":100
}
stream.set_search_arguments(search_args=search_params)

# termination (collect tweets from the last 5 minutes - THEN continue online)
now = datetime.datetime.now()
time_str = (now-datetime.timedelta(seconds=300)).strftime("%a %b %d %H:%M:%S +0000 %Y")
print(time_str)
time_terminator =  get_time_termination(time_str)

# run search (after collecting latest tweets sleep for 15 seconds)
stream.search(15, time_terminator) # YOU MUST TERMINATE THIS SEARCH MANUALLY!
```

## b.) Search for user data

`twittercrawler` enables you to crawl up to date information (meta data, friends, followers) on any Twitter user. Unfortunately, rate limits are much lower for these queries than for event search. Thus you have to plan your user searches carefully (especially for follower queries).

### PeopleCrawler

`PeopleCrawler` enables you to collect Twitter accounts that are related to a given set of keywords.
For example, here we search for phd student in the field of data science. Then, only the name, location and description are export for each account. 

```python
from twittercrawler.crawlers import PeopleCrawler
from twittercrawler.data_io import FileWriter, FileReader

# prepare writers
keys = ["name","location","description"]
file_path = "people_results.txt"
fw = FileWriter(file_path, clear=True, include_mask=keys)

# initialize
people = PeopleCrawler()
people.authenticate("PATH_TO_API_KEY_JSON")
people.connect_output([fw])

# query
search_params = {
    "q":"data scientist AND phd student"
}
people.set_search_arguments(search_args=search_params)

# run search
page, cnt = people.search()
print(page, cnt)

# close
people.close()

#load results
results_df = FileReader(file_path).read()
print("Hits:", len(results_df))
print(results_df.loc[0])
```

### Friends and followers

`FriendsCollector` and `FollowersCollector` are designed to easily collect friends or followers for  given users. Note that for the users of interest you must provide their `id` (not their `screen_name`).

```python
from twittercrawler.crawlers import FriendsCollector
from twittercrawler.data_io import FileWriter

# initialize
friends = FriendsCollector()
friends.authenticate("PATH_TO_API_KEY_JSON")
friends.connect_to([FileWriter("friends.txt")])

# run search
user_ids = [...] # list of user ids whose friends you want to collect
user, cursor, cnt = friends.collect(user_ids)
print(user, cursor, cnt)

# close
friends.close()
```