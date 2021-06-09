from twittercrawler.crawlers import StreamCrawler
from twittercrawler.data_io import SocketWriter
from twittercrawler.search import get_time_termination
import datetime, sys

if len(sys.argv) != 3:
    print("Usage: <twitter_api_key> <port>")
else:
    api_fp = sys.argv[1]
    port = int(sys.argv[2])

    # prepare writers
    sw = SocketWriter(port=port, export_filter="mention")

    # initialize crawler
    stream = StreamCrawler()
    stream.authenticate(api_fp)
    stream.connect_output([sw])

    # query
    search_params = {
        "q":'#BREAKING OR BREAKING OR "breaking news" OR breakingnews',
        "result_type":"recent",
        "count":100
    }
    stream.set_search_arguments(search_args=search_params)

    # termination (collect tweets from the last 5 minutes - THEN continue online)
    now = datetime.datetime.now()
    time_str = (now-datetime.timedelta(seconds=300)).strftime("%a %b %d %H:%M:%S +0000 %Y")
    print(time_str)
    time_terminator =  get_time_termination(time_str)

    # run search (after collecting latest tweets sleep for 15 seconds)
    try:
        stream.search(15, time_terminator) # YOU MUST TERMINATE THIS SEARCH MANUALLY!
    except:
        raise
    finally:
        stream.close()