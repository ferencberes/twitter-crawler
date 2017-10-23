import pandas as pd
import gensim, os, json

def transform_account_name(acc_name, remove_digits, remove_under_score, to_lower):
    result = acc_name
    if to_lower:
        result = result.lower()
    if remove_under_score:
        result = result.replace("_","")
    if remove_digits:
        result = ''.join([i for i in result if not i.isdigit()])
    return result
    
def load_player_accounts(file_path, remove_digits=False, remove_under_score=False, to_lower=False):
    """Return player accounts with some text transformation. 'file_path' is the file that contains the screen_names of the players."""
    with open(file_path) as f:
        filtered_screen_names = json.load(f)
    result = ["@" + n  for n in filtered_screen_names]
    result = [transform_account_name(n, remove_digits=remove_digits, remove_under_score=remove_under_score, to_lower=to_lower) for n in result]
    return result

def get_toplist(pair_occs_df, key_words, snapshot_ids, score_col="occ_score"):
    """Get occurences for the given keywords in multiple snapshots. 
    If more than 1 snapshot id is specified then there could be duplications in the data!"""
    filtered_df = pair_occs_df[(pair_occs_df["word_1"].isin(key_words)) & pair_occs_df["time"].isin(snapshot_ids)]
    return filtered_df.sort_values(score_col, ascending=False)

def get_toplist_with_max_scores(pair_occs_df, key_words, snapshot_ids, score_col="occ_score"):
    """Get occurences for the given keywords in multiple snapshots. 
    If more than 1 snapshot id is specified then only the occurances with maximum score is kept from he duplicated items."""
    df = get_toplist(pair_occs_df, key_words, snapshot_ids, score_col=score_col)
    return df.groupby(by=["word_1","word_2"])[score_col].max().reset_index().sort_values(score_col, ascending=False)


### Word2Vec ###

def load_w2v_models(w2v_model_dir):
    """Load w2v models trained for snapshots"""
    model_names = os.listdir(w2v_model_dir)
    w2v_models = {}
    for m in model_names:
        snapshot_id = m.split(".")[0]
        w2v_models[snapshot_id] = gensim.models.Word2Vec.load("%s/%s" % (w2v_model_dir, m))
    return w2v_models

def w2v_query(w2v_models, key_word, snapshot_id, top_k=None):
    """Handle w2v model request for only one key word and snapshot id."""
    out = pd.DataFrame()
    try:
        model = w2v_models[snapshot_id]
        if top_k == None:
            top_k = len(model.wv.vocab)
        if key_word in  model.wv.vocab:
            res = model.most_similar(positive=[key_word], topn=top_k)
        else:
            res = []
        out = pd.DataFrame(res, columns=["word_2","w2v_score"])
        out["word_1"] = key_word
        out["time"] = snapshot_id
        out = out[["time","word_1","word_2","w2v_score"]]
    except:
        raise
    finally:
        return out

def get_w2v_toplist(w2v_models, key_words, snapshot_ids, top_k):
    """Get most similar words based on word2vec. 
    If more than 1 snapshot id is specified then there could be duplications in the data!"""
    dfs = [w2v_query(w2v_models, kw, sid, top_k) for kw in key_words for sid in snapshot_ids]
    return pd.concat(dfs).sort_values("w2v_score", ascending=False)
