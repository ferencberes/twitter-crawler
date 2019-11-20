# twitter-crawler

A simple Python Twitter crawler is implemented in this repository. The crawler can search for events on Twitter with the help of [Twython](https://github.com/ryanmcgrath/twython). The crawled events are inserted into a [MongoDB](https://www.mongodb.com/) collection in order to be more accessible for further analysis.

# How to deploy?

## Requirements

This package was developed in Python 3.5 conda environment.

## Install

```bash
pip install .
```

# Examples

### a.) With file output

You can see a simple example in this [notebook](ipython/SimpleSearch.ipynb) when the collected data is written to a single file.

### b.) With MongoDB connection

You can find detailed usage examples in this jupyter [notebook](ipython/MultipleSearchWithMongoDB.ipynb). Here the collected data is exported to a MongoDB collection.

# Usage

## 1.) API restrictions 

In order to avoid exceeding your Twitter API limit you have to set 2 parameters:

   * **time_frame:** the length of the time interval (in seconds) where you want to limit the number of requests (e.g.: 900 ~ 15 minutes). 
   * **max_requests** the maximum number of requests enabled to the crawler to execute in each **time_frame** seconds (e.g.: 450).

```python
tcs = TwitterCrawler(time_frame=900,max_requests=450)
```

## 2.a) MongoDB connection

**TwitterCrawler** exports the collected events to a MongoDB collection (e.g: "raw"). You can connect to a running MongoDB database the following way:

```python
tcs.connect_to_mongodb("raw", port=27017, db_name='twitter-crawler')
```

## 2.b) Export to file

**TwitterCrawler** can export the collected events to a File as well:

```python
tcs.connect_to_file("sample.txt")
```

If the file already exists then the new content will be appended. It won't be overwritten completely.

## 3.) Authentication

In order to use Twitter API you have to create an API key for your application. Put your authentication credentials in a simple JSON file:

```json
{
  "api_key":"YOUR_API_KEY",
  "api_secret":"YOUR_API_SECRET",
  "access_token":"YOUR_ACCESS_TOKEN",
  "access_token_secret":"YOUR_ACCESS_TOKEN_SECRET"
}
```
Then you can authenticate your **TwitterCrawler** instance:

```python
tcs.authenticate("PATH_TO_JSON_FILE")
```

## 4.) Setting search parameters

Before you run your **TwitterCrawler** instance you have to specify your search parameters in a Python dictionary.

```python
search_params = {
    "q":"#machinelearning OR #bigdata",
    "result_type":'recent',
    "count":100
}

tcs.set_search_arguments(search_args=search_params)
```

As I am using  [Twython](https://github.com/ryanmcgrath/twython) to handle my search requests you can find more information in the Twitter [Search API](https://dev.twitter.com/rest/public/search) about how to parametrize your search arguments properly .


## 5.) Choose search strategy

In order to work with the Twitter timeline properly one should consider using **"max_id"** and **"since_id"** . So far I have implemented two search strategies. Most of them is probably implemented in other repositories. I just followed this simple [tutorial](https://dev.twitter.com/rest/public/timelines).

### A.)  Recursive search

* Here your search starts at a specific time. It is the current time if you does not set any **current_max_id** parameter
* Then the search tries to explore past events that match your search parameters
* The search terminates if you:
   * set **custom_since_id**: events with smaller id won't be returned
      **OR**
   * set **term_func**: events older than the first event that matches this termination function won't be returned. For example you can set a time lower bound for your search.
   * all events matching your search parameters have been returned
   * **interrupt the execution**

**i.) Terminate by 'since_id'**

```python
tcs.search_by_query(custom_since_id=870285658723684355)
```
**ii.) Terminate by 'term_func'**
Here are two simple termination function example. Some utility function has been already prepared for you.

   * Terminate based on some time stamp

```python
import search_utils as su

my_created_at="Thu Jun 01 00:00:00 +0000 2017"
def my_time_bound_filter(tweet):
    return su.time_bound_filter(tweet, created_at=my_created_at)
```

   * Terminate based on since_id (it has the same effect as in the above example, when I set *custom\_since\_id=870285658723684355*)

```python
import search_utils as su

my_since_id = 870285658723684355
def my_since_id_filter(tweet):
    return su.id_bound_fiter(tweet, since_id=my_since_id)
```
After the termination function has been defined you can execute the search:

```python
tcs.search_by_query(term_func=my_time_bound_filter)
```

### B.) Stream search

   * This search starts with a **recursive search**, which goes back into the past until an event matches the termination function (**termination_func**).
   * Then the search jumps back to the present and starts a new recursive search until all events are recovered since the starting time of the previous recursive search etc.
   * The search terminates if you:
      * **interrupt the execution**
   * This type of search can be used to monitor ongoing events

For a stream search you must specify a **delta_t** parameter. Which is approximately the elapsed time in seconds between two recursive search.

```python
tcs.stream_search(delta_t=120, termination_func=my_time_bound_filter)
```
