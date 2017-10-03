from search_utils import tweet_time_2_epoch

from pymongo import MongoClient
import networkx as nx
import pandas as pd
import numpy as np

from matplotlib import pyplot as plt
from bokeh.plotting import figure, show
from bokeh.palettes import Category20

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

### visualization ###

def filter_for_support(popularity_df, min_times=0, max_times=30):
    name_counts = popularity_df["name"].value_counts()
    filtered_names = list(name_counts[(name_counts >= min_times) & (name_counts <= max_times)].index)
    f_popular_trg_df = popularity_df[popularity_df["name"].isin(filtered_names)]
    return f_popular_trg_df
    
def plot_user_popularity(df, day_list):
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(111)
    names_in_pop_order = list(df["name"].value_counts().index)
    for name in names_in_pop_order:
        if name == "Roland-Garros":
            continue
        item = df[df["name"]==name]
        x, y = item["day_idx"], item["count"]
        ax.plot(x,y,marker='x',markersize=10,label=name)
    plt.xticks(range(len(day_list)),day_list,rotation='vertical')
    plt.xlabel("days")
    #plt.legend()
    handles, labels = ax.get_legend_handles_labels()
    lgd = ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(1.2,1.0))
    ax.grid('on')
    plt.show()

def stacked(df, categories):
    areas = dict()
    last = np.zeros(len(df[categories[0]]))
    for cat in categories:
        next = last + df[cat]
        areas[cat] = np.hstack((last[::-1], next))
        last = next
    return areas

def create_pivot(very_pop_df):
    pop_pivot_df = pd.pivot_table(very_pop_df,values="dominance",index=["day_idx"],columns=["name"])
    pop_pivot_df = pop_pivot_df.fillna(0.0)
    if "Roland-Garros" in pop_pivot_df.columns:
        del pop_pivot_df["Roland-Garros"]
    return pop_pivot_df

def plot_user_dominance(df):
    pop_pivot_df = create_pivot(df)
    index = pop_pivot_df.index
    categories = list(pop_pivot_df.columns)
    areas = stacked(pop_pivot_df, categories)
    colors = Category20[len(areas)]
    x2 = np.hstack((index[::-1], index))
    p = figure()
    p.grid.minor_grid_line_color = '#eeeeee'
    p.patches([x2] * len(areas), [areas[cat] for cat in categories],
          color=colors, alpha=0.8, line_color=None)
    show(p)
    return show_colors_for_users(categories, colors)

def show_colors_for_users(categories,colors):
    def color(col):
        return ["background-color: %s" % val for val in col]
    legend_df = pd.DataFrame(list(zip(categories,colors)),columns=["name","color"])
    return legend_df.style.apply(color)

### export ###

def recode_and_export_mentions(fname,mentions_df,user_names,epoch_lower_bound=None, epoch_upper_bound=None):
    dir_name = "/".join(fname.split("/")[:-1])
    recoder_map = dict(zip(user_names.keys(),range(1,len(user_names)+1)))
    with open("%s/rg17_recoder_map.txt" % dir_name,"w") as f:
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
