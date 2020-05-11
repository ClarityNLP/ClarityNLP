from pymongo import MongoClient

from algorithms import *
from .task_utilities import BaseTask

SECTIONS_FILTER = "sections"

class ValueExtractorTask(BaseTask):
    task_name = "ValueExtractor"

    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        filters = dict()
        if self.pipeline_config.sections and len(self.pipeline_config.sections) > 0:
            filters[SECTIONS_FILTER] = self.pipeline_config.sections

        # default behavior is to extract the NUMERATOR of fractions
        denom_only = False
        if 'denom_only' in self.pipeline_config.custom_arguments:
            value = self.pipeline_config.custom_arguments['denom_only']
            if isinstance(value, str):
                if len(arg_str) > 0 and arg_str.startswith( ('T','t') ):
                    denom_only = True
                else:
                    denom_only = False
            elif isinstance(value, bool):
                denom_only = value

        # default behavior is to look for values AFTER the query terms
        values_before_terms = False
        if 'values_before_terms' in self.pipeline_config.custom_arguments:
            value = self.pipeline_config.custom_arguments['values_before_terms']
            if isinstance(value, str):
                if len(value) > 0 and value.startswith( ('T','t') ):
                    values_before_terms = True
                else:
                    values_before_terms = False
            elif isinstance(value, bool):
                values_before_terms = value
            
        # TODO incorporate sections and filters
        for doc in self.docs:
            result = run_value_extractor_full(term_list = self.pipeline_config.terms,
                                              text = self.get_document_text(doc),
                                              minimum_value = self.pipeline_config.minimum_value,
                                              maximum_value = self.pipeline_config.maximum_value,
                                              enumlist = self.pipeline_config.enum_list,
                                              is_case_sensitive_text = self.pipeline_config.case_sensitive,
                                              denom_only = denom_only,
                                              values_before_terms = values_before_terms)
            if result:
                for meas in result:
                    value = meas['X']

                    obj = {
                        "sentence": meas.sentence,
                        "text": meas.text,
                        "start": meas.start,
                        "end": meas.end,
                        "term": meas.matching_terms,
                        "condition": meas.condition,
                        "value": value,
                        "value1": meas.X,
                        "value2": meas.Y,
                        "min_value":meas.min_value,
                        "max_value":meas.max_value,
                        "result_display": {
                            "date": doc[util.solr_report_date_field],
                            "result_content": "{0}".format(meas.text),
                            "sentence": meas.sentence,
                            "highlights": [meas.text],
                            "start": [meas.start],
                            "end": [meas.end]
                        }
                    }
                    self.write_result_data(temp_file, mongo_client, doc, obj)

                del result
            else:
                temp_file.write("no matches!\n")
