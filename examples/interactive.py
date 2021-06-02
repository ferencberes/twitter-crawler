from twittercrawler.crawlers import InteractiveCrawler
import time, sys

def show_tweets_text(http_resp, seen_tweet_ids, max_size=10000):
    for i in range(len(http_resp['statuses'])):
        try:
            tweet_text = http_resp['statuses'][i]['text']
            tweet_id = http_resp['statuses'][i]['id']
            # only print message if it is new
            if not tweet_id in seen_tweet_ids:
	            print("Tweet Text: " + tweet_text)
	            print ("------------------------------------------")
	            seen_tweet_ids.append(tweet_id)
            else:
            	if len(seen_tweet_ids) > max_size:
            		seen_tweet_ids = seen_tweet_ids[int(max_size*0.2):]
        except:
            e = sys.exc_info()[0]
            raise 
            print("Error: %s" % e)

# initialize
interactive = InteractiveCrawler()
interactive.authenticate("../api_key.json")

# query
search_params = {
    "q":" OR ".join(["@CNN","@BBC","@guardian","@nytimes","#BREAKING"]),
    "result_type":"recent",
    "count":10
}
interactive.set_search_arguments(search_args=search_params)

seen_ids = []
times = 8
for i in range(times):
	res = interactive.search()
	print(show_tweets_text(res, seen_ids))
	if i != times-1:
		print("\nINFO: Sleeping for 15 seconds...\n")
		time.sleep(15)
