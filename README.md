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
