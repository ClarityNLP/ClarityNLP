"""

This is a custom task for finding a patient's immigration status.

Sample NLPQL:

    limit 100;

    phenotype "SDOH Immigration Status Task" version "1";
    include ClarityCore version "1.0" called Clarity;

    documentset Docs:
        Clarity.createDocumentSet({
            "report_types":[
                "Nursing/other",
                "Nursing Progress Note",
                "Nursing Transfer Note",
                "Social Work",
                "Physician ",
                "Discharge summary"
            ]
        });

    define final ImmigrationStatusFinderResults:
        Clarity.ImmigrationStatusFinderTask({
            documentset: [Docs]
        });

    context Patient;

"""

import os
import re
import sys
import json

from pymongo import MongoClient
from tasks.task_utilities import BaseTask
from algorithms import run_immigration_status_finder, ImmigrationTuple


_VERSION_MAJOR = 0
_VERSION_MINOR = 1


###############################################################################
class ImmigrationStatusFinderTask(BaseTask):
    """
    A custom task for finding a patient's immigration status.
    """

    # use this name in NLPQL
    task_name = 'ImmigrationStatusFinderTask'

    def run_custom_task(self, temp_file, mongo_client: MongoClient):

        for doc in self.docs:
            sentence_list = self.get_document_sentences(doc)
            for sentence in sentence_list:
                json_result = run_immigration_status_finder(sentence)
                json_data = json.loads(json_result)
                result_list = [ImmigrationTuple(**d) for d in json_data]

                if len(result_list) > 0:
                    for result_obj in result_list:
                        # need a dict here, not a namedtuple
                        obj = {
                            'sentence' : result_obj.sentence,
                            'immigration_status' : result_obj.immigration_status
                        }
                        
                        self.write_result_data(temp_file, mongo_client, doc, obj)

