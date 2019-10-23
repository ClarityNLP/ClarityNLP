#!/usr/bin/env python3
"""

This is a custom task for extracting ECOG scores from clinical trial inclusion
and exclusion criteria.

Sample NLPQL:

    limit 200;

    phenotype "ECOG Criteria Finder" version "1";
    include ClarityCore version "1.0" called Clarity;

    documentset Docs:
        Clarity.createDocumentSet({
            "report_types":["Clinical Trial Criteria"],
            "filter_query":"source:AACT-TEST"
        });

    define final EcogCriteriaFunction:
        Clarity.EcogCriteriaTask({
            documentset: [Docs]
        });

"""

import os
import re
import sys
import json
import argparse
from pymongo import MongoClient
from collections import namedtuple

# modify path for local testing
if __name__ == '__main__':
    cur_dir = sys.path[0]
    nlp_dir, tail = os.path.split(cur_dir)
    sys.path.append(nlp_dir)
    sys.path.append(os.path.join(nlp_dir, 'tasks'))

# ClarityNLP imports
from tasks.task_utilities import BaseTask
from algorithms.finder import finder_overlap as overlap
from claritynlp_logging import log, ERROR, DEBUG


_VERSION_MAJOR = 0
_VERSION_MINOR = 2

# set to True to enable debug output
_TRACE = False

_str_ecog1 = r'\b(Eastern Cooperative Oncology( Group)?[-\s]+Performance Status (ECOG)?|' +\
    r'Eastern Cooperative Oncology Group[-\s]+(ECOG)?|' +\
    r'ECOG)([a-z\s=:.]+)'

_str_num1 = r'(?P<lo>\d)'
_str_num2 = r'(?P<lo>\d)\s*(,\s*)?(or|to|[-/~&])\s*(?P<hi>\d)'
_str_num3 = r'(?P<lo>\d)\s(?P<mid>\d)\s*(or\s*)?(?P<hi>\d)'
_str_num4 = r'(?P<lo>\d)\s(?P<mid>\d)\s(?P<mid1>\d)\s*(or\s*)?(?P<hi>\d)'

# these regexes assume the ECOG score(s) follow the ECOG statement
_str1 = _str_ecog1 + _str_num1
_regex1 = re.compile(_str1, re.IGNORECASE)

_str2 = _str_ecog1 + _str_num2
_regex2 = re.compile(_str2, re.IGNORECASE)

_str3 = _str_ecog1 + _str_num3
_regex3 = re.compile(_str3, re.IGNORECASE)

_str4 = _str_ecog1 + _str_num4
_regex4 = re.compile(_str4, re.IGNORECASE)

# ECOG score(s) appears between _str_ps and _str_ecog2
_str_ps = r'\bperformance status( of)?\s'
_str_ecog2 = r'\b\s((on the )?Eastern Cooperative Oncology Group( ECOG)?|ECOG)( score)?'

_str5 = _str_ps + _str_num1 + _str_ecog2
_regex5 = re.compile(_str5, re.IGNORECASE)

_str6 = _str_ps + _str_num2 + _str_ecog2
_regex6 = re.compile(_str6, re.IGNORECASE)

_str7 = _str_ps + _str_num3 + _str_ecog2
_regex7 = re.compile(_str7, re.IGNORECASE)

_str8 = _str_ps + _str_num4 + _str_ecog2
_regex8 = re.compile(_str8, re.IGNORECASE)

_str_or        = r'(/| or )'
_str_equal     = r'\b(equal|eq.?)( to )'
_str_eq        = r'(=|' + _str_equal + r')'
_str_less_than = r'\b(less than|lt.?)'
_str_lt        = r'(<|' + _str_less_than + r')'
_str_lte       = r'(<=|' + _str_lt + _str_or + _str_eq + r')'
_str_elt       = r'(=<|' + _str_eq + _str_or + _str_lt + r')'
_str_gt_than   = r'\b(greater than|gt.?)'
_str_gt        = r'(>|'  + _str_gt_than + r')'
_str_gte       = r'(>=|' + _str_gt + _str_or + _str_eq + r')'
_str_egt       = r'(=>|' + _str_eq + _str_or + _str_gt + r')'

