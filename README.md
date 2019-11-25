# twitter-crawler

I implemented a simple Python Twitter crawler on top of the popular [Twython](https://github.com/ryanmcgrath/twython) package. My solution provides the following **key features in addition to Twython:**

   * respect Twitter API [rate limits](https://developer.twitter.com/en/docs/basics/rate-limits) during search
   * recursive or streaming search option for tweets and events
   * search for people
   * export search results to [MongoDB](https://www.mongodb.com/) collections (or files)

# How to deploy?

## Requirements

This package was developed in Python 3.5 conda environment.

## Install

```bash
pip install .
```

# Examples

- [Recursive search](examples/recursive.py)
- [Stream search](examples/stream.py)
- [People search](examples/people.py)
