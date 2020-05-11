#!/usr/bin/env python3
"""

This is a custom task for extracting Oxygen saturation information from
clinical text.

Sample NLPQL:

    limit 100;

    phenotype "O2Saturation Finder" version "1";
    include ClarityCore version "1.0" called Clarity;

    documentset Docs:
        Clarity.createDocumentSet({
            "report_types":["Discharge Summary"]
        });

    define final O2Saturation:
        Clarity.O2SaturationTask({
            documentset: [Docs]
        });

    context Patient;

    
"""

import re
import json
from pymongo import MongoClient
from collections import namedtuple
from tasks.task_utilities import BaseTask
from algorithms import run_o2sat_finder, O2Tuple, EMPTY_O2_FIELD

_VERSION_MAJOR = 0
_VERSION_MINOR = 1


###############################################################################
class O2SaturationTask(BaseTask):
    """
    A custom task for finding Oxygen saturation information.
    """
    
    # use this name in NLPQL
    task_name = "O2SaturationTask"

    def run_custom_task(self, temp_file, mongo_client: MongoClient):

        # for each document in the documentset
        for doc in self.docs:

            # get all sentences in this document
            sentence_list = self.get_document_sentences(doc)

            # look for O2 saturation data in each sentence
            for sentence in sentence_list:
                json_result = run_o2sat_finder(sentence)
                json_data = json.loads(json_result)
                result_list = [O2Tuple(**d) for d in json_data]
                
                if len(result_list) > 0:
                    for result in result_list:
                        obj = {
                            'sentence':result.sentence,
                            'text':result.text,
                            'start':result.start,
                            'end':result.end,
                            'device':result.device,
                            'flow_rate':result.flow_rate,
                            'condition':result.condition,
                            'value':result.value,
                            'value2':result.value2,
                            'pao2':result.pao2,
                            'pao2_est':result.pao2_est,
                            'fio2':result.fio2,
                            'fio2_est':result.fio2_est,
                            'p_to_f_ratio':result.p_to_f_ratio,
                            'p_to_f_ratio_est':result.p_to_f_ratio_est,
                        }
                        
                        self.write_result_data(temp_file, mongo_client, doc, obj)

