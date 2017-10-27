from nltk.stem.snowball import SnowballStemmer
import re

def clean_text(t):
    """Remove non-alphabetical characters + remove commans and numbers"""
    # get only alphabetical words + full mentions
    clean_1 = ' '.join(re.findall("[\w,\@,']+",t))
    # remove numbers and comma
    clean_2 = ' '.join(re.findall("[^\,]+",clean_1))
    return clean_2.lower()

def get_words_above_size_limit(t, size_limit):
    """Get list of words above the provided size limit"""
    words = []
    for w in t.split():
        if len(w) > size_limit:
            words.append(w)
    return words

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
        words = re.findall(pattern,text)
        if remove_hashtag:
            return [self.remove_hashtag(self.stem_word(w)) for w in words]
        else:
            return [self.stem_word(w) for w in words]
        