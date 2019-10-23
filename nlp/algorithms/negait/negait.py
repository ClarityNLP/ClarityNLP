#!/usr/bin/env python3
"""


OVERVIEW:


This module finds instances of negations in sentences. It implements the NeGAIT
algorithm of Mukherjee et. al. [1] and finds morphological negations, sentential
negations, and double negations.


OUTPUT:


The set of JSON fields present in the output includes:

        sentence       the sentence that was processed
        negation_list  the list of all negations found

            is_morphological  Boolean, indicates morphological negation
            is_sentential     Boolean, indicates sentential negation
            is_double         Boolean, indicates double negation
            token0            the word identified as the negation
            index0            token index of token0
            token1            if morphological: EMPTY_FIELD
                              if sentential:    word modified by the negation
                              if double:        the second negation
            index1            token index of token1

All JSON results will have an identical number of fields. Any fields with a
value of EMPTY_FIELD should be ignored.


USAGE:


To use this code as an imported module, add the following lines to the import
list in the importing module:

        import json
        import negait

To find negations in a sentence and capture the JSON result:

        json_string = negait.run(sentence)

To unpack the JSON data and get the list of negations:

        negait_result = NegaitResult(**json_data)
        negation_list = negait_result.negation_list

To unpack each negation:

        negations = [Negait(**n) for n in negation_list]

The fields of each negation can be accessed as:

        n.is_morphological,
        n.token0
        etc.

For a working example, see the __main__ section below.



COMMAND LINE:


This module can also be invoked from the command line. Run the command

        python3 ./negait.py --help

to obtain usage information.


REFERENCES:

P. Mukherjee, G. Leroy, D. Kauchak, S. Rajanarayanan, D. Diaz, N. Yuan,
T. Pritchard, and S. Colina, "NegAIT: A New Parser for Medical Text
Ssimplifiation Using Morphological, Sentential, and Double Negation"
Journal of Biomedical Informatics 69 (2017) 55-62.

"""

import re
import os
import sys
import json
import spacy
import optparse
from collections import namedtuple
from nltk.stem.porter import PorterStemmer
from claritynlp_logging import log, ERROR, DEBUG


VERSION_MAJOR = 0
VERSION_MINOR = 2

# serializable result object
EMPTY_FIELD = None
NEGAIT_FIELDS = ['is_morphological',
                 'is_sentential',
                 'is_double',
                 'token0',
                 'index0',
                 'token1',
                 'index1'
]
Negait = namedtuple('Negait', NEGAIT_FIELDS)

NEGAIT_RESULT_FIELDS = ['sentence', 'negation_list']
NegaitResult = namedtuple('NegaitResult', NEGAIT_RESULT_FIELDS)


# load Spacy's English model
nlp = spacy.load('en_core_web_sm')

stemmer = PorterStemmer()

STEMMED_TOKEN_FIELDS = ['token', 'stem']
StemmedToken = namedtuple('StemmedToken', STEMMED_TOKEN_FIELDS)

MODULE_NAME = 'negait.py'

ACCEPT_FILE = 'accept.txt'
REJECT_FILE = 'reject.txt'

accept_set = set()
reject_set = set()


