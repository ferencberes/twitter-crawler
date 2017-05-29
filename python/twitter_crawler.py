import json
from twython import Twython
from request_scheduler import *

class TwitterCrawler(RequestScheduler):
    def __init__(self,time_frame,max_requests):
        super(TwitterCrawler, self).__init__(time_frame,max_requests)
        self.twitter_api = None
        
    def authenticate(self,auth_file_path):
        try:
            with open(auth_file_path,"r") as f:
                auth_info = json.load(f)
            self.twitter_api = Twython(auth_info["api_key"], auth_info["api_secret"])
            print("Authentication was successful!")
        except:
            raise
        
    def execute_request(self):
        search_results = None
        try:
            search_results = self.twitter_api.search(q='#FINABudapest2017', result_type='recent', count=20)
        except TwythonError as e:
            print(e)
        finally:
            return search_results