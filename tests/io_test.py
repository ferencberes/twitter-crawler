from twittercrawler.data_io import *

sample_tweets = [
    {
        "id_str":"199",
        "full_text":"abc",
        "lang":"en",
        "user":{"screen_name":"john doe"},
        "created_at": "Wed Jun 02 11:43:27 +0000 2021"
    },
    {
        "id_str":"200",
        "full_text":"def",
        "lang":"es",
        "user":{"screen_name":"jane doe"},
        "created_at": "Wed Jun 02 11:45:33 +0000 2021"
    },
]
test_file = "log.txt"

def test_file_io():
    writer = FileWriter(test_file, clear=True)
    writer.write(sample_tweets)
    writer.close()
    reader = FileReader(test_file)
    df = reader.read()
    assert len(df) == 2
    
def test_file_io_again():
    writer = FileWriter(test_file)
    writer.write(sample_tweets)
    writer.close()
    reader = FileReader(test_file)
    df = reader.read()
    assert len(df) == 4
    assert df.shape[1] == 5
    
def test_file_io_include():
    writer = FileWriter(test_file, clear=True, include_mask=["id_str","lang","full_text"])
    writer.write(sample_tweets)
    writer.close()
    reader = FileReader(test_file)
    df = reader.read()
    assert len(df) == 2
    assert df.shape[1] == 3
    
def test_file_io_exclude():
    writer = FileWriter(test_file, clear=True, exclude_mask=["user"])
    writer.write(sample_tweets)
    writer.close()
    reader = FileReader(test_file)
    df = reader.read()
    assert len(df) == 2
    assert df.shape[1] == 4
    
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