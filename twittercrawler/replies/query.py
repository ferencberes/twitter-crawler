from twittercrawler.utils import tweet_time_2_epoch
from datetime import datetime as dt
import numpy as np

class TweetQuery():
    def __init__(self, tweet_dict):
        self._id = tweet_dict["id_str"]
        self._user_name = tweet_dict["user"]["screen_name"]
        self._user_id = tweet_dict["user"]["id_str"]
        self._epoch = tweet_time_2_epoch(tweet_dict["created_at"]) if "created_at" in tweet_dict else None
        self._likes = tweet_dict["favorite_count"]
        self._retweets = tweet_dict["retweet_count"]
        self._max_id = None
        self._since_id = int(self._id)
        self._last_access = None
        
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
        params = {
            "id_str":self.id,
            "favorite_count":self.likes,
            "retweet_count":self.retweets,
            "user":{
                "id_str": self.user_id,
                "screen_name": self.user_name
            }
        }
        copy_q = TweetQuery(params)
        copy_q.set_epoch(self.epoch)
        copy_q.set_max_id(self.max_id)
        copy_q.set_since_id(self.since_id)
        return copy_q
        
    def __repr__(self):
        return "(%s, %s, %s, %s, %i, %i, %s, %s)" % (self.id, self.user_id, self.user_name, self.dt, self.likes, self.retweets, self.max_id, self.since_id)
    
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
            return 10.0
        elif self.accessed_since_days == 0:
            return 0.0
        else:
            return self.elapsed_days + np.log10(1.0+self.engagements)