_op_list    = [_str_lte, _str_gte, _str_elt, _str_egt, _str_lt, _str_gt, _str_eq]
_op_strings = [_str_ecog1 + r'(?P<op>' + op + r')' + r'\s*(?P<lo>\d)'
              for op in _op_list]
_op_regexes = [re.compile(s, re.IGNORECASE) for s in _op_strings]
_op_map     = dict(zip(_op_regexes, _op_list))

_op_regex_list = [k for k in _op_map.keys()]

_regexes = [
    _regex4,
    _regex3,
    _regex2,
    _regex1,
]

# add operator regexes for scores following ECOG statement
_regexes.extend(_op_regex_list)

# add in-between regexes
_regexes.extend([
    _regex8,
    _regex7,
    _regex6,
    _regex5
])

ECOG_RESULT_FIELDS = [
    'sentence', 'start', 'end', 'inc_or_ex', 'score_min', 'score_max'
]

EcogResult = namedtuple('EcogResult', ECOG_RESULT_FIELDS)

_ID_INC    = 1
_ID_EX     = 0
_SCORE_MAX = 5


###############################################################################
def _enable_debug():

    global _TRACE
    _TRACE = True


###############################################################################
def _cleanup_document(document):
    """
    Remove extraneous chars, collapse whitespace, etc., so simpler regexes
    can be used.
    """

    # replace some chars with spaces
    document = re.sub(r'[\(\)\[\],]', ' ', document)

    # collapse repeated whitespace (including newlines) into a single space
    document = re.sub(r'\s+', ' ', document)

    # convert unicode left and right quotation marks to ascii
    document = re.sub(r'(\u2018|\u2019)', "'", document)

    # strip any leading or trailing whitespace
    document = document.strip()
    
    return document


###############################################################################
def _cleanup_sentence(s):
    """
    Replace all-text comparisons with symbols to force match with an operator
    regex. Need to do this since some regexes capture arbitrary words which
    aren't currently being interpreted. Some of these operators are
    nonstandard (i.e. =<, =>), but the meaning should be clear.
    """

    s = re.sub(r'\bequal to or less than\b', '=<', s)
    s = re.sub(r'\bequal to or greater than\b', '=>', s)
    s = re.sub(r'\bgreater than or equal\b', '>=', s)
    s = re.sub(r'\bless than or equal\b', '<=', s)
    s = re.sub(r'\bless than\b', '<', s)
    s = re.sub(r'\bgreater than\b', '>', s)
    s = re.sub(r'\bequal to\b', '=', s)
    
    return s


