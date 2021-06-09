from twittercrawler.data_io import SocketReader
import sys

if len(sys.argv) != 2:
    print("Usage: <port>")
else:
    port = int(sys.argv[1])
    reader = SocketReader(port=port)
    try:
        for tweet in reader.read():
            ts = tweet["created_at"]
            tweet_id = tweet["id_str"]
            source_user = tweet["user"]["screen_name"]
            if "entities" in tweet and "user_mentions" in tweet["entities"]:
                for mention_obj in tweet["entities"]["user_mentions"]:
                    target_user = mention_obj["screen_name"]
                    record = {
                        "time":ts,
                        "tweet_id":tweet_id,
                        "source":source_user,
                        "target":target_user
                    }
                    print(record)
    except:
        raise
    finally:
        reader.close()