from twittercrawler.data_io import *
import pytest, time, json

test_file = "log.txt"
dirpath = os.path.dirname(os.path.realpath(__file__))
json_fp = os.path.join(dirpath, "sample_tweets.json")
with open(json_fp) as f:
    sample_tweets = json.load(f)

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
        cnt = 0
        #execution halts here
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