###############################################################################
def _process_sentence(sentence, inc_or_ex = _ID_INC):
    """
    Find the first ECOG score in a 'sentence', which is the text of either
    the inclusion or exclusion criteria.
    """

    result_list    = []
    candidate_list = []
    
    for regex_index, regex in enumerate(_regexes):

        iterator = regex.finditer(sentence)
        for match in iterator:

            if _TRACE:
                log('\tECOG MATCH[{0}]:\n\t\t"{1}"'.
                      format(regex_index, match.group()))
            
            # character offsets
            start = match.start()
            end = match.end()

            # all regexes have a 'lo' group capture
            lo = int(match.group('lo'))

            try:
                hi = int(match.group('hi'))
            except:
                hi = None

            # backtrack if invalid value was captured for 'hi'
            if hi is not None and hi > _SCORE_MAX:
                hi = None
                try:
                    mid1 = int(match.group('mid1'))
                    hi = mid1
                except:
                    mid1 = None

            if hi is not None and hi > _SCORE_MAX:
                hi = None
                try:
                    mid = int(match.group('mid'))
                    hi = mid
                except:
                    mid = None

            try:
                op = match.group('op')
            except:
                op = None

            if op is not None:

                # determine which operator and adjust [lo, hi] accordingly
                op_string = _op_map[regex]
                if _str_lte == op_string:
                    hi = lo
                    lo = 0
                elif _str_gte == op_string:
                    hi = 5
                elif _str_elt == op_string:
                    hi = lo
                    lo = 0
                elif _str_egt == op_string:
                    hi = 5
                elif _str_lt == op_string:
                    if lo > 1:
                        hi = lo-1
                        lo = 0
                    else:
                        lo = 0
                        hi = None
                elif _str_gt == op_string:
                    if lo < 4:
                        lo = lo + 1
                        hi = 5
                    else:
                        lo = 5
                        hi = None
                elif _str_eq == op_string:
                    # lo remains the same, no hi
                    pass
                else:
                    log('*** Unrecognized operator: {0}'.format(op_string))

            # this is a new candidate
            candidate = overlap.Candidate(start      = start,
                                          end        = end,
                                          match_text = match.group(),
                                          regex      = regex,
                                          other =
                                          {
                                              'sentence':sentence,
                                              'inc_or_ex':inc_or_ex,
                                              'lo':lo,
                                              'hi':hi
                                          })
            
            candidate_list.append(candidate)
            
    # sort candidates in descending order of length overlap resolution
    candidate_list = sorted(candidate_list,
                            key=lambda x: x.end - x.start, reverse=True)

    if len(candidate_list) > 0:
        pruned_candidates = overlap.remove_overlap(candidate_list, _TRACE)
    else:
        pruned_candidates = []

    if _TRACE:
        log('\tcandidates count after overlap removal: {0}'.
              format(len(pruned_candidates)))
        log('\tPruned candidates: ')
        for c in pruned_candidates:
            log('\t\t[{0},{1}): {2}'.format(c.start, c.end, c.match_text))
        log()

    for pc in pruned_candidates:
        result = EcogResult(sentence  = pc.other['sentence'],
                            start     = pc.start,
                            end       = pc.end,
                            inc_or_ex = pc.other['inc_or_ex'],
                            score_min = pc.other['lo'],
                            score_max = pc.other['hi'])
        result_list.append(result)

    return result_list

    
###############################################################################
def _find_ecog_scores(doc):
    """
    Scan a document and run ecog score-finding regexes on it.
    Returns a list of EcogScoreResult namedtuples.

    Assumes a SINGLE set of inclusion criteria and a SINGLE set of exclusion
    criteria in the document text. Also assumes that the inclusion criteria
    come before the exclusion criteria. These assumptions are consistent with
    the AACT 'Clinical Trial Criteria' announcements. 

    The inclusion criteria may appear as 'Inclusion Criteria:',
    'Eligibility Criteria:', 'Inclusion / Exclusion Criteria:', or possibly
    other forms. See the regexes below for all supported forms.
    """

    result_list = []    

    exclusion_header = [
        'exclusion criteria',
        'exclusion'
    ]

    doc_lc = doc.lower()

    # find the exclusion criteria header, if any
    inclusion_str = None
    exclusion_str = None
    pos = -1
    for header in exclusion_header:
        pos = doc_lc.find(header)
        if -1 != pos:
            inclusion_str = doc[:pos]
            exclusion_str = doc[pos:]
        else:
            # all inclusion
            inclusion_str = doc

    if inclusion_str is not None and len(inclusion_str) > 0:
        inclusion_str = _cleanup_sentence(inclusion_str)
        if _TRACE:
            log('CLEANED INCLUSION CRITERIA: "{0}...{1}"'.
                  format(inclusion_str[:24], inclusion_str[-24:]))
        results = _process_sentence(inclusion_str, _ID_INC)
        result_list.extend(results)

    if exclusion_str is not None and len(exclusion_str) > 0:
        exclusion_str = _cleanup_sentence(exclusion_str)
        if _TRACE:
            log('CLEANED EXCLUSION CRITERIA: "{0}...{1}"'.
                  format(exclusion_str[:24], exclusion_str[-24:]))
        results = _process_sentence(exclusion_str, _ID_EX)
        result_list.extend(results)
    
    return result_list


###############################################################################
def _to_mongo_object(result):
    """
    Generate the MongoDB result object from an EcogResult namedtuple.
    """

    scores = [0,0,0,0,0,0]

    lo = result.score_min
    hi = result.score_max

    if hi is None:
        scores[lo] = 1
    else:
        for i in range(lo, hi+1):
            scores[i] = 1

    if 1 == result.inc_or_ex:
        criteria = 'Inclusion'
    else:
        criteria = 'Exclusion'

    mongo_obj = {
        'sentence':result.sentence,
        'start':result.start,
        'end':result.end,
        'criteria_type':criteria,
        'score_0':scores[0],
        'score_1':scores[1],
        'score_2':scores[2],
        'score_3':scores[3],
        'score_4':scores[4],
        'score_5':scores[5],
        'score_lo':result.score_min,
        'score_hi':result.score_max
    }

    return mongo_obj


