# Graph stream example

In this example we demonstrate how to create a graph stream from Twitter data using Python socket programming.

# Overview

Our tiny streaming framework has two components. A socket is used for communication between the producer and the consumer.

## Producer

- collects Twitter data related to the latest news on the fly
   - Tweets containing the following keywords and hashtags: #BREAKING, BREAKING, "breaking news", breakingnews
- **sender of the graph stream:**
   - the latest tweets containing @-mentions are pushed to the socket in every 15 seconds

## Consumer

- **receiver of the graph stream:**
   - read tweets from the socket
- extract @-mentions from each tweet JSON object
- print @-mentions links with timestamp, source and target user account

# Usage

**1.) Start the producer:** You must specify..

- your Twitter API credentials for the producer (API_JSON_PATH)
- a port for the socket (PORT)

```bash
python producer.py API_JSON_PATH PORT
```

**2.) Start the consumer** in a different console with the same port:

```bash
python consumer.py PORT
```