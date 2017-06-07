import json, twython, time
import numpy as np
from twython import Twython
from request_scheduler import *


class TwitterCrawler(RequestScheduler):    
    
    def __init__(self,time_frame,max_requests,verbose=False):
        """Twitter API scheduler object. It enables only 'max_requests' requests in every 'time_frame' seconds."""
        super(TwitterCrawler, self).__init__(time_frame,max_requests,verbose)
        self.twitter_api = None
        self.search_start_time, self.search_last_feedback = None, None
        self.stream_start_time, self.stream_last_feedback = None, None
        
    def authenticate(self,auth_file_path):
        """Authenticate application with Twython."""
        try:
            with open(auth_file_path,"r") as f:
                auth_info = json.load(f)
            self.twitter_api = Twython(auth_info["api_key"], auth_info["api_secret"])
            print("Authentication was successful!")
        except:
            raise
            
    def set_search_arguments(self,search_args):
        """Set search parameters with a dictionary"""
        self.search_args = search_args
        print(self.search_args)        
        
    def print_feedback(self, max_id=0, since_id=None, latest_id=None):
        current_time = time.time()
        print("### FEEDBACK ###")
        print("max_id: %s, since_id: %s, latest_id: %s" % (str(max_id), str(since_id), str(latest_id)))
        if self.search_start_time != None:
            td = datetime.timedelta(seconds=current_time-self.search_start_time)
            print("search_by_query() is RUNNING since: %i days, %i hours and %i minutes %i seconds" % (td.days, td.seconds//3600, (td.seconds//60)%60, td.seconds%60))
            self.search_last_feedback = current_time
        if self.stream_start_time != None:
            td = datetime.timedelta(seconds=current_time-self.stream_start_time)
            print("stream_search() is RUNNING since: %i days, %i hours and %i minutes %i seconds" % (td.days, td.seconds//3600, (td.seconds//60)%60, td.seconds%60))
            self.stream_last_feedback = current_time
        print("################")
        
    def search_by_query(self, wait_for=2, current_max_id=0, custom_since_id=None, term_func=None, feedback_time=15*60):
        self.search_start_time, self.search_last_feedback = time.time(), time.time()
        if "max_id" in self.search_args:
            del self.search_args["max_id"]
        if "since_id" in self.search_args:
            del self.search_args["since_id"]
        
        prev_max_id = -1
        latest_id = -1
        cnt = 0
        while current_max_id != prev_max_id:
            result_tweets = []
            
            # feedback
            if time.time() - self.search_last_feedback > feedback_time:
                self.print_feedback(current_max_id, custom_since_id, latest_id=latest_id)
                
            stop_search = False
            try:
                if current_max_id > 0:
                    self.search_args["max_id"] = current_max_id-1
                if custom_since_id != None:
                    self.search_args["since_id"] = custom_since_id
                
                #print(self.search_args)
                _ = self.verify_new_request()
                tweets = self.twitter_api.search(**self.search_args)
                self.register_request(delta_t=wait_for)
                #print()
                
                prev_max_id = current_max_id
                
                for tweet in tweets['statuses']:
                    tweet_id = int(tweet['id'])
                    if custom_since_id == None or tweet_id >= custom_since_id:
                        result_tweets.append(tweet)
                    if current_max_id == 0 or current_max_id > tweet_id:
                        current_max_id = tweet_id
                    if latest_id < tweet_id:
                        latest_id = tweet_id
                    if term_func != None and term_func(tweet):
                        stop_search = True
                        break

                #no new tweets found
                if (prev_max_id == current_max_id):
                    stop_search = True
                    
                #last tweet found above since_id
                if custom_since_id != None and current_max_id <= custom_since_id + 1:
                    stop_search = True

                self.insert_tweets_to_coll(result_tweets)
                cnt += len(result_tweets)
                    
                if stop_search:
                    break
            except twython.exceptions.TwythonRateLimitError:
                raise
            except Exception as exc:
                raise
        
        return current_max_id, latest_id, cnt  
    
    def stream_search(self, delta_t, termination_func, dev_ratio=0.1, feedback_time=15*60):
        self.stream_start_time, self.stream_last_feedback = time.time(), time.time()
        last_since_id = 0
        since_id = None
        while True:
            # feedback
            if time.time() - self.stream_last_feedback > feedback_time:
                self.search_start_time, self.search_last_feedback = time.time(), time.time()
                self.print_feedback(since_id=since_id)
                
            if last_since_id != since_id:
                # termination function is needed only for the first round!!!
                res = self.search_by_query(wait_for=2, custom_since_id=since_id, term_func=termination_func, feedback_time=feedback_time)
                print("Recursive search result: %s" % str(res))
                max_id, latest_id, cnt = res
                last_since_id = since_id
                since_id = latest_id
            wait_for = np.random.normal(loc=delta_t,scale=delta_t*dev_ratio)
            if self.verbose:
                print("STREAM epoch: Sleeping for %.1f seconds" % wait_for)
            time.sleep(wait_for)
            
    def insert_tweets_to_coll(self,tweets):
        for tweet in tweets:
            try:
                self._raw_coll.insert_one(tweet)
            except Exception as err:
                print(str(err))