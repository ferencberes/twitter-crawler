from .base import SearchCrawler, NetworkCrawler
from .search import search_people
import time
    
class RecursiveCrawler(SearchCrawler):
    def __init__(self, time_frame=900, max_requests=200, sync_time=60, limit=None, verbose=False):
        super(RecursiveCrawler, self).__init__(time_frame, max_requests, sync_time, limit, verbose)
        self._msg = "Recursive search"
        
    def search(self, wait_for=2, current_max_id=0, custom_since_id=None, term_func=None, feedback_time=15*60):
        self._start_time, self._last_feedback = time.time(), time.time()
        self._num_requests = 0
        return self._search_by_query(wait_for, current_max_id, custom_since_id, term_func, feedback_time)
               
class StreamCrawler(SearchCrawler):
    def __init__(self, time_frame=900, max_requests=200, sync_time=60, limit=None, verbose=False):
        super(StreamCrawler, self).__init__(time_frame, max_requests, sync_time, limit, verbose)
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
                max_id, latest_id, cnt = recursive_info
                last_since_id = since_id
                since_id = latest_id
            if self._terminate(False):
                break
            wait_for = np.random.normal(loc=delta_t,scale=delta_t*dev_ratio)
            if self.verbose:
                print("STREAM epoch: Sleeping for %.1f seconds" % wait_for)
            time.sleep(wait_for)
            
class PeopleCrawler(SearchCrawler):
    def __init__(self, time_frame=900, max_requests=100, sync_time=60, limit=None, verbose=False):
        super(PeopleCrawler, self).__init__(time_frame, max_requests, sync_time, limit, verbose)
        
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
                print("user page: %s" % str(user_page))
            # verify
            _ = self._verify_new_request()
            # new request
            hits, last_page = search_people(self.twitter_api, search_params, page)
            self._register_request(delta_t=wait_for)
            # postprocess
            self._export_to_output_framework(hits)
            cnt += len(hits)
            page += 1
            if self._terminate():
                break
        print("%s people were collected. Exiting at page=%i" % (cnt, page))
        return page, cnt
    
class FriendsCollector(NetworkCrawler):
    def __init__(self, time_frame=900, max_requests=12, sync_time=60, limit=None, verbose=False):
        super(FriendsCollector, self).__init__("friend", time_frame, max_requests, limit, sync_time, verbose)

class FollowersCollector(NetworkCrawler):
    def __init__(self, time_frame=900, max_requests=12, sync_time=60, limit=None, verbose=False):
        super(FollowersCollector, self).__init__("follower", time_frame, max_requests, sync_time, limit, verbose)