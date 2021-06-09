import os
from twittercrawler.crawlers import *
from twittercrawler.utils import prepare_credentials
from twittercrawler.data_io import FileWriter, FileReader

dirpath = os.path.dirname(os.path.realpath(__file__))
api_key_file_path = os.path.join(dirpath, "..", "api_key.json")
keys = ["api_key","api_secret","access_token","access_token_secret"]
prepare_credentials(keys, api_key_file_path)

def test_recursive():
    fp = "recursive_results.txt"
    crawler = RecursiveCrawler(limit=2)
    crawler.authenticate(api_key_file_path)
    crawler.connect_output([FileWriter(fp, clear=True)])
    search_params = {
    "q":"#latest OR #news",
    "result_type":'recent',
    "count":5
    }
    crawler.set_search_arguments(search_args=search_params)
    success, max_id, latest_id, cnt = crawler.search(term_func=None)
    crawler.close()
    os.remove(fp)
    assert (success and cnt > 0)

def test_stream():
    fp = "stream_results.txt"
    crawler = StreamCrawler(sync_time=1, limit=10)
    crawler.authenticate(api_key_file_path)
    crawler.connect_output([FileWriter(fp, clear=True)])
    search_params = {
    "q":"#latest OR #news",
    "result_type":'recent',
    "count":5
    }
    crawler.set_search_arguments(search_args=search_params)
    crawler.search(90, None)
    crawler.close()
    results = FileReader(fp).read()
    os.remove(fp)
    assert len(results) > 0

def test_people():
    fp = "people_results.txt"
    crawler = PeopleCrawler(limit=2)
    crawler.authenticate(api_key_file_path)
    crawler.connect_output([FileWriter(fp, clear=True)])
    search_params = {
    "q":"data scientist"
    }
    crawler.set_search_arguments(search_args=search_params)
    page, cnt = crawler.search()
    crawler.close()
    os.remove(fp)
    assert cnt > 0

def test_lookup():
    fp = "lookup_results.txt"
    crawler = UserLookup()
    crawler.authenticate(api_key_file_path)
    crawler.connect_output([FileWriter(fp, clear=True)])
    query_idx, cnt = crawler.collect(screen_names=["ferencberes91","Istvan_A_Seres"])
    crawler.close()
    os.remove(fp)
    assert cnt > 0
    
def test_friends():
    fp = "friends_results.txt"
    crawler = FriendsCollector(limit=1)
    crawler.authenticate(api_key_file_path)
    crawler.connect_output([FileWriter(fp, clear=True)])
    user_id, cursor, cnt = crawler.collect([187908577, 34156194, 66003384, 19248625])
    crawler.close()
    os.remove(fp)
    assert cnt > 0