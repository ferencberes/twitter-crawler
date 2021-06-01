import json, twython, time, traceback
from twython import Twython
from .scheduler import *
from .utils import load_credentials
from twython.exceptions import TwythonAuthError, TwythonError

class Crawler(RequestScheduler):    
    
    def __init__(self, time_frame, max_requests, sync_time, limit, verbose=False):
        """Twitter API scheduler object. It enables only 'max_requests' requests in every 'time_frame' seconds."""
        super(Crawler, self).__init__(time_frame, max_requests , sync_time, verbose)
        self.twitter_api = None
        self._msg = ""
        self._limit = limit
        self._start_time, self._last_feedback = None, None
        
    def authenticate(self, auth_file_path=None):
        """Authenticate application with Twython."""
        success = False
        config = load_credentials(["api_key","api_secret","access_token","access_token_secret"], auth_file_path)
        try:
            self.twitter_api = Twython(config["api_key"], config["api_secret"], config["access_token"], config["access_token_secret"])
            print("Authentication was successful!")
            success = True
        except:
            raise
        finally:
            return success
        
    def _show_time_diff(self):
        current_time = time.time()
        print("### FEEDBACK ###")
        td = datetime.timedelta(seconds=current_time-self._start_time)
        print(self._msg + " is RUNNING since: %i days, %i hours and %i minutes %i seconds" % (td.days, td.seconds//3600, (td.seconds//60)%60, td.seconds%60))
        self._last_feedback = current_time
        
    def _terminate(self, increment=True):
        if increment:
            self._num_requests += 1
        return self._limit != None and self._num_requests >= self._limit

    def _export(self, results):
        if self._writers == None:
            raise RuntimeError("You did not specify any output for your search! Use the connect_output() function!")
        else:
            for writer in self._writers:
                writer.write(results)

class UserLookup(Crawler):
    def __init__(self, time_frame=900, max_requests=300, sync_time=15, limit=None, verbose=False):
        super(UserLookup, self).__init__(time_frame, max_requests , sync_time, limit, verbose)
        
    def collect(self, user_ids=None, screen_names=None, from_index=None, offset=100, wait_for=2, feedback_time=15*60):
        def stringify(l):
            return ','.join([str(val) for val in l])
        self._num_requests, cnt = 0, 0
        self._start_time, self._last_feedback = time.time(), time.time()
        if user_ids == None and screen_names == None:
            raise RuntimeError("Specify the list of user IDs or screen names!")
        else:
            is_ids = user_ids != None
            items = user_ids if is_ids else screen_names
            if from_index != None:
                items = items[from_index:]
            queries = [stringify(items[i:i+offset]) for i in range(0,len(items),offset)]
        for q_idx, query in enumerate(queries):
            # verify
            _ = self._verify_new_request(self.twitter_api)
            # new request
            try:
                self._register_request(delta_t=wait_for)
                if is_ids:
                    res = self.twitter_api.lookup_user(user_id=query)
                else:
                    res = self.twitter_api.lookup_user(screen_name=query)
                # postprocess
                cnt += len(res)
                self._export(res)
            except TwythonAuthError:
               # This error can occur when some ids are not available!
               print("TwythonAuthError", query)
            except TwythonError:
                # This error can occur when some ids are not available!
                print("TwythonError", query)
            except:
                raise
            if self._terminate():
                    break
        return q_idx*offset, cnt
                
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
        for u_id in user_id_list:
            has_more = True
            while has_more:
                # feedback
                if time.time() - self._last_feedback > feedback_time:
                    self._show_time_diff()
                print("type: %s, user_id: %s, cursor: %s" % (str(self._network_type), str(u_id), str(cursor)))
                # verify
                _ = self._verify_new_request(self.twitter_api)
                # new request
                try:
                    self._register_request(delta_t=wait_for)
                    if self._network_type == "friend":
                        res = self.twitter_api.get_friends_ids(user_id=u_id, cursor=cursor)
                    else:
                        res = self.twitter_api.get_follower_ids(user_id=u_id, cursor=cursor)
                except TwythonAuthError:
                   # This error can occur when the node is not available!
                    print(u_id, "TwythonAuthError")
                    break
                except TwythonError:
                    print(u_id, "TwythonError")
                    break
                except:
                    raise
                # postprocess
                new_links = []
                for node in res["ids"]:
                    if self._network_type == "friend":
                        new_links.append({"source":u_id, "target":node})
                    else:
                        new_links.append({"target":u_id, "source":node})
                if len(new_links) > 0:
                    cnt += len(new_links)
                    self._export(new_links)
                if res["next_cursor"] == 0:
                    cursor = -1
                    has_more = False
                else:
                    cursor = res["next_cursor"]
                if self._terminate():
                    break
            if self._terminate(False):
                break
        return u_id, cursor, cnt
                
class SearchCrawler(Crawler):    
    def __init__(self, time_frame, max_requests, sync_time, limit, only_geo=False, verbose=False):
        super(SearchCrawler, self).__init__(time_frame, max_requests, sync_time, limit, verbose)
        self.only_geo = only_geo
        if self.only_geo:
            print("Only geotagged tweets are exported!")
            
    def set_search_arguments(self,search_args):
        """Set search parameters with a dictionary"""
        self.search_args = search_args
        print(self.search_args)
          
    def _search_by_query(self, wait_for, current_max_id=0, custom_since_id=None, term_func=None, feedback_time=15*60):
        if "max_id" in self.search_args:
            del self.search_args["max_id"]
        if "since_id" in self.search_args:
            del self.search_args["since_id"]
        success = True
        prev_max_id = -1
        latest_id = -1
        cnt = 0
        try:
            while current_max_id != prev_max_id:
                result_tweets = []

                # feedback
                if time.time() - self._last_feedback > feedback_time:
                    self._show_time_diff()
                    print("max_id: %s, since_id: %s, latest_id: %s" % (str(current_max_id), str(custom_since_id), str(latest_id)))
                stop_search = False            
                if current_max_id > 0:
                    self.search_args["max_id"] = current_max_id-1
                if custom_since_id != None:
                    self.search_args["since_id"] = custom_since_id
                
                _ = self._verify_new_request(self.twitter_api)
                tweets = self.twitter_api.search(**self.search_args)
                self._register_request(delta_t=wait_for)
                
                prev_max_id = current_max_id
                
                for tweet in tweets['statuses']:
                    tweet_id = int(tweet['id'])
                    if custom_since_id == None or tweet_id >= custom_since_id:
                        skip_record = self.only_geo and tweet["geo"] == None
                        if not skip_record:
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
                self._export(result_tweets)
                cnt += len(result_tweets)

                if stop_search:
                    break
                if self._terminate():
                    break
        except twython.exceptions.TwythonRateLimitError:
            traceback.print_exc()
            print()
            try:
                current_time = time.time()
                _, wait_for = self._check_remaining_limit(self.twitter_api, current_time)
                print("RATE LIMIT RESET in %.1f seconds" % wait_for)
                time.sleep(wait_for)
            except Exception as e:
                traceback.print_exc()
                print("SLEEPING for 900 seconds!")
                time.sleep(901)
            success = False
        except Exception:
            raise
        finally:
            return success, current_max_id, latest_id, cnt
