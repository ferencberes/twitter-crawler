import json, shutil, os, twython, time

class UserTweetStore():
    def __init__(self, store_dir, reload=True):
        self.store_dir = store_dir
        self.reload = reload
        if self.reload:
            self.load()
        else:
            self.reset()
        
    @property
    def store_dir(self):
        if not os.path.exists(self._store_dir):
            os.makedirs(self._store_dir)
        return self._store_dir
    
    @property
    def user_intervals(self):
        return self._user_intervals
    
    @store_dir.setter
    def store_dir(self, val):
        self._store_dir = val
        
    @property
    def interval_file(self):
        return os.path.join(self.store_dir, "user_intervals.json")
        
    @property
    def replies_dir(self):
        rdir = os.path.join(self.store_dir, "replies")
        if not os.path.exists(rdir):
            os.makedirs(rdir)
        return rdir
        
    def save(self):
        with open(self.interval_file, 'w') as f:
            json.dump(self._user_intervals, f, indent=4)
        
    def load(self):
        if os.path.exists(self.interval_file):
            with open(self.interval_file) as f:
                self._user_intervals = json.load(f)
            print("UserStore loaded from folder: %s" % self.store_dir)
        else:
            self.reset()
            
    def reset(self):
        print("UserStore reset in this directory: %s" % self.store_dir)
        if os.path.exists(self.store_dir):
            shutil.rmtree(self.store_dir)
        self._user_intervals = {}
    
    def get_user(self, user_id):
        return self._user_intervals.get(user_id, [None, None])
    
    def update(self, query, latest_id):
        user_id = query.user_id
        from_id, to_id = self.get_user(user_id)
        qid = int(query.id)
        if from_id == None or qid < from_id:
            if query.max_id == None:
                from_id = qid
            else:
                from_id = query.max_id
        if to_id == None or latest_id > to_id:
            # In case of max_id the to_id is properly set. The gap in the interval will be fixed when the same query returns (after executing with max_id)
            to_id = latest_id
        self._user_intervals[user_id] = [from_id, to_id]
    
    def adjust_query(self, query):
        queries = []
        if query.max_id == None:
            from_id, to_id = self.get_user(query.user_id)
            print("ADJUST",query.user_id,from_id,to_id)
            if from_id == None:
                queries.append(query)
            else:
                print("STORE", from_id, query.since_id, from_id - query.since_id)
                if query.since_id < from_id:
                    q = query.copy()
                    q.set_max_id(from_id)
                    queries.append(q)
                # avoid collecting the same data twice
                query.set_since_id(to_id)
                queries.append(query)
        else:
            #The original query is executed in case of max_id!=None
            queries.append(query)
        print("ADJUST",len(queries))
        return queries
    
from twittercrawler.utils import load_json_result
    
class SearchEngine():
    def __init__(self, crawler, store, tweet_mode="extended"):
        self.crawler = crawler
        self.store = store
        self.tweet_mode = tweet_mode
        
    def get_status(self, tweet_id):
        res = None
        try:
            res = self.crawler.twitter_api.show_status(id=tweet_id, tweet_mode=self.tweet_mode)
        except Exception:
            traceback.print_exc()
            print()
        finally:
            return res 
    
    def get_output_fp(self, query):
        return os.path.join(self.store.replies_dir,"%s.txt" % query.user_id)
        
    def collect_replies(self, query, count=100, result_type='recent', wait_for=0, feedback_time=300):
        print(query)
        search_params = {
            "q" : "to:%s" % query.user_name,
            "result_type" : result_type,
            "count" : count,
            "tweet_mode" : self.tweet_mode
        }
        self.crawler.connect_to_file(self.get_output_fp(query))
        self.crawler.set_search_arguments(search_args=search_params)
        if query.max_id != None:
            result = self.crawler.search(wait_for=wait_for, feedback_time=feedback_time, current_max_id=query.max_id, custom_since_id=query.since_id)
        else:
            result = self.crawler.search(wait_for=wait_for, feedback_time=feedback_time, custom_since_id=query.since_id)
        self.crawler.close()
        return result
    
    def extract_replies(self, query):
        reply_tweets = load_json_result(self.get_output_fp(query))
        replies = []
        for tweet in reply_tweets:
            replied_tweet = tweet.get("in_reply_to_status_id_str", None)
            if replied_tweet == query.id:
                replies.append(tweet)
        return replies
        
    # TODO: nagyon átgondolni!!!
    def execute(self, original_query):
        queries = self.store.adjust_query(original_query)
        for idx, query in enumerate(queries):
            success, max_id, latest_id, cnt = self.collect_replies(query)
            print(idx, success, max_id, latest_id, cnt)
            if success:
                if cnt > 0:
                    self.store.update(query, latest_id)
            else:
                break
        replies = []
        if success:
            replies = self.extract_replies(original_query)
            original_query.mark_access()
            if cnt > 0:
                original_query.set_since_id(latest_id)
                original_query.set_max_id(None)#WHY is it inside cnt>0?
        else:
            original_query.set_max_id(max_id)
        return success, original_query, replies