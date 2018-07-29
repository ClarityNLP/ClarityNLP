#!/usr/bin/env python3
"""
"""

import re
import os
import sys
import json
import spacy
import optparse
from collections import namedtuple
from nltk.stem.porter import PorterStemmer

VERSION_MAJOR = 0
VERSION_MINOR = 1

# serializable result object
EMPTY_FIELD = None
NEGAIT_RESULT_FIELDS = ['sentence',
                        'morphological_negation_list',
                        'sentential_negation_list',
                        'double_negation_list'
]
NegaitResult = namedtuple('NegaitResult', NEGAIT_RESULT_FIELDS)


# load Spacy's English model
nlp = spacy.load('en')

stemmer = PorterStemmer()

STEMMED_TOKEN_FIELDS = ['token', 'stem']
StemmedToken = namedtuple('StemmedToken', STEMMED_TOKEN_FIELDS)

MODULE_NAME = 'negait.py'

ACCEPT_FILE = 'accept.txt'
REJECT_FILE = 'reject.txt'

accept_set = set()
reject_set = set()

###############################################################################
def print_token(token):
    """
    Print useful token data to the screen for debugging.
    """

    print('[{0:3}]: {1:30}\t{2:6}\t{3:8}\t{4:12}\t{5}'.format(token.i,
                                                              token.text,
                                                              token.tag_,
                                                              token.pos_,
                                                              token.dep_,
                                                              token.head))


###############################################################################
def print_tokens(doc):
    """
    Print all tokens in a SpaCy document.
    """

    print('\nTokens: ')
    print('{0:7}{1:30}\t{2:6}\t{3:8}\t{4:12}\t{5}'.format('INDEX', 'TOKEN', 'TAG',
                                                          'POS', 'DEP', 'HEAD'))
    for token in doc:
        print_token(token)


###############################################################################
def to_json(original_sentence, morph_results, sent_results, double_results):
    """
    Convert the results to a JSON string.
    """

    return (morph_results, sent_results, double_results)


###############################################################################
def init():
    """
    Load the accept and reject sets, build internal data structures.

    Word lists are all lowercase; files contain non-ascii chars, some digits,
    duplicates, and other junk.

    First word in each line of the accept list has been Porter stemmed.
    Each entry in the reject wordlist is unhelpfully prefixed with an asterisk.
    """

    count = 0

    with open(ACCEPT_FILE, 'r') as infile:
        for line in infile:
            words = line.split(',')
            test_word = words[0].rstrip()

            # remove a terminating '*' character, if any (see 'unstrain*')
            if test_word.endswith('*'):
                test_word = test_word[:-1]
                
            match = re.search(r'[^a-z\-\']+', test_word, re.IGNORECASE)
            if not match:
                accept_set.add(test_word)
                
    with open(REJECT_FILE, 'r') as infile:
        for line in infile:
            words = line.split(',')
            # remove the leading '*'
            test_word = words[0][1:].rstrip()
            match = re.search(r'[^a-z\-\']+', test_word, re.IGNORECASE)
            if not match:
                reject_set.add(test_word)
                
    #print('accept set contains {0} entries'.format(len(accept_set)))
    #print('reject set contains {0} entries'.format(len(reject_set)))


###############################################################################
def morphological_negations(stemmed_token_list):
    """
    Identify all morphological negations in the sentence. Return a list of
    tokens representing such words.
    """

    results = []

    for st in stemmed_token_list:
        stem = st.stem
        token = st.token
        if stem in accept_set or token.text.startswith('non'):
            if token.text not in reject_set:
                results.append(token)

    return results


###############################################################################
def sentential_negations(doc):
    """
    """

    NEG_WORDS = set(['no', 'neither', 'nor', 'stop', 'none', 'not'])

    results = []
    
    # check for 'neg' dependencies and occurrences of 'neg' words
    for token in doc:
        if 'neg' == token.dep_:
            results.append(token)
        elif token.text in NEG_WORDS:
            results.append(token)

    return results


###############################################################################
def double_negations(morph_results, sent_results):
    """
    """

    WINDOW_SIZE = 6
    
    len_m = len(morph_results)
    len_s = len(sent_results)

    # list of 2-tuples
    results = []
    
    # check for double negations involving both morph and sent
    for i in range(len_m):
        for j in range(len_s):
            if j >= i:
                break
            if i-j <= WINDOW_SIZE:
                results.append( (morph_results[i], sent_results[j]) )

    # check for sent + sent double negations
    for i in range(len_s):
        for j in range(len_s):
            if j >= i:
                break
            if i-j <= WINDOW_SIZE:
                results.append( (sent_results[i], sent_results[j]) )
            
    return results
        

