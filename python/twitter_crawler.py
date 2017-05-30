import json
from twython import Twython
from request_scheduler import *

class TwitterCrawler(RequestScheduler):
    def __init__(self,time_frame,max_requests):
        """Twitter API scheduler object. It enables only 'max_requests' requests in every 'time_frame' seconds."""
        super(TwitterCrawler, self).__init__(time_frame,max_requests)
        self.twitter_api = None
        
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
        
    def execute_request(self):
        search_results = None
        try:
            if self.search_args != None:
                search_results = self.twitter_api.search(**self.search_args)
            else:
                raise RuntimeError("You must set search arguments!")
        except TwythonError as e:
            print(e)
        except:
            raise
        finally:
            return search_results