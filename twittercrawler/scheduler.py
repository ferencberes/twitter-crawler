import time, datetime, pymongo, os
import numpy as np
from collections import deque
from pymongo import MongoClient
from twython.exceptions import TwythonError

class RequestScheduler():
    def __init__(self, time_frame, max_requests, sync_time, verbose=False):
        """Abstract scheduler object. It enables only 'max_requests' requests in every 'time_frame' seconds."""
        # scheduler parameters
        self.time_frame = time_frame
        self.max_requests = max_requests
        self.sync_time = sync_time
        self.verbose = verbose
        self._requests = deque([])
        # mongodb parameters
        self._client, self._db = None, None
        self._mongo_coll, self._output_file = None, None
        self._connection_type = None
        
    def connect_to_mongodb(self,collection_name,port=27017,db_name="twitter-crawler"):
        """Connect to MongoDB collection"""
        try:
            self._client = MongoClient('mongodb://localhost:%i/' % port)
            self._db = self._client[db_name]
            try:
                self._db.create_collection(collection_name)
                print("'%s' collection was created!" % collection_name)
            except:
                pass
            self._mongo_coll = self._db[collection_name]
            result = self._mongo_coll.create_index([('id_str', pymongo.ASCENDING)],unique=True)
            print(result)
            print("Connection was created successfully!")
            self._connection_type = "mongo"
        except:
            raise

    def connect_to_file(self, file_name):
        """Connect to output file. Collected tweets and retweets will be stored in tihs file."""
        if os.path.exists(file_name):
            self._output_file = open(file_name, 'a')
        else:
            self._output_file = open(file_name, 'w')
        self._connection_type = "file"

    def close(self):
        """Close MongoDB connection"""
        try:
            if self._connection_type == "mongo":
                if self._client != None:
                    self._client.close()
            elif self._connection_type == "file":
                self._output_file.close()
            print("Connection was closed successfully!")
        except:
            raise
        
    def _check_remaining_limit(self, twitter_api, current_time):
        valid, wait_for = True, self.sync_time
        try:
            num_remaining = int(twitter_api.get_lastfunction_header('x-rate-limit-remaining'))
            rate_limit_reset = int(twitter_api.get_lastfunction_header('x-rate-limit-reset'))
            valid = num_remaining > 0
            wait_for = rate_limit_reset - current_time + self.sync_time 
        except TwythonError:
            print("No former request were made!") 
        except:
            raise
        finally:
            return valid, wait_for

    def _verify_new_request(self, twitter_api):
        """Return only when a request can be made"""
        current_time = time.time()
        valid, wait_for = self._check_remaining_limit(twitter_api, current_time)
        if valid:
            while len(self._requests) > 0 and current_time - self._requests[0] > self.time_frame:
                self._requests.popleft()
            if len(self._requests) >= self.max_requests:
                wait_for = self.time_frame - (current_time - self._requests[0]) + self.sync_time
                print("VERIFYING: sleeping for %.1f seconds" % wait_for)
                time.sleep(wait_for)
        else:
            print("RATE LIMIT RESET in %.1f seconds" % wait_for)
            time.sleep(wait_for)
        return True
            
    def _register_request(self,delta_t,dev_ratio=0.1):
        """Register a request with time stamp"""
        self._requests.append(time.time())
        wait_for = np.random.normal(loc=delta_t,scale=delta_t*dev_ratio)
        if self.verbose:
            print("A REQUEST was made: sleeping for %.1f seconds" % wait_for)
        time.sleep(wait_for)
                    
