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

_VERSION_MAJOR = 0
_VERSION_MINOR = 2

# set to True to enable debug output
_TRACE = False

# inclusion criteria (everything up to the exclusion statement)
_str_inclusion_criteria_1 = r'\bInclusion Criteria:.+(?=Exclusion Criteria:)'
_str_inclusion_criteria_2 = r'\bInclusion Criteria:.+(?=Exclusion:)'
_str_inclusion_criteria = r'(' + _str_inclusion_criteria_1 + r'|' +\
    _str_inclusion_criteria_2 + r')'
_regex_inclusion_criteria = re.compile(_str_inclusion_criteria, re.IGNORECASE)

# exclusion criteria
_str_exclusion_criteria = r'\bExclusion Criteria:.*\Z'
_regex_exclusion_criteria = re.compile(_str_exclusion_criteria, re.IGNORECASE)

# eligibility criteria
_str_eligibility_criteria = r'\bEligibility Criteria:.*\Z'
_regex_eligibility_criteria = re.compile(_str_eligibility_criteria, re.IGNORECASE)

# inclusion / exclusion criteria
_str_inc_ex_criteria = r'\bInclusion / Exclusion Criteria:.*\Z'
_regex_inc_ex_criteria = re.compile(_str_inc_ex_criteria, re.IGNORECASE)

_str_ecog = r'\b(Eastern Cooperative Oncology Group|ECOG)\s*([a-z\s=:.]+){0,4}'

_str1 = _str_ecog + r'(?P<lo>\d)'
_regex1 = re.compile(_str1, re.IGNORECASE)

_str2 = _str_ecog + r'(?P<lo>\d)\s*(,\s*)?(or|to|[-/~&])\s*(?P<hi>\d)'
_regex2 = re.compile(_str2, re.IGNORECASE)

_str3 = _str_ecog + r'(?P<lo>\d)\s(?P<mid>\d)\s*(or\s*)?(?P<hi>\d)'
_regex3 = re.compile(_str3, re.IGNORECASE)

_str4 = _str_ecog + r'(?P<lo>\d)\s(?P<mid>\d)\s(?P<mid1>\d)\s*(or\s*)?(?P<hi>\d)'
_regex4 = re.compile(_str4, re.IGNORECASE)

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
_op_strings = [_str_ecog + r'(?P<op>' + op + r')' + r'\s*(?P<lo>\d)'
              for op in _op_list]
_op_regexes = [re.compile(s, re.IGNORECASE) for s in _op_strings]
_op_map     = dict(zip(_op_regexes, _op_list))

_op_regex_list = [k for k in _op_map.keys()]

_regexes = [_regex4, _regex3, _regex2, _regex1]
_regexes.extend(_op_regex_list)

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

    # replace parens, brackets, and commas with spaces
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
                print('\tECOG MATCH[{0}]:\n\t\t"{1}"'.
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
                    print('*** Unrecognized operator: {0}'.format(op_string))

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

    pruned_candidates = overlap.remove_overlap(candidate_list, _TRACE)

    if _TRACE:
        print('\tcandidates count after overlap removal: {0}'.
              format(len(pruned_candidates)))
        print('\tPruned candidates: ')
        for c in pruned_candidates:
            print('\t\t[{0},{1}): {2}'.format(c.start, c.end, c.match_text))
        print()

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

    # list in order from longest to shortest criteria header
    inclusion_operations = [
        (_regex_inc_ex_criteria,      'INC_EX_CRITERIA',      _ID_INC),
        (_regex_eligibility_criteria, 'ELIGIBILITY CRITERIA', _ID_INC),
        (_regex_inclusion_criteria,   'INCLUSION CRITERIA',   _ID_INC),
    ]

    exclusion_operations = [
        (_regex_exclusion_criteria,   'EXCLUSION CRITERIA',   _ID_EX),
    ]

    # find the inclusion criteria first, then the exclusion criteria
    operations = [inclusion_operations, exclusion_operations]
    for op in operations:
        for regex, criteria, identifier in op:
            match = regex.search(doc)
            if match:
                sentence = match.group()
                sentence = _cleanup_sentence(sentence)

                if _TRACE:
                    print('{0} MATCH:\n\tmatching text: "{1}...{2}"'.
                          format(criteria, match.group()[:24], match.group()[-24:]))

                results = _process_sentence(sentence, identifier)
                result_list.extend(results)

                # search for exclusion criteria in remaining portion of doc
                doc = doc[match.end():]
                break

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
            print('Unknown file specified: "{0}"'.format(filepath))
            sys.exit(-1)
    else:
        print('nInput file not specified.')
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
            print('\nNo documents found')
            sys.exit(-1)
            
        doc_count = len(doc_list)
        print('Found {0} docs'.format(doc_count))

        if -1 == end:
            end = doc_count

        if start >= doc_count:
            print('\nStart index exceeds doc count')
            sys.exit(-1)
        if end == start:
            print('\nEmpty index interval: [{0}, {1})'.format(start, end))
            sys.exit(-1)

        assert end > start
        assert end <= doc_count
        assert start >= 0
        assert start < end
        
        for i in range(start, end):
            doc = doc_list[i]['report_text']
            print('\n[{0}]\n{1}'.format(i, doc))
            text = _cleanup_document(doc)

            # search for ECOG scores
            result_list = _find_ecog_scores(text)

            if 0 == len(result_list):
                print('\t*** No results found ***')
                continue

            print('RESULTS: ')
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
                    print('\t{0}{1} => {2}'.format(indent, k, v))
                print()
