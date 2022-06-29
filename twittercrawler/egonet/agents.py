import tweepy, time

class BaseAgent():
    def __init__(self, credentials, wait_on_rate_limit=True, enable_v2=False):
        self.enable_v2 = enable_v2
        self._check_credentials(credentials)
        auth = tweepy.OAuth1UserHandler(
            credentials["api_key"], credentials["api_secret"], credentials["access_token"], credentials["access_token_secret"]
        )
        self.api = tweepy.API(auth, wait_on_rate_limit=True)
        if self.enable_v2:
            self.client = tweepy.Client(credentials["bearer_token"])
        else:
            self.client = None
        
    def _check_credentials(self, credentials):
        keys = ["api_key", "api_secret", "access_token", "access_token_secret"]
        if self.enable_v2:
            keys.append("bearer_token")
        for key in keys:
            if not key in keys:
                raise RuntimeError("'%s' is not present in the credentials!")
        
class QueryUserConnections(BaseAgent):
    def __init__(self, credentials, query_friends=True, wait_on_rate_limit=True, enable_v2=False):
        super(QueryUserConnections, self).__init__(credentials, wait_on_rate_limit, enable_v2)
        self.query_friends = query_friends
        
    def execute(self, screen_name):
        if self.query_friends:
            results = tweepy.Cursor(self.api.get_friend_ids, screen_name=screen_name).items()
        else:
            results = tweepy.Cursor(self.api.get_follower_ids, screen_name=screen_name).items()
        user_ids = []
        while True:
            try:
                user_id = next(results)
            except tweepy.errors.TooManyRequests:
                time.sleep(60*15)
                user_id = next(results)
            except StopIteration:
                break
            #print(user_id)
            user_ids.append(user_id)
        return user_ids
        
# TODO: get full_text!!!
class LookupAgent(BaseAgent):
    def __init__(self, credentials, user_mode, wait_on_rate_limit=True, enable_v2=False):
        super(LookupAgent, self).__init__(credentials, wait_on_rate_limit, enable_v2)
        self.queue = []
        # API restriction
        self._threshold = 100
        self._user_mode = user_mode
        
    #TODO: reduce duplications!!!
    def add(self, queries, high_priority=False):
        if high_priority:
            self.queue = queries + self.queue
        else:
            self.queue += queries
            
    @property
    def is_long(self):
        return len(self.queue) > self._threshold
    
    def __len__(self):
        return len(self.queue)
            
    #TODO: make magic for exceptions...
    def _make_query(self):
        if self.is_long:
            queries = self.queue[:self._threshold].copy()
            self.queue = self.queue[self._threshold:]
        else:
            queries = self.queue.copy()
            self.queue = []
        queries = list(set(queries))
        if self._user_mode:
            results = self.api.lookup_users(user_id=queries)
        else:
            results = self.api.lookup_statuses(id=queries, tweet_mode='extended')
        return results
            
    def execute(self, force=False):
        results = []
        if force:
            while len(self.queue) > 0:
                results += self._make_query()
        else:
            while self.is_long:
                results += self._make_query()
        return results