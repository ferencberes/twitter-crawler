from .base import TwitterCrawler
from .search import search_people
import datetime, time

class PeopleCrawler(TwitterCrawler):
    def __init__(self, time_frame=900, max_requests=800, sync_time=60, verbose=False):
        super(PeopleCrawler, self).__init__(time_frame, max_requests, sync_time, verbose)
        
    def _print_feedback(self, max_id=0, since_id=None, latest_id=None, user_page=None):
        current_time = time.time()
        print("### FEEDBACK ###")
        print("page: %s" % str(user_page))
        td = datetime.timedelta(seconds=current_time-self._start_time)
        print("People search is RUNNING since: %i days, %i hours and %i minutes %i seconds" % (td.days, td.seconds//3600, (td.seconds//60)%60, td.seconds%60))
        self._last_feedback = current_time
        print("################")
        
    def search(self, wait_for=2, feedback_time=15*60):
        search_params = {}
        search_params["q"] = self.search_args["q"]
        search_params["count"] = self.search_args.get("count", 20)
        page, cnt = 0, 0
        last_page = False
        self._start_time, self._last_feedback = time.time(), time.time()
        while not last_page:
            # feedback
            if time.time() - self._last_feedback > feedback_time:
                self._print_feedback(user_page=page)
            # verify
            _ = self._verify_new_request()
            # new request
            hits, last_page = search_people(self.twitter_api, search_params, page)
            print(hits)
            self._register_request(delta_t=wait_for)
            # postprocess
            self._export_to_output_framework(hits)
            cnt += len(hits)
            page += 1
        print("%s people were collected. Exiting at page=%i" % (cnt, page))
        return page, cnt

    
class RecursiveCrawler(TwitterCrawler):
    def __init__(self, time_frame=900, max_requests=250, sync_time=60, verbose=False):
        super(RecursiveCrawler, self).__init__(time_frame, max_requests, sync_time, verbose)
        
    def _print_feedback(self, max_id=0, since_id=None, latest_id=None, user_page=None):
        current_time = time.time()
        print("### FEEDBACK ###")
        print("max_id: %s, since_id: %s, latest_id: %s" % (str(max_id), str(since_id), str(latest_id)))
        td = datetime.timedelta(seconds=current_time-self._start_time)
        print("Recursive search is RUNNING since: %i days, %i hours and %i minutes %i seconds" % (td.days, td.seconds//3600, (td.seconds//60)%60, td.seconds%60))
        self._last_feedback = current_time
        print("################")
        
    def search(self, wait_for=2, current_max_id=0, custom_since_id=None, term_func=None, feedback_time=15*60):
        self._start_time, self._last_feedback = time.time(), time.time()
        return self._search_by_query(wait_for, current_max_id, custom_since_id, term_func, feedback_time)
        
        
class StreamCrawler(TwitterCrawler):
    def __init__(self, time_frame=900, max_requests=350, sync_time=60, verbose=False):
        super(StreamCrawler, self).__init__(time_frame, max_requests, sync_time, verbose)
        
    def _print_feedback(self, max_id=0, since_id=None, latest_id=None, user_page=None):
        current_time = time.time()
        print("### FEEDBACK ###")
        td = datetime.timedelta(seconds=current_time-self._start_time)
        print("Stream search is RUNNING since: %i days, %i hours and %i minutes %i seconds" % (td.days, td.seconds//3600, (td.seconds//60)%60, td.seconds%60))
        self._last_feedback = current_time
        print("################")
        
    def search(self, delta_t, termination_func, dev_ratio=0.1, feedback_time=15*60):
        self._start_time, self._last_feedback = time.time(), time.time()
        return self._stream_search(delta_t, termination_func, dev_ratio, feedback_time)