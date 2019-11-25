import time, os
os.environ['TZ']='UTC'

### Utils

def tweet_time_2_epoch(time_str):
    """Convert Twitter 'created_at' time format to epoch"""
    time_parts = time_str.split(" ")
    year, month, day, time_parts, time_zone = time_parts[-1], time_parts[1], time_parts[2], time_parts[3], time_parts[4]
    time_stamp_str = " ".join([year,month,day,time_parts])
    #print(time_stamp_str)
    t = time.mktime(time.strptime(time_stamp_str, "%Y %b %d %H:%M:%S"))
    return t
    
def get_time_termination(time_str):
    """Return termination function with respest to Twitter string timestamp 'time_str' (e.g. 'Mon Nov 25 12:41:30 +0000 2019'). The search will terminate for the first tweet with smaller smaller."""
    def time_filter(tweet, created_at):
        t_lower_bound = tweet_time_2_epoch(created_at)
        t_tweet = tweet_time_2_epoch(tweet["created_at"])
        if t_tweet >= t_lower_bound:
            return False
        else:
            return True
    return lambda tweet : time_filter(tweet, created_at=time_str)
    
def get_id_termination(tweet_id):
    """Return termination function with respest to 'tweet_id'. The search will terminate for the first tweet with smaller id."""
    def id_filter(tweet, since_id):
        if int(tweet["id"]) > since_id:
            return False
        else:
            return True
    return lambda tweet : id_filter(tweet, since_id=tweet_id)
    
### Twython extensions

from twython import TwythonError

def search_people(twitter_api, search_params, page=0):
    search_params["count"] = min(20, search_params.get("count", 20))
    search_params["page"] = page
    res = []
    last_page_reached = False
    try:
        res = twitter_api.request(endpoint="users/search", params=search_params)
        if len(res) < search_params["count"]:
            last_page_reached = True
    except TwythonError as twe:
        if "parameter page parameter is invalid" in str(twe):
            last_page_reached = True
        else:
            raise twe
    return res, last_page_reached