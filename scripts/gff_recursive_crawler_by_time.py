import sys

sys.path.insert(0,"../python/")
import search_utils as su
from twitter_crawler import TwitterCrawler

def main(time_frame, max_request_per_time_frame, mongo_coll,search_params, max_id, termination_function):
    tcs = TwitterCrawler(time_frame=time_frame,max_requests=max_request_per_time_frame)
    tcs.connect(mongo_coll)
    tcs.authenticate("../api_key.json")
    tcs.set_search_arguments(search_args=search_params)
    tcs.search_by_query(wait_for=3, current_max_id=max_id, term_func=termination_function)
    tcs.close()

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: <time_frame> <max_request_per_time_frame> <mongo_collection> <max_id>")
    else:
        # crawler parameters
        time_frame = int(sys.argv[1])
        max_request_per_time_frame = int(sys.argv[2])
        mongo_coll = sys.argv[3]
        my_max_id = int(sys.argv[4])
        
        # termination function
        my_created_at="Mon Jun 12 23:59:59 +0000 2017"
        def my_time_bound_filter(tweet):
            return su.time_bound_filter(tweet, created_at=my_created_at)
        
        # termination function
        my_since_id = 875383689844318208
        def my_since_id_filter(tweet):
            return su.id_bound_fiter(tweet, since_id=my_since_id)
        
        # search parameters
        htag_list_1 = ["#londonfire", "#Londonfire", "#LondonFire", "#grenfelltower", "#Grenfelltower", "#GrenfellTower", "#grenfell", "#Grenfell",  "#grenfelltowerfire", "#GrenfellTowerFire", "#GrenfellFire", "#Grenfellfire", "#grenfellfire", "#GlenfellTower", "#Glenfelltower", "#glenfelltower"]
        htag_list_2 = ["#prayforlondon", "#PrayForLondon", "#GreenfellTower", "#londonfirebrigade", "#LondonFireBrigade", "#bedsforgrenfell", "#WestLondonFire", "#GrenFellTower", "#justice4grenfell", "#Justice4Grenfell", "#JUSTICE4Grenfell"]
        #htag_list_total = htag_list_1 + htag_list_2 
        
        query = " OR ".join(htag_list_2)
        search_params = {
            "q":query,
            "result_type":'recent',
            "count":100
        }
        
        # run crawler
        #main(time_frame, max_request_per_time_frame, mongo_coll, search_params, my_max_id, termination_function=my_time_bound_filter)
        main(time_frame, max_request_per_time_frame, mongo_coll, search_params, my_max_id, termination_function=my_since_id_filter)
        