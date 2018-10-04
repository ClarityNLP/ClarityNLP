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

import re
from pymongo import MongoClient
from collections import namedtuple
from tasks.task_utilities import BaseTask

_VERSION_MAJOR = 0
_VERSION_MINOR = 1

# find inclusion criteria text (everything up to the exclusion criteria)
_str_inclusion_criteria = r'\bInclusion Criteria:.+(?=Exclusion Criteria:)'
_regex_inclusion_criteria = re.compile(_str_inclusion_criteria)

# find exclusion criteria text
_str_exclusion_criteria = r'\bExclusion Criteria:.*\Z'
_regex_exclusion_criteria = re.compile(_str_exclusion_criteria)

_str_ecog = r'\b(Eastern Cooperative Oncology Group|ECOG) ([a-z\s=:]+){0,4}'

_str1 = _str_ecog + r'(?P<lo>\d)'
_regex1 = re.compile(_str1, re.IGNORECASE)

_str2 = _str_ecog + r'(?P<lo>\d)\s*(,\s*)?(or|to|-|/)\s*(?P<hi>\d)'
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
def _cleanup_document(document):
    """
    Decode from bytes object, remove repeated whitespace.
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

    # replace all-text comparisons with symbols to force op-regex match
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

    result_list = []
    
    count = 0
    #min_start = 9999999
    for regex in _regexes:
        match = regex.search(sentence)
        if match:
        #iterator = regex.finditer(sentence)
        #for match in iterator:

            #print('matching text: {0}'.format(match.group()))

            # character offsets
            start = match.start()
            # if start < min_start:
            #     min_start = start
            # else:
            #     continue
            end = match.end()

            # all regexes have a 'lo' group capture
            lo = int(match.group('lo'))

            try:
                hi = int(match.group('hi'))
            except:
                hi = None

            # backtrack if invalid value was captured
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
                # all op matches capture the 'lo' group
                #print('\top: {0}'.format(op))

                # determine which op
                op_string = _op_map[regex]
                if _str_lte == op_string:
                    hi = lo
                    lo = 0
                    #print('\t\tLESS THAN OR EQUAL')
                elif _str_gte == op_string:
                    hi = 5
                    #print('\t\tGT THAN OR EQUAL')
                elif _str_elt == op_string:
                    hi = lo
                    lo = 0
                    #print('\t\tEQ TO OR LESS THAN')
                elif _str_egt == op_string:
                    hi = 5
                    #print('\t\tEQ TO OR GT THAN')
                elif _str_lt == op_string:
                    if lo > 1:
                        hi = lo-1
                        lo = 0
                    else:
                        lo = 0
                        hi = None
                    #print('\t\tLESS THAN')
                elif _str_gt == op_string:
                    if lo < 4:
                        lo = lo + 1
                        hi = 5
                    else:
                        lo = 5
                        hi = None
                    #print('\t\tGT THAN')
                elif _str_eq == op_string:
                    pass
                    # lo remains the same
                    #print('\t\tEQUAL')
                else:
                    print('*** Unrecognized operator: {0}'.format(op_string))

            # if hi is not None:
            #     print('\t[{0}, {1}]'.format(lo, hi))
            # else:
            #     print('\t[{0}]'.format(lo))

            # save to results
            result = EcogResult(sentence, start, end, inc_or_ex, lo, hi)
            result_list.append(result)
                
            # keep the first match, since more complex regexes come first
            break

    count += 1
    
    return result_list

    
###############################################################################
def _find_ecog_scores(document_list):
    """
    Scan a document list and run ecog score-finding regexes on each.
    Returns a list of EcogScoreResult namedtuples.
    """

    result_list = []

    for doc in document_list:

        # inclusion criteria
        match = _regex_inclusion_criteria.search(doc)
        if match:
            sentence = match.group()
            sentence = _cleanup_sentence(sentence)
            results = _process_sentence(sentence, _ID_INC)
            result_list.extend(results)
            
        # exclusion criteria
        match = _regex_exclusion_criteria.search(doc)
        if match:
            sentence = match.group()
            sentence = _cleanup_sentence(sentence)
            results = _process_sentence(sentence, _ID_EX)
            result_list.extend(results)

    return result_list


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
            result_list = _find_ecog_scores([text])

            # write results to MongoDB
            if len(result_list) > 0:
                for result in result_list:

                    scores = [0,0,0,0,0,0]

                    lo = result.score_min
                    hi = result.score_max

                    if hi is None:
                        scores[lo] = 1
                    else:
                        for i in range(lo, hi+1):
                            scores[i] = 1

                    obj = {
                        'sentence':result.sentence,
                        'start':result.start,
                        'end':result.end,
                        'inc_or_ex':result.inc_or_ex,
                        'score_0':scores[0],
                        'score_1':scores[1],
                        'score_2':scores[2],
                        'score_3':scores[3],
                        'score_4':scores[4],
                        'score_5':scores[5],
                        'score_lo':result.score_min,
                        'score_hi':result.score_max
                    }

                    self.write_result_data(temp_file, mongo_client, doc, obj)

