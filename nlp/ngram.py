"""
n-gram generator for Chart review
"""


import sys
import nltk
from nltk import word_tokenize
from nltk.util import ngrams
from collections import Counter


# For texting using text file.
# TODO: Extract information from Solr
with open('input.txt') as f:
    text = f.read()
f.close()

# Extracting n-gram
token = nltk.word_tokenize(text)
n = int(sys.argv[1])
n_grams = ngrams(token, n)


# Printing logs
res = Counter(n_grams)
print(res)
