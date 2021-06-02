from twittercrawler.crawlers import PeopleCrawler
from twittercrawler.data_io import FileWriter, FileReader

# initialize
file_path = "people_results.txt"
people = PeopleCrawler(limit=10)
people.authenticate("../api_key.json")
people.connect_output([FileWriter(file_path, clear=True)])

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
results_df = FileReader(file_path).read()
print("Hits:", len(results_df))
print(results_df.loc[0])