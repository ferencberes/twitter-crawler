import time
import numpy as np
from collections import deque

class RequestScheduler():
    def __init__(self,time_frame,max_requests):
        self.time_frame = time_frame
        self.max_requests = max_requests
        self._requests = deque([])
        self._crawled_data = {}
        
    def execute_request(self):
        return None
        
    def run(self,delta_t,dev_ratio=0.2,sync_time=10):
        print("Started at: %s\n" % time.strftime("%b %d %Y %H:%M:%S",time.localtime()))
        while True:
            if len(self._requests) < self.max_requests:
                time_str = time.strftime("%b %d %Y %H:%M:%S",time.localtime())
                self._crawled_data[time_str] = self.execute_request()
                print("A REQUEST was made!")
                self._requests.append(time.time())
                wait_for = np.random.normal(loc=delta_t,scale=delta_t*dev_ratio)
                print("Sleeping for %.1f seconds" % wait_for)
                time.sleep(wait_for)
            else:
                time_diff = time.time() - self._requests[0]
                if time_diff > self.time_frame:
                    self._requests.popleft()
                    continue
                else:
                    print("Sleeping for %.1f seconds" % sync_time)
                    time.sleep(sync_time)
                    
    def get(self):
        return self._crawled_data