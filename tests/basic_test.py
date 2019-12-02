import os, sys
from twittercrawler.crawlers import *
from twittercrawler.utils import load_json_result

api_key_file_path = "../api_key.json"

def test_api_key():
    os.path.exists(api_key_file_path)
    
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
    max_id, latest_id, cnt = crawler.search(term_func=None)
    crawler.close()
    os.remove("recursive_results.txt")
    assert cnt > 0
    
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

def test_friends():
    crawler = FriendsCollector(limit=1)
    crawler.authenticate(api_key_file_path)
    crawler.connect_to_file("friends_results.txt")
    user_id, cursor, cnt = crawler.collect([187908577, 34156194, 66003384, 19248625])
    crawler.close()
    os.remove("friends_results.txt")
    assert cnt > 0