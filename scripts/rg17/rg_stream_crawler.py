import sys

sys.path.insert(0,"../python/")
import search_utils as su
from twitter_crawler import TwitterCrawler

def main(time_frame, max_request_per_time_frame, mongo_coll,search_params, termination_function):
    tcs = TwitterCrawler(time_frame=time_frame,max_requests=max_request_per_time_frame)
    tcs.connect(mongo_coll)
    tcs.authenticate("../api_key.json")
    tcs.set_search_arguments(search_args=search_params)
    tcs.stream_search(delta_t=120, termination_func=termination_function,feedback_time=300)
    tcs.close()

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: <time_frame> <max_request_per_time_frame> <mongo_collection> <since_id>")
    else:
        # crawler parameters
        time_frame = int(sys.argv[1])
        max_request_per_time_frame = int(sys.argv[2])
        mongo_coll = sys.argv[3]
        my_since_id = int(sys.argv[4])
        
        # termination function
        def my_since_id_filter(tweet):
            return su.id_bound_fiter(tweet, since_id=my_since_id)
        
        # search parameters
        query = " OR ".join(["#FrenchOpen", "#frenchopen", "#RG17", "#rg17", "#RolandGarros2017", "#rolandgarros2017", "#RolandGarros", "#rolandgarros", "@rolandgarros"])
        search_params = {
            "q":query,
            "result_type":'recent',
            "count":100
        }
        
        # run crawler
        main(time_frame,max_request_per_time_frame,mongo_coll,search_params,termination_function=my_since_id_filter)
        