from .base import SearchCrawler, NetworkCrawler, UserLookup
from .search import search_people
import time
import numpy as np
    
class InteractiveCrawler(SearchCrawler):
    """
    Execute search queries interactively (basic Twython functionality).

    Parameters
    ----------
    time_frame
        The time duration you define the request policy
    max_requests
        The number of enabled requests within the time_frame
    sync_time
        Time to wait (seconds) in addition to halting time defined by API rate limits
    limit
        Terminate after the given number of Twitter API calls
    """
    def __init__(self, time_frame=900, max_requests=200, sync_time=15, limit=None, only_geo=False, verbose=False):
        super(InteractiveCrawler, self).__init__(time_frame, max_requests, sync_time, limit, only_geo, verbose)
        self._msg = "Interactive search"
        self._start_time, self._last_feedback = time.time(), time.time()
        self._num_requests = 0

    def search(self, wait_for=0):
        """
        Search for events
        
        Parameters
        ----------
        wait_for
           Seconds to pause after each Twitter API call
        """
        _ = self._verify_new_request(self.twitter_api)
        resp = self.twitter_api.search(**self.search_args)
        if self.only_geo:
            new_status = []
            for tweet in resp['statuses']:
                if self.only_geo and tweet["geo"] == None:
                    continue
                new_status.append(tweet)
            resp['statuses'] = new_status
        self._register_request(delta_t=wait_for)
        return resp

class RecursiveCrawler(SearchCrawler):
    """
    Execute search queries from a time in the past up to the current timestamp.

    Parameters
    ----------
    time_frame
        The time duration you define the request policy
    max_requests
        The number of enabled requests within the time_frame
    sync_time
        Time to wait (seconds) in addition to halting time defined by API rate limits
    limit
        Terminate after the given number of Twitter API calls
    """
    def __init__(self, time_frame=900, max_requests=200, sync_time=15, limit=None, only_geo=False, verbose=False):
        super(RecursiveCrawler, self).__init__(time_frame, max_requests, sync_time, limit, only_geo, verbose)
        self._msg = "Recursive search"
        
    def search(self, wait_for=2, current_max_id=0, custom_since_id=None, term_func=None, feedback_time=15*60):
        self._start_time, self._last_feedback = time.time(), time.time()
        self._num_requests = 0
        return self._search_by_query(wait_for, current_max_id, custom_since_id, term_func, feedback_time)
               
class StreamCrawler(SearchCrawler):
    """
    Execute search queries online.

    Parameters
    ----------
    time_frame
        The time duration you define the request policy
    max_requests
        The number of enabled requests within the time_frame
    sync_time
        Time to wait (seconds) in addition to halting time defined by API rate limits
    limit
        Terminate after the given number of Twitter API calls
    """
    def __init__(self, time_frame=900, max_requests=200, sync_time=15, limit=None, only_geo=False, verbose=False):
        super(StreamCrawler, self).__init__(time_frame, max_requests, sync_time, limit, only_geo, verbose)
        self._msg = "Stream search"
        
    def search(self, delta_t, termination_func, dev_ratio=0.1, feedback_time=15*60):
        self._start_time, self._last_feedback = time.time(), time.time()
        self._num_requests = 0
        last_since_id = 0
        since_id = None
        while True:
            if last_since_id != since_id:
                # termination function is needed only for the first round!!!
                recursive_info = self._search_by_query(wait_for=2, custom_since_id=since_id, term_func=termination_func, feedback_time=feedback_time)
                print("Recursive search result: %s" % str(recursive_info))
                success, max_id, latest_id, cnt = recursive_info
                last_since_id = since_id
                since_id = latest_id
            if (not success) or self._terminate(False):
                break
            wait_for = np.random.normal(loc=delta_t,scale=delta_t*dev_ratio)
            if self.verbose:
                print("STREAM epoch: Sleeping for %.1f seconds" % wait_for)
            time.sleep(wait_for)

from twython import TwythonStreamer
from .utils import load_credentials

