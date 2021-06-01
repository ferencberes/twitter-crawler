from twittercrawler.data_io import *

sample_tweets = [
    {
        "id_str":199,
        "full_text":"abc",
        "user":{"screen_name":"john doe"}
    },
    {
        "id_str":200,
        "full_text":"def",
        "user":{"screen_name":"jane doe"}
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
    assert df.shape[1] == 3