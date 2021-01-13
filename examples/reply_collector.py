import numpy as np
import pandas as pd
import os, shutil, sys, time

from twittercrawler.replies.components import SearchEngine, UserTweetStore
from twittercrawler.replies.query import TweetQuery
from twittercrawler.replies.collector import ReplyCollector
from twittercrawler.crawlers import RecursiveCrawler

data_dir = sys.argv[1]
tweet_ids_file = sys.argv[2]
store_dir = os.path.join(data_dir,"user_store")
collector_dir = os.path.join(data_dir,"collector")
twitter_key_fp = "../api_key.json"
comet_key_fp = "../comet_key.txt"

#if os.path.exists(data_dir):
#    shutil.rmtree(data_dir)

comet_info = (comet_key_fp,"collector","covid-vaccine")
crawler = RecursiveCrawler(max_requests=400)
crawler.authenticate(twitter_key_fp)
store = UserTweetStore(store_dir)
engine = SearchEngine(crawler, store)

print(len(store.user_intervals))

tweet_ids = []
with open(tweet_ids_file) as f:
    for line in f:
        if not "#" in line:
            tweet_ids.append(line.rstrip())
print(tweet_ids)

for tweet_id in tweet_ids:
    print()
    print("New seed tweet:", tweet_id)
    collector = ReplyCollector(engine, tweet_id, collector_dir)
    collector.run(feedback_interval=10, max_requests=10000, comet_info=comet_info)
    print("SLEEPING for 5 minutes")
    time.sleep(300)
    print()