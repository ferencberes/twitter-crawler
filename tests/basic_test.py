import os, sys, json
#from twittercrawler.base import UserLookup
from twittercrawler.crawlers import *
from twittercrawler.utils import load_json_result, prepare_credentials

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
"""    
def test_recursive():
    crawler = RecursiveCrawler(limit=2)
    crawler.authenticate(api_key_file_path)
    crawler.connect_to_file("recursive_results.txt")
    search_params = {
    "q":"#latest OR #news",
    "result_type":'recent',
    "count":5
    }
    crawler.set_search_arguments(search_args=search_params)
    success, max_id, latest_id, cnt = crawler.search(term_func=None)
    crawler.close()
    os.remove("recursive_results.txt")
    assert (success and cnt > 0)

def test_stream():
    crawler = StreamCrawler(sync_time=1, limit=10)
    crawler.authenticate(api_key_file_path)
    crawler.connect_to_file("stream_results.txt")
    search_params = {
    "q":"#latest OR #news",
    "result_type":'recent',
    "count":5
    }
    crawler.set_search_arguments(search_args=search_params)
    crawler.search(90, None)
    crawler.close()
    results = load_json_result("stream_results.txt")
    os.remove("stream_results.txt")
    assert len(results) > 0

def test_people():
    crawler = PeopleCrawler(limit=2)
    crawler.authenticate(api_key_file_path)
    crawler.connect_to_file("people_results.txt")
    search_params = {
    "q":"data scientist"
    }
    crawler.set_search_arguments(search_args=search_params)
    page, cnt = crawler.search()
    crawler.close()
    os.remove("people_results.txt")
    assert cnt > 0

def test_lookup():
    crawler = UserLookup()
    crawler.authenticate(api_key_file_path)
    crawler.connect_to_file("lookup_results.txt")
    query_idx, cnt = crawler.collect(screen_names=["ferencberes91","Istvan_A_Seres"])
    crawler.close()
    os.remove("lookup_results.txt")
    assert cnt > 0
    
def test_friends():
    crawler = FriendsCollector(limit=1)
    crawler.authenticate(api_key_file_path)
    crawler.connect_to_file("friends_results.txt")
    user_id, cursor, cnt = crawler.collect([187908577, 34156194, 66003384, 19248625])
    crawler.close()
    os.remove("friends_results.txt")
    assert cnt > 0
"""