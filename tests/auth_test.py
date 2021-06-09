import os
from twittercrawler.crawlers import StreamCrawler
from twittercrawler.utils import prepare_credentials

dirpath = os.path.dirname(os.path.realpath(__file__))
api_key_file_path = os.path.join(dirpath, "..", "api_key.json")
keys = ["api_key","api_secret","access_token","access_token_secret"]
prepare_credentials(keys, api_key_file_path)

def test_api_key():
    if api_key_file_path == None:
        assert True
    else:
        assert os.path.exists(api_key_file_path)

def test_json_auth():
    crawler = StreamCrawler()
    assert crawler.authenticate(api_key_file_path)
    
def test_env_auth():
    crawler = StreamCrawler()
    assert crawler.authenticate(None)