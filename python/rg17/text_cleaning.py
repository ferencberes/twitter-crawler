import contractions, nltk, unicodedata, re
from nltk.stem import SnowballStemmer, WordNetLemmatizer
import numpy as np

### Text Cleaning ###

def replace_contractions(text, verbose=False):
    """Replace contractions in string of text"""
    new_text = contractions.fix(text)
    if verbose:
        print(new_text)
    return new_text

def tokenization_and_lowercase(text, verbose=False):
    "Handle tokenization and lowercasing for words"
    words = nltk.word_tokenize(text)
    i = 0
    fixed_words = []
    while i < len(words):
        if words[i] == "@":
            # no lowercasing for mentions
            if i != len(words) - 1:
                fixed_words.append("@"+words[i+1])
            i += 2
        else:
            fixed_words.append(words[i].lower())
            i += 1
    if verbose:
        print(fixed_words)
    return fixed_words

def remove_non_ascii(words, verbose=False):
    """Remove non-ASCII characters from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)
    if verbose:
        print(new_words)
    return new_words

def remove_numbers(words, verbose=False):
    """Remove numbers from tokenized words"""
    new_words = []
    for word in words:
        if not word.isdigit():
            new_words.append(word)
    if verbose:
        print(new_words)
    return new_words

def remove_short_words(words, limit=1, verbose=False):
    """Remove short words from tokenized words"""
    new_words = []
    for word in words:
        if len(word) > limit:
            new_words.append(word)
    if verbose:
        print(new_words)
    return new_words


def remove_punctuation(words, verbose=False):
    """Remove punctuation from list of tokenized words. Mentions are enabled (due to Twitter text)"""
    new_words = []
    for word in words:
        new_word = re.sub(r'[^\w\s\@]', '', word)
        if new_word != '':
            new_words.append(new_word)
    return new_words

def remove_stopwords(words, stop_words, verbose=False):
    """Remove stop words from list of tokenized words"""
    new_words = []
    for word in words:
        if word not in stop_words:
            new_words.append(word)
    if verbose:
        print(new_words)
    return new_words

def stem_words(words, fixed_words=[], verbose=False):
    """Stem words in list of tokenized words. Do NOT stem mentions!"""
    stemmer = SnowballStemmer('english')
    stems = []
    for word in words:
        if "@" in word or word in fixed_words:
            stem = word
        else:
            stem = stemmer.stem(word)
        stems.append(stem)
    if verbose:
        print(stems)
    return stems

def lemmatize_words(words, fixed_words=[], verbose=False):
    """Lemmatize words in list of tokenized words"""
    lemmatizer = WordNetLemmatizer()
    lemmas = []
    for word in words:
        if word in fixed_words:
            lemma = word
        else:
            # lemmatize as noun
            lemma = lemmatizer.lemmatize(word,pos='n')
            # lemmatize as verb
            lemma = lemmatizer.lemmatize(lemma,pos='v')
        lemmas.append(lemma)
    if verbose:
        print(lemmas)
    return lemmas

def process_tweet_text(text, stop_words, fixed_words=[], use_stemming=False, verbose=False):
    """Clean and normalize Tweet text."""
    # format
    text = text.replace('\n',' ')
    text = replace_contractions(text, verbose=verbose)
    words = tokenization_and_lowercase(text, verbose=verbose)
    # cleaning
    cleaned_words = remove_non_ascii(words, verbose=verbose)
    cleaned_words = remove_punctuation(cleaned_words, verbose=verbose)
    cleaned_words = remove_stopwords(cleaned_words, stop_words, verbose=verbose)
    cleaned_words = remove_numbers(cleaned_words, verbose=verbose)
    cleaned_words = remove_short_words(cleaned_words, limit=2, verbose=verbose)
    # normalize
    if use_stemming:
        stemmed_words = stem_words(cleaned_words, fixed_words=fixed_words, verbose=verbose)
        return " ".join(stemmed_words)
    else:
        lemmatized_words = lemmatize_words(cleaned_words, fixed_words=fixed_words, verbose=verbose)
        return " ".join(lemmatized_words)

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
