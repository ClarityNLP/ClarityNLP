"""

This is a custom task for finding a patient's primary language(s).

Sample NLPQL:

    limit 100;

    phenotype "SDOH Task" version "1";
    include ClarityCore version "1.0" called Clarity;

    documentset Docs:
        Clarity.createDocumentSet({
            "report_types":["Discharge Summary"]
        });

    define final LanguageFinderResults:
        Clarity.LanguageFinderTask({
            documentset: [Docs]
        });

    context Patient;


"""

import os
import re
import sys
import json
import argparse
from collections import namedtuple

from pymongo import MongoClient
from tasks.task_utilities import BaseTask
from algorithms import run_language_finder, LanguageTuple

_VERSION_MAJOR = 0
_VERSION_MINOR = 1


###############################################################################
class LanguageFinderTask(BaseTask):
    """
    A custom task for finding a patient's primary language(s).
    """

    # use this name in NLPQL
    task_name = 'LanguageFinderTask'

    def run_custom_task(self, temp_file, mongo_client: MongoClient):

        for doc in self.docs:
            sentence_list = self.get_document_sentences(doc)
            for sentence in sentence_list:
                json_result = run_language_finder(sentence)
                json_data = json.loads(json_result)
                result_list = [LanguageTuple(**d) for d in json_data]

                if len(result_list) > 0:
                    for result_obj in result_list:
                        # need a dict here, not a namedtuple
                        obj = {
                            'sentence' : result_obj.sentence,
                            'languages' : result_obj.languages
                        }
                        
                        self.write_result_data(temp_file, mongo_client, doc, obj)

                