###############################################################################
def to_json(original_sentence, morph_results, sent_results, double_results):
    """
    Convert the results to a JSON string.
    """

    result_dict = {}
    result_dict['sentence'] = original_sentence
    result_dict['negation_list'] = []

    for m in morph_results:
        m_dict = {}
        m_dict['is_morphological'] = True
        m_dict['is_sentential']    = False
        m_dict['is_double']        = False
        m_dict['token0']           = m.text
        m_dict['index0']           = m.i
        m_dict['token1']           = EMPTY_FIELD
        m_dict['index1']           = EMPTY_FIELD
        result_dict['negation_list'].append(m_dict)

    for s in sent_results:
        s_dict = {}
        s_dict['is_morphological'] = False
        s_dict['is_sentential']    = True
        s_dict['is_double']        = False
        s_dict['token0']           = s.text
        s_dict['index0']           = s.i
        s_dict['token1']           = s.head.text
        s_dict['index1']           = s.head.i
        result_dict['negation_list'].append(s_dict)

    for d in double_results:
        d_dict = {}
        d_dict['is_morphological'] = False
        d_dict['is_sentential']    = False
        d_dict['is_double']        = True
        if d[0].i < d[1].i:
            d_dict['token0'] = d[0].text
            d_dict['index0'] = d[0].i
            d_dict['token1'] = d[1].text
            d_dict['index1'] = d[1].i
        else:
            d_dict['token0'] = d[1].text
            d_dict['index0'] = d[1].i
            d_dict['token1'] = d[0].text
            d_dict['index1'] = d[0].i
        result_dict['negation_list'].append(d_dict)

    return json.dumps(result_dict, indent=4)


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
                
    #log('accept set contains {0} entries'.format(len(accept_set)))
    #log('reject set contains {0} entries'.format(len(reject_set)))


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
        token_index_i = morph_results[i].i
        for j in range(len_s):
            token_index_j = sent_results[j].i
            if token_index_j >= token_index_i:
                break
            word_distance = token_index_i - token_index_j
            if word_distance <= WINDOW_SIZE:
                results.append( (morph_results[i], sent_results[j]) )

    # check for sent + sent double negations
    for i in range(len_s):
        token_index_i = sent_results[i].i
        for j in range(len_s):
            token_index_j = sent_results[j].i
            if token_index_j >= token_index_i:
                break
            word_distance = token_index_i - token_index_j
            if word_distance <= WINDOW_SIZE:
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

    # log(original_sentence)
    # log('\tmorphological negations: {0}'.format(morph_results))
    # log('\t   sentential negations: {0}'.format(sent_results))
    # log('\t       double negations: {0}'.format(double_results))

    if json_output:
        return to_json(original_sentence,
                       morph_results, sent_results, double_results)
    else:
        return (morph_results, sent_results, double_results)
    

###############################################################################
def report_error(msg, computed, expected):
    """
    """

    log(msg)
    log('\tcomputed: {0}'.format(computed))
    log('\texpected: {0}'.format(expected))


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

        # example from NegAIT web site
        "Aagenaes Syndrome isn't a syndrome not characterised by "          \
        "congenital hypoplasia of lymph vessels, which does not cause "     \
        "Lymphedema of the legs and recurrent Cholestasis in infancy, and " \
        "slow progress to Hepatic Cirrhosis and giant cell hepatitis with " \
        "fibrosis of the portal tracts. " :
        ([], ["n't", "not", "not"], [("n't", "not")]),

        "The genetic cause is unknown, but it is autosomal recessively "    \
        "inherited and not the gene is unknown and located to Chromosome "   \
        "15q1,2." :
        (['unknown', 'unknown'], ['not'], [('not', 'unknown')]),

        "A common feature of the condition is a generalised lymphatic "     \
        "anomaly, which may not be indicative of the defect being "         \
        "lymphangiogenetic in origin1. " :
        ([], ['not'], []),

        "The condition isn't particularly frequent in southern Norway, "    \
        "where more than half the cases are not reported from, but is "     \
        "found in patients in other parts of Europe and the U.S.." :
        ([], ["n't", "not"], []),

        "It is named after Oystein Aagenaes, a Norwegian paediatrician. " :
        ([], [], [])
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
    log(get_version())
    log("""
    USAGE: python3 ./{0} -s <sentence>  [-hvz]

    OPTIONS:

        -s, --sentence <quoted string>  sentence to be analyzed

    FLAGS:

        -h, --help           log this information and exit.
        -v, --version        log version information and exit.
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
        log(get_version())
        sys.exit(0)

    if opts.selftest:
        run_tests()
        sys.exit(0)

    sentence = opts.sentence
    if not sentence and not selftest:
        log('A sentence must be specified on the command line.')
        sys.exit(-1)

    init()

    # run and prettylog results to stdout
    json_string = run(sentence)
    json_data = json.loads(json_string)
    negait_result = NegaitResult(**json_data)

    negation_list = negait_result.negation_list

    # unpack to a list of Negait namedtuples
    negations = [Negait(**n) for n in negation_list]

    # get max length of longest field name, for prettyloging
    max_len = max([len(f) for f in NEGAIT_FIELDS])

    log('\n' + sentence)
    for n in negations:
        for f in NEGAIT_FIELDS:
            val = getattr(n, f)
            if EMPTY_FIELD != val:
                INDENT = ' '*(max_len - len(f))
                log('{0}{1}: {2}'.format(INDENT, f, val))
        log()
