from twittercrawler.data_io import SocketReader
import sys

def listen_for_news(port, hide_accounts=True):
    reader = SocketReader(port=port)
    try:
        for tweet in reader.read():
            ts = tweet["created_at"]
            tweet_id = tweet["id_str"]
            source = tweet["user"]["id_str"] if hide_accounts else tweet["user"]["screen_name"]
            if "entities" in tweet and "user_mentions" in tweet["entities"]:
                for mention_obj in tweet["entities"]["user_mentions"]:
                    target = mention_obj["id_str"] if hide_accounts else mention_obj["screen_name"]
                    record = {
                        "time":ts,
                        "tweet_id":tweet_id,
                        "source":source,
                        "target":target
                    }
                    print(record)
    except:
        raise
    finally:
        reader.close()
        
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: <port> <hide_screen_name?>")
    else:
        port = int(sys.argv[1])
        if len(sys.argv) >= 3:
            hide_accounts = sys.argv[2]=="True"
        else:
            hide_accounts = True
        listen_for_news(port, hide_accounts)