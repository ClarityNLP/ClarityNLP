"""
n-gram generator for Chart review

Usage localhost:5000/ngram?cohort_id=1&keyword=test&n=5&frequency=3

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
import urllib.request
import urllib.parse
import requests

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


#r = requests.get('https://api.github.com/events')

# cohort_id = '6'
# url = 'https://bluebookshelf01.icl.gtri.org/cohortentities/%s/WebAPI' %(cohort_id)
# #r = requests.get('https://bluebookshelf01.icl.gtri.org/cohortentities/6/WebAPI', verify=False)
# r = requests.get(url, verify=False)
# q = r.json()
# temp = q[0]['demographics']
# subID = temp['personSourceValue']
# #for i in q:
# # i = q[0]
# # t = str(i['personSourceValue'])
# total_text = ""
# flag = 1
# for i in q:
#     flag = 2
#     temp = i['demographics']
#     subID = temp['personSourceValue']
#
#     url2 = 'https://bluebookshelf01.icl.gtri.org/subjectdocuments/%s/*:*' %(subID)
#     r2 = requests.get(url2, verify=False)
#     doc_json = r2.json()
#
#     for doc in doc_json['documents']:
#         total_text += doc['reportText']
#
#     if flag == 2:
#         break
#
# token = RegexpTokenizer(r'\w+') #without Punctuations
# token = token.tokenize(total_text)
# all_ngrams = ngrams(token, 2)
#
# result = []
# fdist = nltk.FreqDist(all_ngrams)
# for i,j in fdist.items():
#     if j>9:
#         result.append(str((i,j)))
#
# for i in result:
#     print (i)


def extract_ngrams(cohort_id, keyword='NIL', n=5, frequency=3):
    # GET DATA
    # text = ?
    url = 'https://bluebookshelf01.icl.gtri.org/cohortentities/%s/WebAPI' %(cohort_id)
    r = requests.get(url, verify=False)
    q = r.json()
    text = ""
    for i in q:
        temp = i['demographics']
        subID = temp['personSourceValue']

        url2 = 'https://bluebookshelf01.icl.gtri.org/subjectdocuments/%s/*:*' %(subID)
        r2 = requests.get(url2, verify=False)
        doc_json = r2.json()

        for doc in doc_json['documents']:
            text += doc['reportText']

    #patient_url = 'https://bluebookshelf01.icl.gtri.org/cohortentities/%s/WebAPI' % cohort_id
    # for patient in patient_json
    #   patient_id = patient.personSourceValue
    #   document_url = 'https://bluebookshelf01.icl.gtri.org/subjectdocuments/%s/*:*' % patient_id
    #   Returns JSON object
    #   for doc in obj['documents']:
    #       text = doc['reportText']


    if keyword != None:
        sentences = nltk.sent_tokenize(text)
        sentence_list = [x for x in sentences if keyword in x]
        text = ''.join(sentence_list)

    token = RegexpTokenizer(r'\w+') #without Punctuations
    token = token.tokenize(text)
    all_ngrams = ngrams(token, n)

    result = []
    fdist = nltk.FreqDist(all_ngrams)
    for i,j in fdist.items():
        if j>frequency:
            result.append(str((i,j)))
            print ((i,j))

    return result


#extract_ngrams('6',None,5,9)
