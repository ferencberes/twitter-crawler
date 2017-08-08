import time, os
os.environ['TZ']='UTC'

def tweet_time_2_epoch(time_str):
    """Convert Twitter 'created_at' time format to epoch"""
    time_parts = time_str.split(" ")
    year, month, day, time_parts, time_zone = time_parts[-1], time_parts[1], time_parts[2], time_parts[3], time_parts[4]
    time_stamp_str = " ".join([year,month,day,time_parts])
    #print(time_stamp_str)
    t = time.mktime(time.strptime(time_stamp_str, "%Y %b %d %H:%M:%S"))
    return t

def id_bound_fiter(tweet, since_id):
    """Filter used for setting a 'since_id' as the lower bound of the search"""
    if int(tweet["id"]) > since_id:
        return False
    else:
        return True
    
def time_bound_filter(tweet, created_at):
    """Filter used for setting a timestamp 'created_at' as the lower bound of the search"""
    t_lower_bound = tweet_time_2_epoch(created_at)
    t_tweet = tweet_time_2_epoch(tweet["created_at"])
    if t_tweet >= t_lower_bound:
        return False
    else:
        return True