"""
n-gram generator for Chart review

Usage python ngram.py <n_value> <lookup_term>

"""


import sys
import re
import nltk
from nltk import word_tokenize
from nltk import sent_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.util import ngrams
from collections import Counter


# Inputs for testing
n = 2
word = None

# For texting using text file.
# TODO: Extract information from Solr
with open('input.txt') as f:
    text = f.read()
f.close()

if word:
    sentences = text.split('.')
    sentence_list = [x for x in sentences if word in x]
    text = ''.join(sentence_list)

#token = nltk.word_tokenize(text) #With Punctuations
token = RegexpTokenizer(r'\w+') #without Punctuations
token = token.tokenize(text)
all_ngrams = ngrams(token, n)

"""
Filterning ngrams which contain a keyword
result = [x for x in all_ngrams if word in x]
"""

# Printing ngrams and their frequences
fdist = nltk.FreqDist(all_ngrams)
for i,j in fdist.items():
    if j>1:
        print (i,j)
