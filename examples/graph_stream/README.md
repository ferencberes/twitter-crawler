# Graph stream example

In this example, we demonstrate how to create a graph stream from Twitter data using Python socket programming.

# Overview

Our streaming framework has two main components. A socket is used for communication between the producer and the consumer.

## Producer

- collects tweets with the Twitter Streaming API in real-time:
   - only English tweets with the following hashtags are collected: 
   #BREAKING, #BREAKINGNEWS, #breakingnews
- **sender of the graph stream:**
   - filter for tweets containing @-mentions 
   - push collected tweets to a socket

## Consumer

- **receiver of the graph stream:**
   - read tweets from the socket
- extract @-mentions from each tweet JSON object
- print @-mention links with timestamp, source and target user account identifiers

# Usage

**1.) Start the producer:** Specify

- your Twitter API credentials (API_JSON_PATH). See the details [here](https://github.com/ferencberes/twitter-crawler/tree/streaming#b-json-configuration-file).
- a port for the socket (PORT)

```bash
python producer.py API_JSON_PATH PORT
```

**2.) Start the consumer** in a different console with the same port:

```bash
python consumer.py PORT
```