###############################################################################
def run(original_sentence, json_output=True):
    """
    """

    sentence = original_sentence.lower()
    
    doc = nlp(sentence)

    # build stemmed token list
    st_list = [StemmedToken(token, stemmer.stem(token.text)) for token in doc]
    
    morph_results  = morphological_negations(st_list)
    sent_results   = sentential_negations(doc)
    double_results = double_negations(morph_results, sent_results)

    print(original_sentence)
    print('\tmorphological negations: {0}'.format(morph_results))
    print('\t   sentential negations: {0}'.format(sent_results))
    print('\t       double negations: {0}'.format(double_results))

    if json_output:
        return to_json(original_sentence,
                       morph_results, sent_results, double_results)
    else:
        return (morph_results, sent_results, double_results)
    

###############################################################################
def report_error(msg, computed, expected):
    """
    """

    print(msg)
    print('\tcomputed: {0}'.format(computed))
    print('\texpected: {0}'.format(expected))


###############################################################################
def run_tests():

    init()

    TEST_DICT = {

        # morphological negations
        'The doctor disagreed with the test report.' :
        (['disagreed'], [], []),
        'It is illogical to conduct the experiment.' :
        (['illogical'], [], []),
        'It is related to Typhoid fever, but such as Typhoid, it is ' \
        'unrelated to Typhus.' :
        (['unrelated'], [], []),
        'The ruthlessness of the doctor is represented by means of his ' \
        'attitude towards his patients.' :
        ([], [], []),

        # sentential negations
        'The doctor could not diagnose the disease.' :
        ([], ['not'], []),
        "The medicine didn't end the fever." :
        ([], ["n't"], []),
        'Although vaccines have been developed, none are currently ' \
        'available in the United States.' :
        (['none'], ['none'], []),

        # double negations
        "The hospital won't allow no more visitors." :
        ([], ["n't", "no"], [('no', "n't")]),
        "Aagenaes Syndrome isn't a syndrome not characterised by congenital " \
        "hypoplasia of lymph vessels." :
        ([], ["n't", "not"], [('not', "n't")]),
    }

    for sentence, truth in TEST_DICT.items():
        # 'morph' and 'sent' are lists of Spacy tokens
        morph, sent, double = run(sentence, False)
        
        morph_truth  = truth[0]
        sent_truth   = truth[1]
        double_truth = truth[2]

        if len(morph) != len(morph_truth):
            report_error('error in morphological results: ',
                         morph, morph_truth)

        result_texts = [t.text for t in morph]
        for r in result_texts:
            if r not in morph_truth:
                report_error('error in morphological results: ',
                             morph, morph_truth)

        if len(sent) != len(sent_truth):
            report_error('error in sentential results: ',
                         sent, sent_truth)

        result_texts = [t.text for t in sent]
        for r in result_texts:
            if r not in sent_truth:
                report_error('error in sentential results: ',
                             sent, sent_truth)

        if len(double) != len(double_truth):
            report_error('error in double negation results: ',
                         double, double_truth)

        for i in range(len(double)):
            r0 = double[i][0].text
            r1 = double[i][1].text
            truth = [double_truth[i][0], double_truth[i][1]]
            if r0 not in truth or r1 not in truth:
                report_error('error in double negation results: ',
                             double, double_truth)


###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(MODULE_NAME, VERSION_MAJOR, VERSION_MINOR)


###############################################################################
def show_help():
    print(get_version())
    print("""
    USAGE: python3 ./{0} -f <filename>  [-hvz]

    OPTIONS:

        -s, --sentence <quoted string>  sentence to be analyzed

    FLAGS:

        -h, --help           Print this information and exit.
        -v, --version        Print version information and exit.
        -z, --selftest       Run self-tests and exit

    """.format(MODULE_NAME))


###############################################################################
if __name__ == '__main__':

    optparser = optparse.OptionParser(add_help_option=False)
    optparser.add_option('-s', '--sentence', action='store',
                         dest='sentence')
    optparser.add_option('-v', '--version',  action='store_true',
                         dest='get_version')
    optparser.add_option('-h', '--help',     action='store_true',
                         dest='show_help', default=False)
    optparser.add_option('-z', '--selftest', action='store_true',
                         dest='selftest')

    opts, other = optparser.parse_args(sys.argv)

    # show help if no command line arguments
    if opts.show_help or 1 == len(sys.argv):
        show_help()
        sys.exit(0)

    if opts.get_version:
        print(get_version())
        sys.exit(0)

    if opts.selftest:
        run_tests()
        sys.exit(0)

    init()

    result = run(sentence)
    print(result)