###############################################################################
class EcogCriteriaTask(BaseTask):
    """
    A custom task for finding ECOG scores in clinical trial inclusion and
    exclusion criteria. The text strings for the different criteria are
    returned as separate 'sentences'.
    """
    
    # use this name in NLPQL
    task_name = "EcogCriteriaTask"

    def run_custom_task(self, temp_file, mongo_client: MongoClient):

        # for each document in the NLPQL-specified doc set
        for doc in self.docs:

            # get the document text and clean it
            text = self.get_document_text(doc)
            text = _cleanup_document(text)

            # search for ECOG scores
            result_list = _find_ecog_scores(text)

            # write results to MongoDB
            if len(result_list) > 0:
                for result in result_list:
                    mongo_obj = _to_mongo_object(result)
                    self.write_result_data(temp_file,
                                           mongo_client, doc, mongo_obj)

                    
###############################################################################
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='test EcogCriteriaTask independently of full pipeline')
    parser.add_argument('-f', '--filepath',
                        help='path to JSON file containing ECOG scores in '
                        'the report_text field')
    parser.add_argument('-s', '--start',
                        help='0-based index of first record to process')
    parser.add_argument('-e', '--end',
                        help='0-based index of final record to process + 1')
    parser.add_argument('--debug',
                        action='store_true',
                        help='print debugging information')

    args = parser.parse_args()

    filepath = None
    if 'filepath' in args and args.filepath:
        filepath = args.filepath
        if not os.path.isfile(filepath):
            log('Unknown file specified: "{0}"'.format(filepath))
            sys.exit(-1)
    else:
        log('nInput file not specified.')
        sys.exit(0)

    if 'debug' in args and args.debug:
        _enable_debug()

    start = 0
    if 'start' in args and args.start:
        start = int(args.start)
        if start < 0:
            start = 0

    # -1 == process all documents
    end = -1
    if 'end' in args and args.end:
        end = int(args.end)
        if end < 0:
            end = -1

    with open(filepath, 'rt') as infile:
        json_string = infile.read()
        json_data = json.loads(json_string)

        doc_list = None
        if 'response' in json_data and 'docs' in json_data['response']:
            doc_list = json_data['response']['docs']
        elif list == type(json_data):
            doc_list = json_data

        if doc_list is None:
            log('\nNo documents found')
            sys.exit(-1)
            
        doc_count = len(doc_list)
        log('Found {0} docs'.format(doc_count))

        if -1 == end:
            end = doc_count

        if start >= doc_count:
            log('\nStart index exceeds doc count')
            sys.exit(-1)
        if end == start:
            log('\nEmpty index interval: [{0}, {1})'.format(start, end))
            sys.exit(-1)

        assert end > start
        assert end <= doc_count
        assert start >= 0
        assert start < end
        
        for i in range(start, end):
            doc = doc_list[i]['report_text']
            log('\n[{0}]\n{1}'.format(i, doc))
            text = _cleanup_document(doc)

            # search for ECOG scores
            result_list = _find_ecog_scores(text)

            if 0 == len(result_list):
                log('\t*** No results found ***')
                continue

            log('RESULTS: ')
            max_key_len = 0
            for result in result_list:
                mongo_obj = _to_mongo_object(result)

                if 0 == max_key_len:
                    for k in mongo_obj.keys():
                        if len(k) > max_key_len:
                            max_key_len = len(k)
                
                for k,v in mongo_obj.items():
                    if 'sentence' == k:
                        # display only the ECOG match
                        sentence = mongo_obj[k]
                        start = mongo_obj['start']
                        end   = mongo_obj['end']
                        k = 'matching_text'
                        v = sentence[start:end]
                    indent = ' ' * (max_key_len - len(k))
                    log('\t{0}{1} => {2}'.format(indent, k, v))
                log()
