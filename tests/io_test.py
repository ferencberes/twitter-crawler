from twittercrawler.data_io import *
import pytest, time

sample_tweets = [
    {
        "id_str":"199",
        "full_text":"abc",
        "lang":"en",
        "user":{"screen_name":"john doe"},
        "created_at": "Wed Jun 02 11:43:27 +0000 2021",
        "entities": {
            "user_mentions": [
            ],
        }
    },
    {
        "id_str":"200",
        "full_text":"@ferencberes91 uses @twitterapi often",
        "lang":"es",
        "user":{"screen_name":"jane doe"},
        "created_at": "Wed Jun 02 11:45:33 +0000 2021",
        "entities": {
            "user_mentions": [
                {
                  "name": "Twitter API",
                  "screen_name": "twitterapi",
                  "id_str": "6253282"
                },
                {
                  "name": "Ferenc Beres",
                  "screen_name": "ferencberes91",
                  "id_str": "6253000"
                }
            ],
        }
    },
    {
        "id_str":"201",
        "full_text":"RT abs",
        "lang":"en",
        "user":{"screen_name":"jane doe"},
        "created_at": "Wed Jun 02 11:46:27 +0000 2021",
        "entities": {},
        "retweeted_status":{
            "id_str":"199",
            "full_text":"abc",
            "lang":"en",
            "user":{"screen_name":"john doe"},
            "created_at": "Wed Jun 02 11:43:27 +0000 2021",
            "entities": {
                "user_mentions": [
                ],
            }
        }
    },
    
]
test_file = "log.txt"

def test_file_io():
    writer = FileWriter(test_file, clear=True)
    writer.write(sample_tweets)
    writer.close()
    reader = FileReader(test_file)
    df = reader.read()
    assert len(df) == 3
    assert df.shape[1] == 7
    
def test_file_io_again():
    writer = FileWriter(test_file)
    writer.write(sample_tweets)
    writer.close()
    reader = FileReader(test_file)
    df = reader.read()
    assert len(df) == 6
    assert df.shape[1] == 7
    
def test_file_io_include():
    writer = FileWriter(test_file, clear=True, include_mask=["id_str","lang","full_text"])
    writer.write(sample_tweets)
    writer.close()
    reader = FileReader(test_file)
    df = reader.read()
    assert len(df) == 3
    assert df.shape[1] == 3
    
def test_file_io_exclude():
    writer = FileWriter(test_file, clear=True, exclude_mask=["user"])
    writer.write(sample_tweets)
    writer.close()
    reader = FileReader(test_file)
    df = reader.read()
    assert len(df) == 3
    assert df.shape[1] == 6
    
def test_invalid_filter():
    with pytest.raises(ValueError):
        writer = FileWriter(test_file, export_filter="all")
        
def test_tweet_filter():
    writer = FileWriter(test_file, clear=True, export_filter="tweet")
    writer.write(sample_tweets)
    writer.close()
    reader = FileReader(test_file)
    df = reader.read()
    assert len(df) == 2
    
def test_mention_filter():
    writer = FileWriter(test_file, clear=True, export_filter="mention")
    writer.write(sample_tweets)
    writer.close()
    reader = FileReader(test_file)
    df = reader.read()
    assert len(df) == 1
    
def test_retweet_filter():
    writer = FileWriter(test_file, clear=True, export_filter="retweet")
    writer.write(sample_tweets)
    writer.close()
    reader = FileReader(test_file)
    df = reader.read()
    assert len(df) == 1
    
def test_quote_filter():
    writer = FileWriter(test_file, clear=True, export_filter="quote")
    writer.write(sample_tweets)
    writer.close()
    reader = FileReader(test_file)
    df = reader.read()
    assert len(df) == 0
    
def start_socket_server(port):
    server = SocketWriter(port)
    server.write(sample_tweets)
    server.close()
    
def test_socket_io():
    from multiprocessing import Process
    port = 7000
    p = Process(target=start_socket_server, args=(port,))
    p.start()
    time.sleep(3)
    client = SocketReader(port)
    received_records = [msg for msg in client.read()]
    client.close()
    assert len(received_records) == len(sample_tweets)
    
"""
def test_kafka_io():
    topic, host, port = "sample", "localhost", 9092 
    success = False
    try:
        reader = KafkaReader(topic, host, port)
        writer = KafkaWriter(topic, host, port)
        writer.write(sample_tweets)
        #cnt = 0
        #for message in reader.consumer:
        #    cnt += 1
        #assert cnt > 0
        writer.close()
        reader.close()
        success = True
    except:
        raise
    assert success
"""