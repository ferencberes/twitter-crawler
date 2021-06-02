from twittercrawler.crawlers import RecursiveCrawler
from twittercrawler.data_io import FileWriter, FileReader
from twittercrawler.search import get_time_termination, get_id_termination
import datetime, time

# initialize
file_path = "recursive_results.txt"
recursive = RecursiveCrawler()
recursive.authenticate("../api_key.json")
recursive.connect_output([FileWriter(file_path, clear=True)])

# query
search_params = {
    "q":"#bitcoin OR #ethereum OR blockchain",
    "result_type":"recent",
    "lang":"en",
    "count":100
}
recursive.set_search_arguments(search_args=search_params)

# termination (collect tweets from the last 5 minutes)
now = datetime.datetime.now()
time_str = (now-datetime.timedelta(seconds=300)).strftime("%a %b %d %H:%M:%S +0000 %Y")
print(time_str)
time_terminator =  get_time_termination(time_str)

# run search - FIRST STAGE
success, max_id, latest_id, cnt = recursive.search(term_func=time_terminator)
print("\nFirst stage report:")
print(success, max_id, latest_id, cnt)

# wait for 5 minutes
print("\nSleeping for 5 minutes...")
time.sleep(5*60)

# NEW termination (collect only new tweets)
id_terminator =  get_id_termination(latest_id)

# NEW search - SECOND STAGE
success, new_max_id, new_latest_id, new_cnt = recursive.search(term_func=id_terminator)
print("\nSecond stage report:")
print(success, new_max_id, new_latest_id, new_cnt)

# close
recursive.close()

# load results
results_df = FileReader(file_path).read()
print("\nTotal hits:", len(results_df))
print(results_df.loc[0])