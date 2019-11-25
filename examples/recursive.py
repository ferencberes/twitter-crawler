from twittercrawler.crawlers import RecursiveCrawler
from twittercrawler.search import get_time_termination, get_id_termination
from twittercrawler.utils import load_json_result
import datetime, time

# initialize
recursive = RecursiveCrawler()
recursive.authenticate("../api_key.json")
recursive.connect_to_file("recursive_results.txt")

# query
search_params = {
    "q":"#bitcoin OR #ethereum",
    "result_type":'recent',
    "count":100
}
recursive.set_search_arguments(search_args=search_params)

# termination (collect tweets from the last 5 minutes)
now = datetime.datetime.now()
time_str = (now-datetime.timedelta(seconds=300)).strftime("%a %b %d %H:%M:%S +0000 %Y")
print(time_str)
time_terminator =  get_time_termination(time_str)

# run search - FIRST STAGE
max_id, latest_id, cnt = recursive.search(term_func=time_terminator)
print(max_id, latest_id, cnt)

# wait for 5 minutes
time.sleep(5*60)

# NEW termination (collect only new tweets)
id_terminator =  get_id_termination(max_id)

# NEW search - SECOND STAGE
new_max_id, new_latest_id, new_cnt = recursive.search(term_func=time_terminator)
print(new_max_id, new_latest_id, new_cnt)

# close
recursive.close()

# load results
results = load_json_result("recursive_results.txt")
print("Hits:", len(results))
print(results[0]["text"])