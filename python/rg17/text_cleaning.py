from nltk.stem.snowball import SnowballStemmer
import re
import numpy as np
import pandas as pd

### Text Cleaning ### 

def clean_text(t, pattern="[\w,\@,',\#]+"):
    """Remove non-alphabetical characters + remove commas"""
    # get only alphabetical words + full mentions
    clean_1 = ' '.join(re.findall(pattern,t))
    # remove comma
    clean_2 = ' '.join(re.findall("[^\,]+",clean_1))
    return clean_2.lower()

def get_words_above_size_limit(t, size_limit):
    """Get list of words above the provided size limit"""
    words = []
    for w in t.split():
        if len(w) > size_limit:
            words.append(w)
    return words


### Stemming ###

class CustomStemmer:
    def __init__(self, fixed_words, lang):
        self._stemmer = SnowballStemmer(lang)
        self.fixed_words = [w.lower() for w in fixed_words]
        
    def stem_word(self, word):
        do_stem = True
        if "@" in word:
            do_stem = False
        elif "#" in word:
            do_stem = False
        else:
            do_stem = not word.lower() in self.fixed_words
        return self._stemmer.stem(word) if do_stem else word
    
    def remove_hashtag(self, word):
        has_hashtag = False
        if "#" == word[0]:
            has_hashtag = True
        return word[1:] if has_hashtag else word
        
    def stem_words(self, text, remove_hashtag=True, pattern="[\w,\@,',\#]+"):
        words = clean_text(text, pattern=pattern).split()
        if remove_hashtag:
            return [self.remove_hashtag(self.stem_word(w)) for w in words]
        else:
            return [self.stem_word(w) for w in words]

### Cleaning Combined Occurences ###

def clean_line(x):
    """Cleaning raw line of combined occurences input file"""
    out = x
    try:
        for pattern in ["Some(","List(","(",")"," "]:
            if pattern in out:
                out = out.replace(pattern,"")
    except:
        print(x)
        raise
    return out

def get_occurences_data_frame(file_path, num_cols):
    """Load combined occurences file into DataFrame with cleaning"""
    raw_rows = []
    with open(file_path) as f:
        i = 0
        for line in f:
            i += 1
            c_line = clean_line(line.rstrip())
            splitted = c_line.split(",")
            if len(splitted) < 5 or int(splitted[4]) == 0:
                # no combined occurences
                continue
            row = list(np.nan for j in range(num_cols))
            row[:len(splitted)] = splitted
            raw_rows.append(tuple(row))
    return pd.DataFrame(raw_rows)
