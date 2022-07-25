"""

This is a custom task for finding a patient's sexual orientation.

Sample NLPQL:

    limit 100;

    phenotype "SDOH Sexual Orientation Finder Task" version "1";
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

    define final SexualOrientationFinderResults:
        Clarity.SexualOrientationFinderTask({
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
from algorithms import run_sexual_orientation_finder, SexualOrientationTuple


_VERSION_MAJOR = 0
_VERSION_MINOR = 1


###############################################################################
class SexualOrientationFinderTask(BaseTask):
    """   
    A custom task for finding a patient's immigration status.
    """

    # use this name in NLPQL
    task_name = 'SexualOrientationFinderTask'

    def run_custom_task(self, temp_file, mongo_client: MongoClient):

        for doc in self.docs:
            sentence_list = self.get_document_sentences(doc)
            for sentence in sentence_list:
                json_result = run_sexual_orientation_finder(sentence)
                json_data = json.loads(json_result)
                result_list = [SexualOrientationTuple(**d) for d in json_data]

                if len(result_list) > 0:
                    for result_obj in result_list:
                        # need a dict here, not a namedtuple
                        obj = {
                            'sentence' : result_obj.sentence,
                            'sexual_orientation' : result_obj.sexual_orientation,
                        }
                        
                        self.write_result_data(temp_file, mongo_client, doc, obj)

