from twittercrawler.crawlers import PeopleCrawler
from twittercrawler.data_io import FileWriter, SocketWriter, FileReader

# prepare writers
keys = ["name","location","description"]
file_path = "people_results.txt"
fw = FileWriter(file_path, clear=True, include_mask=keys)
sw = SocketWriter(7000, include_mask=keys)
# execute this command in a bash console to continue: telnet localhost 7000

# initialize

people = PeopleCrawler(limit=5)
people.authenticate("../api_key.json")
people.connect_output([fw, sw])

# query
search_params = {
    "q":"data scientist AND phd student",
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