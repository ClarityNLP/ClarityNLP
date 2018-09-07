#!/usr/bin/env python3
"""

This is a custom task for extracting a patient's Gleason score, which is
relevant to prostate cancer diagnosis and staging.

Sample NLPQL, uses a special set of docs with report_type:"Gleason" :

    limit 100;

    phenotype "Gleason Score Finder" version "1";
    include ClarityCore version "1.0" called Clarity;

    documentset GleasonDocs:
        Clarity.createDocumentSet({
            "report_types":["Gleason"]
        });

    define final GleasonFinderFunction:
        Clarity.GleasonScoreTask({
            documentset: [DischargeSummaries]
        });
"""

import re
from pymongo import MongoClient
from collections import namedtuple
from tasks.task_utilities import BaseTask

VERSION_MAJOR = 0
VERSION_MINOR = 1

# Gleason('?s)? score 7 (4 + 3)
str_gleason1 = r'\bGleason(\'?s)?\s+score\s+(?P<score>\d+)\s+'     +\
               r'\(\s*(?P<first_num>\d)\s*\+\s*(?P<second_num>\d)\s*\)'

# Gleason('?s)? (score)? 4 + 3
str_gleason2 = r'\bGleason(\'?s)?\s+(score\s+)?(?P<first_num>\d)\s*\+\s*(?P<second_num>\d)'

# Gleason('?s)? score 7
str_gleason3 = r'\bGleason(\'?s)?\s+(score\s+)?(?P<score>\d+)'

regex_gleason1 = re.compile(str_gleason1, re.IGNORECASE)
regex_gleason2 = re.compile(str_gleason2, re.IGNORECASE)
regex_gleason3 = re.compile(str_gleason3, re.IGNORECASE)
REGEXES = [regex_gleason1, regex_gleason2, regex_gleason3]

GLEASON_SCORE_RESULT_FIELDS = ['sentence_index', 'start', 'end',
                               'score', 'first_num', 'second_num']
GleasonScoreResult = namedtuple('GleasonScoreResult',
                                GLEASON_SCORE_RESULT_FIELDS)


###############################################################################
def find_gleason_score(sentence_list):
    """
    Scan a list of sentences and run Gleason score-finding regexes on each.
    Returns a list of GleasonScoreResult namedtuples.
    """

    result_list = []

    for i in range(len(sentence_list)):
        s = sentence_list[i]
        best_width = 0
        best_candidate = None
        for regex in REGEXES:
            match = regex.search(s)
            if match:
                start = match.start()
                end   = match.end()

                # keep match if longer than any previous matches
                width = end - start
                if width < best_width:
                    continue
                
                best_width = width

                try:
                    first_num = int(match.group('first_num'))
                except:
                    first_num = None

                try:
                    second_num = int(match.group('second_num'))
                except:
                    second_num = None

                try:
                    score = int(match.group('score'))
                except:
                    if first_num is not None and second_num is not None:
                        score = first_num + second_num
                    else:
                        score = None
                    
                result = GleasonScoreResult(i, start, end,
                                            score, first_num, second_num)
                best_candidate = result

        if best_candidate is not None:
            result_list.append(best_candidate)

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
            result_list = find_gleason_score(sentence_list)
                
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

