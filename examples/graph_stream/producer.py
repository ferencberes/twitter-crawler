from twittercrawler.crawlers import TwythonStreamCrawler
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
    stream = TwythonStreamCrawler([sw], api_fp)

    # query
    search_params = {
        "q":'#BREAKING OR #BREAKINGNEWS OR #breakingnews',
        "lang":"en",
    }
    stream.set_search_arguments(search_args=search_params)

    # run stream search (pause for 0.5 second after each tweet) 
    try:
        # YOU MUST TERMINATE THIS SEARCH MANUALLY!
        stream.search()
    except:
        raise
    finally:
        stream.close()
