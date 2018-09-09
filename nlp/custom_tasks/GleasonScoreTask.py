#!/usr/bin/env python3
"""

This is a custom task for extracting a patient's Gleason score, which is
relevant to prostate cancer diagnosis and staging.

Sample NLPQL:

    limit 100;

    phenotype "Gleason Score Finder" version "1";
    include ClarityCore version "1.0" called Clarity;

    documentset Docs:
        Clarity.createDocumentSet({
            "report_types":["Pathology"]
        });

    define final GleasonFinderFunction:
        Clarity.GleasonScoreTask({
            documentset: [Docs]
        });
"""

import re
from pymongo import MongoClient
from collections import namedtuple
from tasks.task_utilities import BaseTask

_VERSION_MAJOR = 0
_VERSION_MINOR = 2

_SCORE_TEXT_TO_INT = {
    'two':2,
    'three':3,
    'four':4,
    'five':5,
    'six':6,
    'seven':7,
    'eight':8,
    'nine':9,
    'ten':10
}

_str_gleason  = r'Gleason(\'?s)?\s*'
_str_desig    = r'(score|sum|grade|pattern)(\s+(is|of))?'

# accept a score in digits under these circumstances:
#     digit not followed by a '+', e.g. 'Gleason score 6'
#     digit followed by '+' but no digit after, e.g. 'Gleason score 3+'
# constructs such as Gleason score 3+3 captured in two-part expression below

_str_score = r'(?P<score>(\d+(?!\+)(?!\s\+)|\d+(?=\+(?!\d))|'             +\
             r'two|three|four|five|six|seven|eight|nine|ten))'

# parens are optional, space surrounding the '+' varies
_str_two_part = r'((\(\s*)?(?P<first_num>\d+)\s*\+\s*(?P<second_num>\d+)' +\
                r'(\s*\))?)?'

_str_total = _str_gleason + r'(' + _str_desig + r'\s*)?'                  +\
             r'(' + _str_score + r'\s*)?' + _str_two_part
_regex_gleason = re.compile(_str_total, re.IGNORECASE)

# another module might want to import these, so no leading underscore
GLEASON_SCORE_RESULT_FIELDS = ['sentence_index', 'start', 'end',
                               'score', 'first_num', 'second_num']
GleasonScoreResult = namedtuple('GleasonScoreResult',
                                GLEASON_SCORE_RESULT_FIELDS)


###############################################################################
def _find_gleason_score(sentence_list):
    """
    Scan a list of sentences and run Gleason score-finding regexes on each.
    Returns a list of GleasonScoreResult namedtuples.
    """

    result_list = []

    for i in range(len(sentence_list)):
        s = sentence_list[i]
        iterator = _regex_gleason.finditer(s)
        for match in iterator:
            start = match.start()
            end   = match.end()

            try:
                first_num = int(match.group('first_num'))
            except:
                first_num = None

            try:
                second_num = int(match.group('second_num'))
            except:
                second_num = None

            try:
                match_text = match.group('score')
                if match_text.isdigit():
                    score = int(match_text)
                else:
                    match_text = match_text.strip()
                    if match_text in _SCORE_TEXT_TO_INT:
                        score = _SCORE_TEXT_TO_INT[match_text]
                    else:
                        score = None
            except:
                # no single score was given
                if first_num is not None and second_num is not None:
                    score = first_num + second_num
                else:
                    score = None

            # 1 <= first_num <= 5
            # 1 <= second_num <= 5
            # 2 <= score <= 10
            # anything outside of these limits is invalid

            if first_num is not None and (first_num > 5 and first_num <= 10):
                # assume score reported for first_num
                score = first_num
                first_num = None
                second_num = None
            elif score is not None and (score < 2 or score > 10):
                # invalid
                score = None
                continue
                    
            result = GleasonScoreResult(i, start, end,
                                        score, first_num, second_num)
            result_list.append(result)

    return result_list


###############################################################################
class GleasonScoreTask(BaseTask):
    """
    A custom task for finding the Gleason score, which is relevant to 
    prostate cancer diagnosis and staging.
    """
    
    # use this name in NLPQL
    task_name = "GleasonScoreTask"

    def run_custom_task(self, temp_file, mongo_client: MongoClient):

        # for each document in the NLPQL-specified doc set
        for doc in self.docs:

            # all sentences in this document
            sentence_list = self.get_document_sentences(doc)

            # all Gleason score results in this document
            result_list = _find_gleason_score(sentence_list)
                
            if len(result_list) > 0:
                for result in result_list:
                    obj = {
                        'sentence':sentence_list[result.sentence_index],
                        'start':result.start,
                        'end':result.end,
                        'value':result.score,
                        'value_first':result.first_num,
                        'value_second':result.second_num
                    }
            
                    self.write_result_data(temp_file, mongo_client, doc, obj)

