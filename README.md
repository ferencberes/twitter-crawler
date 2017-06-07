twitter-crawler
============
A simple Twitter crawler is implemented in this repository. The crawler can search for events on Twitter with the help of [Twython](https://github.com/ryanmcgrath/twython). The crawled events are inserted into a [MongoDB](https://www.mongodb.com/) collection in order to be more accessible for further analysis.

Requirements
------------------
As the crawler inserts events into a MongoDB collection you need to be able to connect to a MongoDB database.

Here are the Python packages that this project depends on:

a.) Packages used in TwitterCrawler:

   * **twython**
   * **pymongo**
   * collections
   * numpy
   * datetime

b.) Packages only needed for the data analyzer notebook:

   * pandas
   * networkx
   * matplotlib


Usage
--------
This documentation haven't been finished yet. Until then you can find usage examples in this jupyter [notebook](ipython/Samples.ipynb).

###Authentication
TODO

###Setting search parameters
TODO

### Available search strategies
TODO
