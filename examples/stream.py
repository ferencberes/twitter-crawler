from twittercrawler.crawlers import StreamCrawler
from twittercrawler.search import get_time_termination
from twittercrawler.utils import load_json_result
import datetime

# initialize
stream = StreamCrawler()
stream.authenticate("../api_key.json")
stream.connect_to_file("stream_results.txt")

# query
search_params = {
    "q":"#bitcoin OR #ethereum",
    "result_type":'recent',
    "count":100
}
stream.set_search_arguments(search_args=search_params)

# termination (collect tweets from the last minute - THEN continue online)
now = datetime.datetime.now()
time_str = (now-datetime.timedelta(seconds=60)).strftime("%a %b %d %H:%M:%S +0000 %Y")
print(time_str)
time_terminator =  get_time_termination(time_str)

# run search (after collecting latest tweets sleep for 300 seconds)
stream.search(300, time_terminator) # YOU MUST TERMINATE THIS SEARCH MANUALLY!

# close
stream.close()

# load results
results = load_json_result("stream_results.txt")
print("Hits:", len(results))
print(results[0]["text"])