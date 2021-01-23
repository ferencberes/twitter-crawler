from collections import deque
import pandas as pd
import os, sys, shutil, traceback
from twittercrawler.replies.components import SearchEngine
from twittercrawler.replies.query import TweetQuery
from twittercrawler.replies.comet import init_experiment, load_api_key

class ReplyCollector():
    def __init__(self, engine, tweet_id, collector_dir, min_engagement=5, postpone_day_limit=3, action_day_limit=5, drop_day_limit=7, reload=True, renew_status=True):
        self.engine = engine
        self.tweet_id = tweet_id
        self.collector_dir = collector_dir
        self.reload = reload
        self.renew_status = renew_status
        self.min_engagement = min_engagement
        self.postpone_day_limit = postpone_day_limit
        self.action_day_limit = action_day_limit
        self.drop_day_limit = drop_day_limit
        self._clear()
        if self.reload:
            self.load()
        
    def _clear(self):
        self.seed_tweet = self.engine.get_status(self.tweet_id)
        if self.seed_tweet != None:
            self.tweet_thread = [self.seed_tweet]
            seed_query = TweetQuery(self.seed_tweet)
            self._queue = deque([seed_query])
            print("\n### SEED TWEET ###")
            print(self.seed_tweet['full_text'])
            print(seed_query)
            print()
        else:
            print("SEED TWEET NOT FOUND!")
            self.tweet_thread = []
            self._queue = deque([])
        self.active_tweet_ids = []
        
    def reset(self):
        shutil.rmtree(self.collector_dir)
        
    @property
    def params(self):
        return {
            "tweet_id":self.tweet_id,
            "collector_dir":self.collector_dir,
            "min_engagement":self.min_engagement,
            "postpone_day_limit":self.postpone_day_limit,
            "action_day_limit":self.action_day_limit,
            "drop_day_limit":self.drop_day_limit,
            "reload":self.reload,
            "renew_status":self.renew_status,
            "screen_name":self.seed_tweet["user"]["screen_name"] if self.seed_tweet != None else None,
            "user_id":self.seed_tweet["user"]["id_str"] if self.seed_tweet != None else None,
        }
        
    @property
    def queue(self):
        return self._queue
    
    @property
    def size(self):
        return len(self.queue)
    
    @property
    def active_queries(self):
        return [q for q in self.queue if (q.priority > 0 and q.engagements > self.min_engagement)]
    
    @property
    def collector_dir(self):
        return self._collector_dir
    
    @collector_dir.setter
    def collector_dir(self, value):
        dir_path = os.path.join(value, self.tweet_id)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        self._collector_dir = dir_path
        
    @property
    def thread_fp(self):
        return os.path.join(self.collector_dir, "thread.csv")
    
    @property
    def queue_fp(self):
        return os.path.join(self.collector_dir, "queue.csv")
    
    @property
    def status(self):
        return {
            "total_queries": self.size,
            "remaining_queries": len(self.active_queries),
            "seed_tweet_id": self.tweet_id,
        }
    
    def _save_thread(self):
        df = pd.DataFrame(self.tweet_thread)
        df.to_csv(self.thread_fp, index=False)
        
    def _save_queue(self):
        df = pd.DataFrame([q.get() for q in self.queue])
        df.to_csv(self.queue_fp, index=False)
    
    def save(self):
        self.engine.store.save()
        self._save_thread()
        self._save_queue()
        
    def _load_thread(self):
        if os.path.exists(self.thread_fp):
            thread = []
            df = pd.read_csv(self.thread_fp)
            for idx, row in df.iterrows():
                thread.append(dict(row))
            self.tweet_thread += thread
        
    def _load_queue(self):
        if os.path.exists(self.queue_fp):
            queries = []
            df = pd.read_csv(self.queue_fp)
            for idx, row in df.iterrows():
                q = TweetQuery()
                q.load(row)
                queries.append(q)
            self._queue = deque(queries)
        
    def load(self):
        self._load_thread()
        self._load_queue()
        self._sort_queries()
        print("Collector was LOADED from this folder: %s" % self.collector_dir)
    
    def _sort_queries(self):
        self._queue = deque(sorted(self._queue, key=lambda x: x.priority, reverse=True))
        
    def _decide_execution(self, query):
        if query.elapsed_days < self.postpone_day_limit:
            execute_now = False
        #elif query.elapsed_days >= self.action_day_limit:
        #    # here we try to catch the begining of each thread
        #    execute_now = True
        else:
            if query.engagements >= self.min_engagement:
                execute_now = True
            else:
                execute_now = False
        return execute_now
        
    def run(self, feedback_interval=10, max_requests=100, comet_info=None):
        def make_checkpoint():
            if comet_info != None:
                exp.log_metrics(self.status, step=j)
                exp.log_metric("executed_queries", i, step=j)
            x.append(j)
            y_exec.append(i)
            y_total.append(self.status["total_queries"])
            y_remain.append(self.status["remaining_queries"])
            print("\n### STATUS ###")
            print("Executed queries: %i" % i)
            print(self.status)
            print()
        x, y_total, y_remain, y_exec = [], [], [], []
        if comet_info != None:
            api_key_fp, project, workspace = comet_info
            api_key = load_api_key(api_key_fp)
            exp = init_experiment(api_key, project, workspace)
            if self.seed_tweet != None:
                seed_query = TweetQuery(self.seed_tweet)
                exp.add_tag(seed_query.date_str)
            else:
                exp.add_tag("Failed")
            exp.log_parameters(self.params)
        try:
            print("\n### SEED ###")
            print(self.params)
            if self.seed_tweet != None:
                print(self.seed_tweet["full_text"])
                if comet_info != None:
                    exp.log_text(self.seed_tweet["full_text"])
            i, j = 0, 0
            make_checkpoint()
            while len(self.queue) > 0:
                j += 1
                query = self.queue.popleft()
                if query.priority == 0:
                    self._queue.appendleft(query)
                    break
                if self.renew_status and query.accessed_since_days > -1:
                    new_status = self.engine.get_status(query.id)
                    if new_status != None:
                        query.update_metrics(new_status)
                execute_now = self._decide_execution(query)
                if execute_now:
                    print(query)
                    success, new_query, replies = self.engine.execute(query)
                    print(query.id,len(replies))
                    self.tweet_thread += replies
                    for reply in replies:
                        q = TweetQuery(reply)
                        if not q.id in self.active_tweet_ids:
                            self._queue.append(q)
                    if new_query.elapsed_days < self.drop_day_limit or not success:
                        self._queue.append(new_query)
                    self._sort_queries()
                    #if not success:
                    #    break
                    i += 1
                else:
                    self._queue.append(query)
                self.save()
                if j % feedback_interval == 0:
                    make_checkpoint()
                if i >= max_requests:
                    print("Exiting at %i executed queries!" % max_requests)
                    break
            make_checkpoint()
        except KeyboardInterrupt:
            print('Interrupted')
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
        except Exception:
            traceback.print_exc()
            print()
            if comet_info != None:
                exp.add_tag("Failed")
        finally:
            if comet_info != None:
                df = pd.DataFrame(list(zip(x,y_exec,y_remain,y_total)), columns=["step","executed","remaining","total"])
                exp.log_table("step_metrics.csv",tabular_data=df,headers=True)
                exp.end()