class TwythonStreamCrawler():
    def __init__(self, writers=None, auth_file_path=None):
        self._writers = writers
        self.auth_file_path = auth_file_path
        
    def close(self):
        """Close writer objects"""
        try:
            if self._writers != None:
                for writer in self._writers:
                    writer.close()
            print("Connection was closed successfully!")
        except:
            raise
            
    def set_search_arguments(self,search_args):
        """Set search parameters with a dictionary"""
        self.search_args = search_args
        print(self.search_args)
        
    def search(self, wait_for=0.0):
        query = self.search_args["q"].replace(" OR ",",")
        lang = self.search_args.get("lang", None)
        WRITERS = self._writers
        class MyStreamer(TwythonStreamer):
            def on_success(self, data):
                if WRITERS == None:
                    raise RuntimeError("You did not specify any output for your search! Use the connect_output() function!")
                    #if 'text' in data:
                    #    print(data['text'])
                else:
                    if "id_str" in data:
                        for writer in WRITERS:
                            writer.write([data])
                    else:
                        print("NO ID:", data)
                    if wait_for > 0.0:
                        time.sleep(wait_for)

            def on_error(self, data):
                print("ERROR occured")
                print(data)
                print()
        
        config = load_credentials(["api_key","api_secret","access_token","access_token_secret"], self.auth_file_path)
        stream = MyStreamer(config["api_key"], config["api_secret"], config["access_token"], config["access_token_secret"])
        stream.statuses.filter(track=query, language=lang)
            
class PeopleCrawler(SearchCrawler):
    """
    Search for Twitter users.

    Parameters
    ----------
    time_frame
        The time duration you define the request policy
    max_requests
        The number of enabled requests within the time_frame
    sync_time
        Time to wait (seconds) in addition to halting time defined by API rate limits
    limit
        Terminate after the given number of Twitter API calls
    """
    def __init__(self, time_frame=900, max_requests=100, sync_time=15, limit=None, verbose=False):
        super(PeopleCrawler, self).__init__(time_frame, max_requests, sync_time, limit, False, verbose)
        self._msg = "People search"
        
    def search(self, wait_for=2, feedback_time=15*60):
        search_params = {}
        search_params["q"] = self.search_args["q"]
        search_params["count"] = self.search_args.get("count", 20)
        page, cnt = 0, 0
        last_page = False
        self._start_time, self._last_feedback = time.time(), time.time()
        self._num_requests = 0
        while not last_page:
            # feedback
            if time.time() - self._last_feedback > feedback_time:
                self._show_time_diff()
            print("user page: %s" % str(page))
            # verify
            _ = self._verify_new_request(self.twitter_api)
            # new request
            hits, last_page = search_people(self.twitter_api, search_params, page)
            self._register_request(delta_t=wait_for)
            # postprocess
            self._export(hits)
            cnt += len(hits)
            page += 1
            if self._terminate():
                break
        print("%s people were collected. Exiting at page=%i" % (cnt, page))
        return page, cnt
    
class FriendsCollector(NetworkCrawler):
    """
    Crawl friends for a given set of Twitter accounts.

    Parameters
    ----------
    time_frame
        The time duration you define the request policy
    max_requests
        The number of enabled requests within the time_frame
    sync_time
        Time to wait (seconds) in addition to halting time defined by API rate limits
    limit
        Terminate after the given number of Twitter API calls
    """
    def __init__(self, time_frame=900, max_requests=12, sync_time=15, limit=None, verbose=False):
        super(FriendsCollector, self).__init__("friend", time_frame, max_requests, sync_time, limit, verbose)
        self._msg = "Friends network collector"

class FollowersCollector(NetworkCrawler):
    """
    Crawl followers for a given set of Twitter accounts.

    Parameters
    ----------
    time_frame
        The time duration you define the request policy
    max_requests
        The number of enabled requests within the time_frame
    sync_time
        Time to wait (seconds) in addition to halting time defined by API rate limits
    limit
        Terminate after the given number of Twitter API calls
    """
    def __init__(self, time_frame=900, max_requests=12, sync_time=15, limit=None, verbose=False):
        super(FollowersCollector, self).__init__("follower", time_frame, max_requests, sync_time, limit, verbose)
        self._msg = "Follower network collector"
