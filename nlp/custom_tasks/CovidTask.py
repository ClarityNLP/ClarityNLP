#!/usr/bin/env python3
"""

This is a custom task for extracting Covid-19 information from text. The task
returns the number of case reports, hospitalizations, and deaths
due to Covid-19.

Sample NLPQL:

    limit 100;

    phenotype "Covid Finder" version "1";
    include ClarityCore version "1.0" called Clarity;

    documentset Docs:
        Clarity.createDocumentSet({
            "report_types":["Discharge Summary"]
        });

    define final Covid:
        Clarity.CovidTask({
            documentset: [Docs]
        });

    context Patient;

    
"""

import re
import json
from pymongo import MongoClient
from collections import namedtuple
from tasks.task_utilities import BaseTask
from algorithms import run_covid_finder, CovidTuple, EMPTY_COVID_FIELD

from claritynlp_logging import log, ERROR, DEBUG

_VERSION_MAJOR = 0
_VERSION_MINOR = 2


###############################################################################
class CovidTask(BaseTask):
    """
    A custom task for finding the number of reported cases, hospitalizations,
    and deaths related to Covid-19.
    """
    
    # use this name in NLPQL
    task_name = "CovidTask"

    def run_custom_task(self, temp_file, mongo_client: MongoClient):

        # for each document in the documentset
        for doc in self.docs:

            # skip any doc with a missing 'subject' field
            if 'subject' not in doc:
                if 'id' in doc:
                    log('***** DOC ID WITH MISSING SUBJECT FIELD: {0}'.
                        format(doc['id']))
                else:
                    log('***** DOC WITH MISSING SUBJECT FIELD: {0}'.
                        format(doc))
                continue

            # get all sentences in this document
            sentence_list = self.get_document_sentences(doc)

            # look for Covid-19 counts in each sentence
            for sentence in sentence_list:
                json_result = run_covid_finder(sentence)
                json_data = json.loads(json_result)
                result_list = [CovidTuple(**d) for d in json_data]
                
                if len(result_list) > 0:
                    for result in result_list:
                        obj = {
                            'sentence':result.sentence,
                            'case_start':result.case_start,
                            'case_end':result.case_end,
                            'hosp_start':result.hosp_start,
                            'hosp_end':result.hosp_end,
                            'death_start':result.death_start,
                            'death_end':result.death_end,
                            'text_case':result.text_case,
                            'text_hosp':result.text_hosp,
                            'text_death':result.text_death,
                            'value_case':result.value_case,
                            'value_hosp':result.value_hosp,
                            'value_death':result.value_death,
                        }
                        
                        self.write_result_data(temp_file, mongo_client, doc, obj)

