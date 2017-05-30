import time, datetime
import numpy as np
from collections import deque
from pymongo import MongoClient

class RequestScheduler():
    def __init__(self,time_frame,max_requests,port=27017,db_name="twitter-crawler",verbose=False):
        """Abstract scheduler object. It enables only 'max_requests' requests in every 'time_frame' seconds."""
        # scheduler parameters
        self.time_frame = time_frame
        self.max_requests = max_requests
        self.verbose = verbose
        self._requests = deque([])
        # mongodb parameters
        self._client, self._db = None, None
        self._raw_coll = None
        self._port = port
        self._db_name = db_name
        
    def connect(self,collection_name):
        """Connect to MongoDB collection"""
        try:
            self._client = MongoClient('mongodb://localhost:%i/' % self._port)
            self._db = self._client[self._db_name]
            try:
                self._db.create_collection(collection_name)
                print("'%s' collection was created!" % collection_name)
            except:
                pass
            self._raw_coll = self._db[collection_name]
            print("Connection was created successfully!")
        except:
            raise
        
    def close(self):
        """Close MongoDB connection"""
        try:
            if self._client != None:
                self._client.close()
        
            print("Connection was closed successfully!")
        except:
            raise
        
    def execute_request(self):
        return None
        
    def run(self,delta_t,dev_ratio=0.2,sync_time=10, feedback_time=15*60):
        """Run scheduler object. It will sleep for normally distributed seconds after each request.
        'delta_t' is the mean and 'delta_t'*'dev_ratio' is the deviance of this normal distribution."""
        start_time, last_feedback = time.time(), time.time()
        print("Started at: %s\n" % time.strftime("%b %d %Y %H:%M:%S",time.localtime()))
        while True:
            # feedback
            current_time = time.time()
            if current_time - last_feedback > feedback_time:
                td = datetime.timedelta(seconds=current_time - start_time)
                print("Scheduler RUNNING since: %i days, %i hours and %i minutes" % (td.days, td.seconds//3600, (td.seconds//60)%60))
                last_feedback = current_time
                
            # request
            if len(self._requests) < self.max_requests:
                time_str = time.strftime("%b %d %Y %H:%M:%S",time.localtime())
                self._raw_coll.insert_one({"time":time_str,"result":self.execute_request()})
                self._requests.append(time.time())
                wait_for = np.random.normal(loc=delta_t,scale=delta_t*dev_ratio)
                if self.verbose:
                    print("A REQUEST was made!")
                    print("Sleeping for %.1f seconds" % wait_for)
                time.sleep(wait_for)
            else:
                time_diff = time.time() - self._requests[0]
                if time_diff > self.time_frame:
                    self._requests.popleft()
                    continue
                else:
                    if self.verbose:
                        print("Sleeping for %.1f seconds" % sync_time)
                    time.sleep(sync_time)
                    