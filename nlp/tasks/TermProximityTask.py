#!/usr/bin/env python3
"""

This is a custom task for performing a term proximity search. It takes two
lists of search terms and a maximum word distance. If terms from lists 1 and
2 both appear in the sentence and are within the specified distance, the search
succeeds and both terms appear in the results. A boolean parameter can also
be provided that either enforces or ignores the order of the terms.

This task requires a set of NLPQL custom parameters:

    termset1: (quoted string) a comma-separated list of terms to search for
    termset2: (quoted string) a comma-separated list of terms to search for
    word_distance: (integer) max distance between search terms
    any_order: (quoted string)
               if "False": termset1 term(s) must appear before termset2 term(s)
               if "True": search terms can appear in any order

For now, consider all of these NLPQL parameters as mandatory.

Sample NLPQL:


    limit 100;

    phenotype "Term Proximity Search" version "1";
    include ClarityCore version "1.0" called Clarity;

    documentset Docs:
        Clarity.createDocumentSet({
            "report_types":["Pathology"]
        });

    define final TermProximityFunction:
        Clarity.TermProximityTask({
            documentset: [Docs],
            "termset1": "prostate, score, sum, grade, pattern",
            "termset2": "cancer, Gleason, Gleason's, Gleasons",
            "word_distance": 5,
            "any_order": "False"
        });

"""

import re
from pymongo import MongoClient
from collections import namedtuple
from tasks.task_utilities import BaseTask
from claritynlp_logging import log, ERROR, DEBUG

_VERSION_MAJOR = 0
_VERSION_MINOR = 1

PROXIMITY_RESULT_FIELDS = ['sentence_index',
                           'word1', 'start1', 'end1',
                           'word2', 'start2', 'end2']
ProximityResult = namedtuple('ProximityResult', PROXIMITY_RESULT_FIELDS)


_TARGET_FIELDS = ['word_index', 'char_offset', 'word']
_Target = namedtuple('_Target', _TARGET_FIELDS)


###############################################################################
def _find_word_pairs(sentence_list, set1, set2, distance, any_order=False):
    """
    Find pairs of words in the given sentences, where one word of the pair
    is taken from set1 and the other word from set2. The params 'set1' and
    'set2' are sets of strings representing the search terms. The default
    search order takes words from set1 before those from set2. If the parameter
    'any_order' is set to True, word order is ignored.

    The 'distance' parameter has been checked prior to calling this function
    and is known to be a positive integer >= 1.
    """

    results = []
    for s in range(len(sentence_list)):
        sentence = sentence_list[s].lower()

        # split on whitespace to get individual words
        words = sentence.split()

        targets1 = []
        targets2 = []
        char_offset = 0

        # search for each word in sentence s, save word index and char offset
        for i in range(len(words)):
            w = words[i]
            char_offset = sentence.find(w, char_offset)
            if w in set1:
                targets1.append( _Target(i, char_offset, w))
            if w in set2:
                targets2.append( _Target(i, char_offset, w))
                
            # prevent finding the same w again if it appears more than once
            char_offset += 1

        if 0 == len(targets1) or 0 == len(targets2):
            continue

        for t1 in targets1:
            for t2 in targets2:
                index1 = t1.word_index
                index2 = t2.word_index

                # skip same word in both lists at same index
                if index1 == index2:
                    continue

                # words from list 1 must precede those of list 2,
                # unless any_order is True
                if (index1 > index2) and not any_order:
                    continue

                if abs(index2 - index1) <= distance:
                    start1 = t1.char_offset
                    end1   = start1 + len(t1.word)
                    start2 = t2.char_offset
                    end2   = start2 + len(t2.word)

                    # write words in order of appearance in the text
                    if index1 < index2:
                        result = ProximityResult(s,
                                                 t1.word, start1, end1,
                                                 t2.word, start2, end2)
                    else:
                        result = ProximityResult(s,
                                                 t2.word, start2, end2,
                                                 t1.word, start1, end1)
                    results.append(result)
                    
    return results


###############################################################################
def _log_error(msg):
    """
    Print an error message to the log file.
    """

    log('TermProximityTask error: {0}'.format(msg))
    return


###############################################################################
class TermProximityTask(BaseTask):
    """
    A custom task for a term proximity search.
    """
    
    # use this name in NLPQL
    task_name = "TermProximityTask"

    def run_custom_task(self, temp_file, mongo_client: MongoClient):

        # get custom NLPQL params 'termset1', 'termset2', and 'word_distance'

        if 'termset1' not in self.pipeline_config.custom_arguments:
            _log_error("required NLPQL parameter 'termset1' not found.")
            return
        else:
            termset1 = self.pipeline_config.custom_arguments['termset1']

        if 'termset2' not in self.pipeline_config.custom_arguments:
            _log_error("required NLPQL parameter 'termset2' not found.")
            return
        else:
            termset2 = self.pipeline_config.custom_arguments['termset2']

        if 'word_distance' not in self.pipeline_config.custom_arguments:
            _log_error("required NLPQL parameter 'word_distance' not found.")
            return
        else:
            word_distance = self.pipeline_config.custom_arguments['word_distance']
        
            # convert to int if user entered distance as a string
            distance = word_distance
            if isinstance(word_distance, str):
                word_distance = word_distance.strip()
                if word_distance.isdigit():
                    # string is a valid number, consists of all digits
                    distance = int(word_distance)
                else:
                    _log_error('NLPQL parameter word_distance is invalid: {0}'.
                               format(distance))
                    return
            
            # error if negative distance; for 0 distance use TermFinder
            if distance <= 0:
                _log_error('NLPQL parameter word_distance is invalid: {0}'.
                           format(distance))
                return

        # get custom NLPQL param 'any_order'; default value is False
        if 'any_order' not in self.pipeline_config.custom_arguments:
            any_order = False
        else:
            any_order = self.pipeline_config.custom_arguments['any_order']

            # convert to bool if user entered as a string
            if isinstance(any_order, str):
                if 'true' == any_order.lower().strip():
                    any_order = True
                else:
                    any_order = False

        #log('*** PARAMS: ***')
        #log('\t distance: {0}'.format(distance))
        #log('\tany_order: {0}'.format(any_order))
        if type(termset1) == str:
            termset1 = termset1.strip('"').split(',')
        if type(termset2) == str:
            termset2 = termset2.strip('"').split(',')
        
        # normalize and remove any duplicates in each list
        set1 = set([t.lower().strip() for t in termset1])
        set2 = set([t.lower().strip() for t in termset2])

        # for each document in the NLPQL-specified doc set
        for doc in self.docs:

            # all sentences in this document
            sentence_list = self.get_document_sentences(doc)

            # all term pairs found in this document
            result_list = _find_word_pairs(sentence_list, set1, set2,
                                           distance, any_order)
                
            if len(result_list) > 0:
                for result in result_list:
                    obj = {
                        'sentence':sentence_list[result.sentence_index],
                        'word1':result.word1,
                        'start1':result.start1,
                        'end1':result.end1,
                        'word2':result.word2,
                        'start2':result.start2,
                        'end2':result.end2,
                        'start': min(result.start1, result.start2),
                        'end': max(result.end1, result.end2),
                        'value':','.join([result.word1, result.word2])
                    }
            
                    self.write_result_data(temp_file, mongo_client, doc, obj)

