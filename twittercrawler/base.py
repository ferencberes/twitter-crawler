import json, twython, time
from twython import Twython
from .scheduler import *


class Crawler(RequestScheduler):    
    
    def __init__(self, time_frame, max_requests, sync_time, limit, verbose=False):
        """Twitter API scheduler object. It enables only 'max_requests' requests in every 'time_frame' seconds."""
        super(Crawler, self).__init__(time_frame, max_requests , sync_time, verbose)
        self.twitter_api = None
        self._msg = ""
        self._limit = limit
        self._start_time, self._last_feedback = None, None
        
    def authenticate(self,auth_file_path):
        """Authenticate application with Twython."""
        try:
            with open(auth_file_path,"r") as f:
                auth_info = json.load(f)
            self.twitter_api = Twython(auth_info["api_key"], auth_info["api_secret"], auth_info["access_token"], auth_info["access_token_secret"])
            print("Authentication was successful!")
        except:
            raise
        
    def _show_time_diff(self):
        current_time = time.time()
        print("### FEEDBACK ###")
        td = datetime.timedelta(seconds=current_time-self._start_time)
        print(self._msg + " is RUNNING since: %i days, %i hours and %i minutes %i seconds" % (td.days, td.seconds//3600, (td.seconds//60)%60, td.seconds%60))
        self._last_feedback = current_time
        #print("################")
        
    def _terminate(self, increment=True):
        if increment:
            self._num_requests += 1
        return self._limit != None and self._num_requests >= self._limit

    def _export_to_output_framework(self, results):
        for res in results:
            try:
                if self._connection_type == "mongo":
                    self._mongo_coll.insert_one(res)
                elif self._connection_type == "file":
                    self._output_file.write("%s\n" % json.dumps(res))
                else:
                    raise RuntimeError("You did not specify any output for your search! Use connect_to_mongodb() ot connect_to_file() functions!")
            except Exception as err:
                print("ERROR occured:", str(err))
                
class NetworkCrawler(Crawler):
    def __init__(self, network_type, time_frame, max_requests, sync_time, limit, verbose=False):
        super(NetworkCrawler, self).__init__(time_frame, max_requests , sync_time, limit, verbose)
        if network_type in ["friend","follower"]:
            self._network_type = network_type
        else:
            raise RuntimeError("Choose 'network_type' parameter from values 'friend' or 'follower'!")

    def collect(self, user_ids, from_user=None, from_cursor=-1, wait_for=2, feedback_time=15*60):
        self._num_requests, cnt = 0, 0
        self._start_time, self._last_feedback = time.time(), time.time()
        cursor = from_cursor
        if from_user != None:
            idx = user_ids.index(from_user)
            user_id_list = user_ids[idx:]
        else:
            user_id_list = user_ids
        try:
            for u_id in user_id_list:
                has_more = True
                while has_more:
                    # feedback
                    if time.time() - self._last_feedback > feedback_time:
                        self._show_time_diff()
                    print("type: %s, user_id: %s, cursor: %s" % (str(self._network_type), str(u_id), str(cursor)))
                    # verify
                    _ = self._verify_new_request()
                    # new request
                    if self._network_type == "friend":
                        res = self.twitter_api.get_friends_ids(user_id=u_id, cursor=cursor)
                    else:
                        res = self.twitter_api.get_follower_ids(user_id=u_id, cursor=cursor)
                    self._register_request(delta_t=wait_for)
                    # postprocess
                    new_links = []
                    for node in res["ids"]:
                        if self._network_type == "friend":
                            new_links.append({"source":u_id, "target":node})
                        else:
                            new_links.append({"target":u_id, "source":node})
                    if len(new_links) > 0:
                        cnt += len(new_links)
                        self._export_to_output_framework(new_links)
                    if res["next_cursor"] == 0:
                        cursor = -1
                        has_more = False
                    else:
                        cursor = res["next_cursor"]
                    if self._terminate():
                        break
                if self._terminate(False):
                    break
        except twython.exceptions.TwythonRateLimitError:
            raise
        except Exception as exc:
            raise
        return u_id, cursor, cnt
                
class SearchCrawler(Crawler):    
    
    def __init__(self, time_frame, max_requests, sync_time, limit, verbose=False):
        super(SearchCrawler, self).__init__(time_frame, max_requests, sync_time, limit, verbose)
            
    def set_search_arguments(self,search_args):
        """Set search parameters with a dictionary"""
        self.search_args = search_args
        print(self.search_args)
          
    def _search_by_query(self, wait_for, current_max_id=0, custom_since_id=None, term_func=None, feedback_time=15*60):
        if "max_id" in self.search_args:
            del self.search_args["max_id"]
        if "since_id" in self.search_args:
            del self.search_args["since_id"]
        
        prev_max_id = -1
        latest_id = -1
        cnt = 0
        while current_max_id != prev_max_id:
            result_tweets = []
            
            # feedback
            if time.time() - self._last_feedback > feedback_time:
                self._show_time_diff()
                print("max_id: %s, since_id: %s, latest_id: %s" % (str(current_max_id), str(custom_since_id), str(latest_id)))
                
            stop_search = False
            try:
                if current_max_id > 0:
                    self.search_args["max_id"] = current_max_id-1
                if custom_since_id != None:
                    self.search_args["since_id"] = custom_since_id
                
                _ = self._verify_new_request()
                tweets = self.twitter_api.search(**self.search_args)
                self._register_request(delta_t=wait_for)
                
                prev_max_id = current_max_id
                
                for tweet in tweets['statuses']:
                    tweet_id = int(tweet['id'])
                    if custom_since_id == None or tweet_id >= custom_since_id:
                        result_tweets.append(tweet)
                    if current_max_id == 0 or current_max_id > tweet_id:
                        current_max_id = tweet_id
                    if latest_id < tweet_id:
                        latest_id = tweet_id
                    if term_func != None and term_func(tweet):
                        stop_search = True
                        break

                #no new tweets found
                if (prev_max_id == current_max_id):
                    stop_search = True
                    
                #last tweet found above since_id
                if custom_since_id != None and current_max_id <= custom_since_id + 1:
                    stop_search = True

                # export tweets
                self._export_to_output_framework(result_tweets)
                cnt += len(result_tweets)

                if stop_search:
                    break
                if self._terminate():
                    break
            except twython.exceptions.TwythonRateLimitError:
                raise
            except Exception as exc:
                raise
        return current_max_id, latest_id, cnt