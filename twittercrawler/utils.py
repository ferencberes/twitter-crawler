from .search import tweet_time_2_epoch#
from pymongo import MongoClient
import networkx as nx
import pandas as pd
import numpy as np
import json, os

### authentication ###

def load_credentials(keys, auth_file_path=None):
    values = []
    if auth_file_path != None:
        with open(auth_file_path,"r") as f:
            auth_info = json.load(f)                
            values = [auth_info.get(key, None) for key in keys]
    else:
        values = [os.getenv(key.upper()) for key in keys]
    config = dict(zip(keys, values))
    for key, val in config.items():
        if val == None:
            if auth_file_path != None:
                raise ValueError("'%s' key is missing from the JSON config file: '%s'" % (key, auth_file_path))
            else:
                raise ValueError("'%s' environmental variable is missing!" % missing_key.upper())
    return config  

def prepare_credentials(keys, api_key_file_path):
    if os.path.exists(api_key_file_path):
        with open(api_key_file_path) as f:
            config = json.load(f)
        for key in keys:
            os.environ[key.upper()] = config[key]
    else:
        config = load_credentials(keys, None)
        with open(api_key_file_path, 'w') as f:
            json.dump(config, f)

### json ###

def load_json_result(file_name):
    messages = []
    with open(file_name) as f:
        for line in f:
            messages.append(json.loads(line.rstrip()))
    return messages

### mongodb ###

def get_coll(coll_name,mongo_port=27017,mongo_db="twitter-crawler"):
    client = MongoClient('mongodb://localhost:%i/' % mongo_port)
    db = client[mongo_db]
    return db[coll_name], db

def find_some_docs(coll,sort_params=[('id',-1)],limit=10):
    res = coll.find().sort(sort_params).limit(limit)
    for item in res:
        print(item["id"],item["created_at"])

### tweets ###

def get_text_with_no_urls(doc):
    text = doc["text"]
    # cut all urls from the text
    for url_item in doc['entities']['urls']:
        splitted = text.split(url_item['url'])
        text = ''.join(splitted)
    # url can occur in under 'media' key as well!
    if 'media' in doc['entities']:
        for url_item in doc['entities']['media']:
            splitted = text.split(url_item['url'])
            text = ''.join(splitted)
    return text

def get_tweets(coll,limit=None, without_urls=False):
    res = coll.find().limit(limit) if limit != None else coll.find()
    tweet_info = []
    for item in res:
        if "RT " == item['text'][:3]:
            continue
        src_id, src_name = item['user']['id_str'], item['user']['name']
        time = int(tweet_time_2_epoch(item['created_at']))
        tweet_id, msg, lang = item["id_str"], item["text"], item["lang"]
        if without_urls:
            msg = get_text_with_no_urls(item)
        tweet_info.append((tweet_id, time, src_id, src_name, lang, msg.replace("\n"," ")))
    return tweet_info
        
### mention network ###

def get_mentions(coll,limit=None,use_only_tweets=True):
    res = coll.find().limit(limit) if limit != None else coll.find()
    num_tweets, num_retweets = 0, 0
    user_names, user_screen_names = {}, {}
    edges = []
    for item in res:
        if use_only_tweets and "RT " == item['text'][:3]:
            num_retweets += 1
            continue
        num_tweets += 1
        src_id, epoch = item['user']['id_str'], int(tweet_time_2_epoch(item['created_at']))
        user_names[src_id] = item['user']['name']
        user_screen_names[src_id] = item['user']['screen_name']
        msg, lang = item["text"], item["lang"]
        if 'user_mentions' in item['entities']:
            for mention in item['entities']['user_mentions']:
                trg_id = mention['id_str']
                user_names[trg_id] = mention['name']
                user_screen_names[trg_id] = mention['screen_name']
                edges.append((epoch,src_id,trg_id,lang,msg.replace("\n"," ")))
    return edges, user_names, user_screen_names, num_tweets, num_retweets

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

### export ###

def recode_and_export_mentions(fname,mentions_df,user_names,epoch_lower_bound=None, epoch_upper_bound=None):
    dir_name = "/".join(fname.split("/")[:-1])
    data_id = fname.split("/")[-2]
    recoder_map = dict(zip(user_names.keys(),range(1,len(user_names)+1)))
    with open("%s/%s_recoder_map.txt" % (dir_name,data_id),"w") as f:
        f.write("generated_id original_id\n")
        for item in recoder_map.items():
            f.write("%i %s\n" % (item[1],item[0]))
    recoded_mentions_df = mentions_df[["epoch","src","trg"]].copy()
    recoded_mentions_df["src"] = recoded_mentions_df["src"].apply(lambda x: recoder_map[x])
    recoded_mentions_df["trg"] = recoded_mentions_df["trg"].apply(lambda x: recoder_map[x])
    if epoch_lower_bound != None:
        length_before_lower_cut = len(recoded_mentions_df)
        recoded_mentions_df = recoded_mentions_df[recoded_mentions_df["epoch"] > epoch_lower_bound]
        print(length_before_lower_cut, len(recoded_mentions_df))
    if epoch_upper_bound != None:
        length_before_upper_cut = len(recoded_mentions_df)
        recoded_mentions_df = recoded_mentions_df[recoded_mentions_df["epoch"] < epoch_upper_bound]
        print(length_before_upper_cut, len(recoded_mentions_df))
    recoded_mentions_df.to_csv(fname, sep=" ", header=False, index=False)
