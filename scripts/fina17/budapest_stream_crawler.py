import sys

sys.path.insert(0,"../python/")
import search_utils as su
from twitter_crawler import TwitterCrawler

def main(time_frame, max_request_per_time_frame, mongo_coll,search_params, termination_function):
    tcs = TwitterCrawler(time_frame=time_frame,max_requests=max_request_per_time_frame)
    tcs.connect(mongo_coll)
    tcs.authenticate("../api_key.json")
    tcs.set_search_arguments(search_args=search_params)
    tcs.stream_search(delta_t=900, termination_func=termination_function,feedback_time=900)
    tcs.close()

if __name__ == "__main__":
    if not len(sys.argv) in [4,5]:
        print("Usage: <time_frame> <max_request_per_time_frame> <mongo_collection> <?since_id?>")
    else:
        # crawler parameters
        time_frame = int(sys.argv[1])
        max_request_per_time_frame = int(sys.argv[2])
        mongo_coll = sys.argv[3]

        # search parameters
        key_words = ["#budapest2017","#Budapest2017","#budapest","#Budapest"]
        key_words += ["budapest","Budapest"]
        
        query = " OR ".join(key_words)
        search_params = {
            "q":query,
            "result_type":'recent',
            "count":100
        }
            
        if len(sys.argv) == 4:
            print("NOTE: Termination function is based on time_stamp!!!")
            # termination function
            my_created_at="Sun Jun 25 23:59:59 +0000 2017"
            def my_time_bound_filter(tweet):
                return su.time_bound_filter(tweet, created_at=my_created_at)
            # run crawler
            main(time_frame, max_request_per_time_frame, mongo_coll, search_params, termination_function = my_time_bound_filter)   
        else:
            print("NOTE: Termination function is based on since_id!!!")
            # termination function
            my_since_id = int(sys.argv[4])
            def my_since_id_filter(tweet):
                return su.id_bound_fiter(tweet, since_id=my_since_id)
            # run crawler
            main(time_frame, max_request_per_time_frame, mongo_coll, search_params, termination_function = my_since_id_filter)