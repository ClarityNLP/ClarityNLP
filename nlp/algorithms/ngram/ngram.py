"""
n-gram generator for Chart review
Usage localhost:5000/ngram?cohort_id=1&keyword=test&n=5&frequency=3
Google: nltk collocations for more filtering and approaches
"""


#import sys
#import re
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.util import ngrams
import requests
# import sys
# import re
import nltk
import requests
from nltk.tokenize import RegexpTokenizer
from nltk.util import ngrams
from claritynlp_logging import log, ERROR, DEBUG


def extract_ngrams(cohort_id, keyword='NIL', n=5, frequency=3):
    url = 'https://bluebookshelf01.icl.gtri.org/cohortentities/%s/WebAPI' % cohort_id
    r = requests.get(url, verify=False)
    q = r.json()
    text = ""
    for i in q:
        temp = i['demographics']
        subID = temp['personSourceValue']

        url2 = 'https://bluebookshelf01.icl.gtri.org/subjectdocuments/%s/*:*' % subID
        r2 = requests.get(url2, verify=False)
        doc_json = r2.json()

        for doc in doc_json['documents']:
            text += doc['reportText']

    if keyword:
        sentences = nltk.sent_tokenize(text)
        sentence_list = [x for x in sentences if keyword in x]
        text = ''.join(sentence_list)

    token = RegexpTokenizer(r'\w+') #without Punctuations
    token = token.tokenize(text.lower())
    all_ngrams = ngrams(token, n)

    result = []
    fdist = nltk.FreqDist(all_ngrams)
    for i, j in fdist.items():
        if j > frequency:
            gram = ' '.join(i)
            freq = str(j)
            if gram and freq:
                formatted = "'%s',%s" % (gram, freq)
                result.append(formatted)

    log("\n".join(result))
    return result
