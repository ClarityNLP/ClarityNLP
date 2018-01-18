"""
n-gram generator for Chart review

Usage python ngram.py <n_value> <lookup_term>

Google: nltk collocations for more filtering and approaches

"""


#import sys
#import re
import nltk
from nltk import word_tokenize
from nltk import sent_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.util import ngrams
from collections import Counter

#
# # Inputs for testing
# n = 4
# word = 'through'
#
# # For texting using text file.
# # TODO: Extract information from Solr
# with open('input.txt') as f:
#     text = f.read()
# f.close()
#
# if word:
#     #sentences = text.split('.')
#     sentences = nltk.sent_tokenize(text)
#     sentence_list = [x for x in sentences if word in x]
#     text = ''.join(sentence_list)
#
# #token = nltk.word_tokenize(text) #With Punctuations
# token = RegexpTokenizer(r'\w+') #without Punctuations
# token = token.tokenize(text)
# all_ngrams = ngrams(token, n)
#
# """
# Filterning ngrams which contain a keyword
# result = [x for x in all_ngrams if word in x]
# """
#
# # Printing ngrams and their frequences
# fdist = nltk.FreqDist(all_ngrams)
# for i,j in fdist.items():
#     if j>2:
#         print (i,j)



def extract_ngrams(cohort_id, keyword='NIL', n=3, frequency=1):
    # GET DATA
    # text = ?

    patient_url = 'https://bluebookshelf01.icl.gtri.org/cohortentities/%s/WebAPI' % cohort_id
    # for patient in patient_json
    #   patient_id = patient.personSourceValue
    #   document_url = 'https://bluebookshelf01.icl.gtri.org/subjectdocuments/%s/*:*' % patient_id
    #   Returns JSON object
    #   for doc in obj['documents']:
    #       text = doc['reportText']

    if keyword != 'NIL':
        sentences = nltk.sent_tokenize(text)
        sentence_list = [x for x in sentences if word in x]
        text = ''.join(sentence_list)

    token = RegexpTokenizer(r'\w+') #without Punctuations
    token = token.tokenize(text)
    all_ngrams = ngrams(token, n)

    result = []
    fdist = nltk.FreqDist(all_ngrams)
    for i,j in fdist.items():
        if j>frequency:
            result.append((i,j))

    return result
