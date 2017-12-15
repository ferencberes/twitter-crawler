import numpy as np

def get_word2_frequency_factor(df, norm_const = 5, log_base = 10):
    word_2_counts = df.groupby(by=["word_2"])["date"].count()
    freq_factor = np.floor(np.log(word_2_counts / norm_const) / np.log(log_base))
    return freq_factor

def calculate_frequency_val(df, freq_factor):
    df["frequency_val"] = df["word_2"].apply(lambda word: 0.0 if freq_factor[word] < 1 else 1.0 / freq_factor[word])

def calculate_r(df, snapshot_weight, frequency_weight):
    global_weight = (1.0 - (snapshot_weight + frequency_weight))
    df["r"] = global_weight * df["global_val"] + snapshot_weight * df["snapshot_val"] + frequency_weight * df["frequency_val"]

def calculate_rel_count(df, c=0.0):
    df["numerator"] = df["word_2_count"] + df["r"] * c
    df["denominator"] = df["word_1_count"] + c
    df["rel_count_c%i" % c] = df["numerator"] / df["denominator"]
    df = df.drop(["numerator", "denominator"], axis=1)
    
def calculate_norm(df, c=0.0):
    df["norm_c%i" % c] = df["rel_count_c%i" % c] / df["r"]
    