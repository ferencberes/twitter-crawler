from twittercrawler.crawlers import PeopleCrawler
from twittercrawler.utils import load_json_result

# initialize
people = PeopleCrawler()
people.authenticate(None)#"../api_key.json")
people.connect_to_file("people_results.txt")

# query
search_params = {
    "q":"data scientist AND phd student"
}
people.set_search_arguments(search_args=search_params)

# run search
page, cnt = people.search()
print(page, cnt)

# close
people.close()

#load results
results = load_json_result("people_results.txt")
print("Hits:", len(results))
print(results[0]["name"])
