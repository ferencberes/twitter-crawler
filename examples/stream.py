from twittercrawler.crawlers import StreamCrawler
from twittercrawler.data_io import FileWriter, FileReader
from twittercrawler.search import get_time_termination
import datetime

# initialize
file_path = "stream_results.txt"
stream = StreamCrawler()
stream.authenticate("../api_key.json")
stream.connect_output([FileWriter(file_path, clear=True)])

# query
search_params = {
    "q":"#bitcoin OR #ethereum OR blockchain",
    "result_type":"recent",
    "lang":"en",
    "count":100
}
stream.set_search_arguments(search_args=search_params)

# termination (collect tweets from the last 5 minutes - THEN continue online)
now = datetime.datetime.now()
time_str = (now-datetime.timedelta(seconds=300)).strftime("%a %b %d %H:%M:%S +0000 %Y")
print(time_str)
time_terminator =  get_time_termination(time_str)

# run search (after collecting latest tweets sleep for 15 seconds)
stream.search(15, time_terminator) # YOU MUST TERMINATE THIS SEARCH MANUALLY!