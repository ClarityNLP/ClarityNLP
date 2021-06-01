#!/usr/bin/env python3
"""

This is a custom task for extracting information on Covid-19 variants from
text. The task returns information about potential new outbreaks of Covid
variants.

Sample NLPQL:

    limit 100;

    phenotype "Covid Variant Finder" version "1";
    include ClarityCore version "1.0" called Clarity;

    documentset Docs:
        Clarity.createDocumentSet({
            "report_types":["Discharge Summary"]
        });

    define final CovidVariant:
        Clarity.CovidVariantTask({
            documentset: [Docs]
        });

    context Patient;

    
"""

import re
import json
from pymongo import MongoClient
from collections import namedtuple
from tasks.task_utilities import BaseTask
from algorithms import run_covid_variant_finder, CovidVariantTuple, EMPTY_COVID_VARIANT_FIELD

from claritynlp_logging import log, ERROR, DEBUG

_VERSION_MAJOR = 0
_VERSION_MINOR = 1


###############################################################################
class CovidVariantTask(BaseTask):
    """
    A custom task for finding information on Covid-19 variants.
    """
    
    # use this name in NLPQL
    task_name = "CovidVariantTask"

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

            # look for Covid-19 variants in each sentence
            for sentence in sentence_list:
                json_result = run_covid_variant_finder(sentence)
                json_data = json.loads(json_result)
                result_list = [CovidVariantTuple(**d) for d in json_data]
                
                if len(result_list) > 0:
                    for result in result_list:
                        obj = {
                            'sentence':result.sentence,
                            'covid':result.covid,
                            'possible':result.possible,
                            'related':result.related,
                            'emerging':result.emerging,
                            'spreading':result.spreading,
                            'variant':result.variant,
                            'symptom':result.symptom,
                            'case':result.case,
                            'illness':result.illness,
                            'spike':result.spike,
                            'clade':result.clade,
                            'location':result.location,
                            'pango':result.pango,
                            'british':result.british,
                            'amino':result.amino,
                        }
                        
                        self.write_result_data(temp_file, mongo_client, doc, obj)

