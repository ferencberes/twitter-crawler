from twittercrawler.utils import tweet_time_2_epoch
from datetime import datetime as dt
import numpy as np

class TweetQuery():
    def __init__(self, tweet_dict=None):
        self._id = None
        self._user_id = None
        self._user_name = None
        self._epoch = None
        self._likes = None
        self._retweets = None
        self._max_id = None
        self._since_id = None
        self._last_access = None
        if tweet_dict != None:
            self._load_from_tweet(tweet_dict)
        
    def _load_from_tweet(self, tweet_dict):
        self._id = tweet_dict["id_str"]
        self._user_id = tweet_dict["user"]["id_str"]
        self._user_name = tweet_dict["user"]["screen_name"]
        self._epoch = tweet_time_2_epoch(tweet_dict["created_at"])
        self._likes = tweet_dict["favorite_count"]
        self._retweets = tweet_dict["retweet_count"]
        self._since_id = int(self._id)
    
    def load(self, d):
        self._id = d["id"]
        self._user_id = d["user_id"]
        self._user_name = d["user_name"]
        self._epoch = d["epoch"]
        self._likes = d["likes"]
        self._retweets = d["retweets"]
        self._max_id = d["max_id"]
        self._since_id = d["since_id"]
        try:
            self._last_access = dt.strptime(d["last_access"], '%Y-%m-%d %H:%M:%S.%f')
        except TypeError:
            self._last_access = None
        except:
            raise
    
    def get(self):
        return {
            "id":self.id,
            "user_id":self.user_id,
            "user_name":self.user_name,
            "epoch":self.epoch,
            "likes":self.likes,
            "retweets":self.retweets,
            "max_id":self.max_id,
            "since_id":self.since_id,
            "last_access":self._last_access,
            "priority":self.priority,
            "dt":self.dt
        }
        
    def __repr__(self):
        return str(self.get())
        
    def update_metrics(self, tweet_dict):
        if tweet_dict["id_str"] == self.id:
            self._likes = tweet_dict["favorite_count"]
            self._retweets = tweet_dict["retweet_count"]
        else:
            raise ValueError("Id mismatch! Original id: %s, new id: %s" % (self.id, tweet_dict["id_str"]))  
        
    def set_epoch(self, epoch):
        self._epoch = epoch
        
    def set_max_id(self, max_id):
        self._max_id = max_id
        
    def set_since_id(self, since_id):
        self._since_id = int(since_id)
        
    def mark_access(self):
        self._last_access = dt.now()
        
    def copy(self):
        params = self.get()
        copy_q = TweetQuery(tweet_dict=None)
        copy_q.load(params)
        return copy_q
    
    @property
    def id(self):
        return self._id
    
    @property
    def user_name(self):
        return self._user_name
    
    @property
    def user_id(self):
        return self._user_id
    
    @property
    def epoch(self):
        return self._epoch
    
    @property
    def dt(self):
        return dt.fromtimestamp(self.epoch)
    
    @property
    def date_str(self):
        return self.dt.strftime('%Y-%m-%d')
    
    @property
    def likes(self):
        return self._likes
    
    @property
    def retweets(self):
        return self._retweets
    
    @property
    def engagements(self):
        return self.likes + self.retweets
    
    @property
    def max_id(self):
        return self._max_id
    
    @property
    def since_id(self):
        return self._since_id
    
    @property
    def elapsed_days(self):
        return (dt.now() - self.dt).days
    
    @property
    def accessed_since_days(self):
        if self._last_access == None:
            return -1
        else:
            return (dt.now() - self._last_access).days
        
    @property
    def priority(self):
        if self.max_id != None:
            return 100.0
        elif self.accessed_since_days == 0:
            return 0.0
        else:
            return self.elapsed_days + np.log10(1.0+self.engagements)