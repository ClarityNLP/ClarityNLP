#!/usr/bin/env python3
"""

This is a custom task for extracting a patient's race (i.e. asian,
african american, caucasian, etc.).

Sample NLPQL, results written to the intermediate_results file:

    limit 100;

    phenotype "Race Finder" version "1";
    include ClarityCore version "1.0" called Clarity;

    documentset DischargeSummaries:
        Clarity.createReportTagList(["Discharge Summary"]);

    define RaceFinderFunction:
        Clarity.RaceFinderTask({
            documentset: [DischargeSummaries]
        });
"""

import util
import re
import json
from pymongo import MongoClient
from collections import namedtuple
from tasks.task_utilities import BaseTask, pipeline_cache, document_sentences, document_text,\
    get_document_by_id
from cachetools import cached

race_terms = ["white","caucasian","black","african american","asian","pacific islander","alaska native",
              "native american", "native hawaiian"]
str_sep = r'(\s-\s|-\s|\s-|\s)'
str_word = r'\b[-a-z.\d]+'
str_punct = r'[,.\s]*'
str_words = r'(' + str_word + str_punct + r'){0,6}'
str_person = r'\b(gentleman|gentlewoman|male|female|man|woman|person|' + \
             r'child|boy|girl|infant|baby|newborn|neonate|individual)\b'
str_category = r'\b(american' + str_sep + r'indian|' + \
               r'alaska' + str_sep + r'native|asian|' + \
               r'african' + str_sep + r'american|black|negro|' + \
               r'native' + str_sep + r'hawaiian|' + \
               r'other' + str_sep + r'pacific' + str_sep + r'islander|' + \
               r'pacific' + str_sep + r'islander|' + \
               r'native' + str_sep + r'american|' + \
               r'white|caucasian|european)'

str_race1 = r'(\brace:?\s*)' + r'(?P<category>' + str_category + r')'
regex_race1 = re.compile(str_race1, re.IGNORECASE)
str_race2 = r'(?P<category>' + str_category + r')' + str_punct + \
            str_words + str_person
regex_race2 = re.compile(str_race2, re.IGNORECASE)
str_race3 = str_person + str_punct + str_words + r'(?P<category>' + \
            str_category + r')'
regex_race3 = re.compile(str_race3, re.IGNORECASE)
REGEXES = [regex_race1, regex_race2, regex_race3]

RACE_FINDER_RESULT_FIELDS = ['sentence_index', 'start', 'end', 'race',
                             'normalized_race']
RaceFinderResult = namedtuple('RaceFinderResult', RACE_FINDER_RESULT_FIELDS)


###############################################################################
def normalize(race_text):
    """
    Convert a matching race string to a 'normalized' version.
    """

    NORM_MAP = {
        'african american': 'black',
        'negro': 'black',
        'caucasian': 'white',
        'european': 'white',
    }

    # convert to lowercase, remove dashes, collapse repeated whitespace
    race = race_text.lower()
    race = re.sub(r'[-]+', '', race)
    race = re.sub(r'\s+', ' ', race)

    if race in NORM_MAP:
        return NORM_MAP[race]
    else:
        return race


###############################################################################
def find_race(sentence_list):
    """
    Scan a list of sentences and run race-finding regexes on each.
    Returns a list of RaceFinderResult namedtuples. Currently returns only
    the first result found.
    """

    result_list = []

    found_match = False
    for i in range(len(sentence_list)):
        s = sentence_list[i]
        for regex in REGEXES:
            match = regex.search(s)
            if match:
                match_text = match.group('category')
                start = match.start()
                end = match.end()
                normalized = normalize(match_text)
                result = RaceFinderResult(i, start, end, match_text, normalized)
                result_list.append(result)
                found_match = True
                break

        # Reports are unlikely to have more than one sentence stating the
        # patient's race.
        if found_match:
            break

    return result_list


###############################################################################


def get_race_for_doc(document_id):
    doc = get_document_by_id(document_id)
    # all sentences in this document
    sentence_list = document_sentences(doc)

    # all race results in this document
    result_list = find_race(sentence_list)

    if len(result_list) == 0:
        sentence_list = list()

    return {
        'sentences': sentence_list,
        'results': result_list
    }


@cached(pipeline_cache)
def _get_race_data(document_id):
    util.add_cache_compute_count()
    return get_race_for_doc(document_id)


def get_race_data(document_id):
    if util.use_redis_caching == "true":
        util.add_cache_query_count()
        key = "raceFinder:" + str(document_id)
        res = util.get_from_redis_cache(key)
        if res:
            return json.loads(res)
        else:
            util.add_cache_compute_count()
            res2 = get_race_for_doc(document_id)
            util.write_to_redis_cache(key, json.dumps(res2))
            return res2
    elif util.use_memory_caching == "true":
        util.add_cache_query_count()
        return _get_race_data(document_id)
    else:
        return get_race_for_doc(document_id)


class RaceFinderTask(BaseTask):
    """
    A custom task for finding a patient's race.
    """

    # use this name in NLPQL
    task_name = "RaceFinderTask"

    def run_custom_task(self, temp_file, mongo_client: MongoClient):

        # for each document in the NLPQL-specified doc set
        for doc in self.docs:
            obj = get_race_data(doc[util.solr_report_id_field])

            result_list = obj['results']
            sentence_list = obj['sentences']
            if len(result_list) > 0:
                for result in result_list:
                    if isinstance(result, list):
                        obj = {
                            'sentence': sentence_list[result[0]],
                            'start': result[1],
                            'end': result[2],
                            'value': result[3],
                            'value_normalized': result[4],
                        }
                    else:
                        obj = {
                            'sentence': sentence_list[result.sentence_index],
                            'start': result.start,
                            'end': result.end,
                            'value': result.race,
                            'value_normalized': result.normalized_race,
                        }

                    self.write_result_data(temp_file, mongo_client, doc, obj)

