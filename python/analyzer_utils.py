from search_utils import tweet_time_2_epoch

from pymongo import MongoClient
import networkx as nx
import pandas as pd

### mongodb ###

def get_coll(coll_name,mongo_port=27017,mongo_db="twitter-crawler"):
    client = MongoClient('mongodb://localhost:%i/' % mongo_port)
    db = client[mongo_db]
    return db[coll_name], db

def find_some_docs(coll,sort_params=[('id',-1)],limit=10):
    res = coll.find().sort(sort_params).limit(limit)
    for item in res:
        print(item["id"],item["created_at"])
        
        
### mention network ###

def get_mentions(coll,limit=None,use_only_tweets=True):
    res = coll.find().limit(limit) if limit != None else coll.find()
    num_tweets, num_retweets = 0, 0
    users = {}
    edges = []
    for item in res:
        if use_only_tweets and "RT " == item['text'][:3]:
            num_retweets += 1
            continue
        num_tweets += 1
        src_id, epoch = item['user']['id_str'], int(tweet_time_2_epoch(item['created_at']))
        users[src_id] = item['user']['name']
        if 'user_mentions' in item['entities']:
            for mention in item['entities']['user_mentions']:
                trg_id = mention['id_str']
                users[trg_id] = mention['name']
                msg = item["text"]
                edges.append((epoch,src_id,trg_id,msg))
    return edges, users, num_tweets, num_retweets

def show_frequent_items(df,user_names,col,k=10):
    val_counts = pd.DataFrame(df[col].value_counts()[:k])
    frequent_users = [user_names[u_id] for u_id in val_counts.index]
    res_df = pd.DataFrame()
    res_df["id"] = val_counts.index
    res_df["name"] = frequent_users
    res_df["count"] = val_counts.values
    return res_df

def get_graph_stats(df):
    edges = list(zip(df["src"],df["trg"]))
    G = nx.DiGraph()
    G.add_edges_from(edges)
    N = G.number_of_nodes()
    M = G.number_of_edges()
    wc_comp = nx.number_weakly_connected_components(G)
    sc_comp = nx.number_strongly_connected_components(G)
    return (N,M,wc_comp,sc_comp)
