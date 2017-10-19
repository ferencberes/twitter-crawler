import pandas as pd
import json

def transform_account_name(acc_name, remove_digits, remove_under_score, to_lower):
    result = acc_name
    if to_lower:
        result = result.lower()
    if remove_under_score:
        result = result.replace("_","")
    if remove_digits:
        result = ''.join([i for i in result if not i.isdigit()])
    return result
    
def load_player_accounts(remove_digits=False, remove_under_score=False, to_lower=False):
    """Return player accounts with some text transformation"""
    file_name = "/mnt/idms/fberes/network/online_ranker/roland_garros_updated_schedule/filtered_true_matches_screen_names.json"
    with open(file_name) as f:
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
