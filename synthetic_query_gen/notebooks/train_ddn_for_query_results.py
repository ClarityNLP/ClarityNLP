from sklearn.model_selection import cross_validate
from sklearn.metrics.scorer import make_scorer
from sklearn.metrics import confusion_matrix
from sklearn.neural_network import MLPClassifier
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import sys
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
#import seaborn as sns
#from gensim.models import Doc2Vec
#import psycopg2
#from config import config
import sys
#from urllib import request
#from urllib.parse import quote
#import simplejson
import requests
#import traceback
import sys
from collections import OrderedDict
import json
import pysolr
import sklearn
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import urllib
import json
import math
import pickle
from joblib import dump, load


def get_doc_term_matrix(notesdf):
    vectorizer = CountVectorizer(lowercase=True, stop_words="english")
    #vectorizer = TfidfVectorizer(lowercase=True, stop_words="english")
    X = vectorizer.fit_transform(notesdf.loc[:, 'text'])   
    
    with open('trained_vectorizer.pk', 'wb') as fin:
        pickle.dump(vectorizer, fin)
    return X

def train_and_test_dnn(args):
    
    for a in args:
        print(a)
    
    primitive = args[1]
    res =  pickle.load(open(sys.argv[2], "rb" ))
    notes_with_truth_labels_for_query_primitives = pd.read_csv(args[3])
   
    dl_results = pd.DataFrame(columns = ['primitive', 'avg_fit_time', 'avg_score_time', 'avg_score'])
    
    X = get_doc_term_matrix(res)
    y = notes_with_truth_labels_for_query_primitives.loc[:, primitive]

    clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(128, 5, 2), random_state=1)

    try:

        sm = SMOTE(random_state=357)
        X_sm, y_sm = sm.fit_sample(X, y)

    except ValueError:
        print("value error, smote")
        X_sm = X
        y_sm = y

    cv_results = cross_validate(clf, X_sm, y_sm, cv=3, return_train_score=False)
    print(cv_results)

    dump(clf, './models/{}_trained_dnn.joblib'.format(primitive)) 

    dl_results.loc[0, 'primitive'] = primitive
    dl_results.loc[0, 'avg_fit_time'] = np.mean(cv_results['fit_time'])
    dl_results.loc[0, 'avg_score_time'] = np.mean(cv_results['score_time'])
    dl_results.loc[0, 'avg_test_score'] = np.mean(cv_results['test_score'])

    with open(args[4], 'a') as f:
        f.write("{}, {}, {}, {}\n".format(dl_results.loc[0,'primitive'], dl_results.loc[0,'avg_fit_time'], dl_results.loc[0,'avg_score_time'], dl_results.loc[0,'avg_test_score']))
        #f.write(dl_results.loc[0,:])
        #f.write("\n")
        f.close()
    
    print("DONE w/ {}".format(primitive))
    
if __name__=="__main__":
    
    # need to ingest: primitive, textdf; truth_labelsdf, output_df    
    train_and_test_dnn(sys.argv)



