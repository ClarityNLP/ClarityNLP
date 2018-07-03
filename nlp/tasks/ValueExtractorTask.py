from pymongo import MongoClient
import util
from algorithms import *
from .task_utilities import BaseTask

SECTIONS_FILTER = "sections"


class ValueExtractorTask(BaseTask):
    task_name = "ValueExtractor"

    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        filters = dict()
        if self.pipeline_config.sections and len(self.pipeline_config.sections) > 0:
            filters[SECTIONS_FILTER] = self.pipeline_config.sections

        # TODO incorporate sections and filters
        for doc in self.docs:
            result = run_value_extractor_full(self.pipeline_config.terms, doc[util.solr_text_field],
                                              float(self.pipeline_config.
                                                    minimum_value),
                                              float(self.pipeline_config.maximum_value), self.pipeline_config.
                                              case_sensitive)
            if result:
                for meas in result:
                    value = meas['X']

                    obj = {
                        "sentence": meas.sentence,
                        "text": meas.text,
                        "start": meas.start,
                        "value": value,
                        "end": meas.end,
                        "term": meas.subject,
                        "dimension_X": meas.X,
                        "dimension_Y": meas.Y,
                        "dimension_Z": meas.Z,
                        "units": meas.units,
                        "location": meas.location,
                        "condition": meas.condition,
                        "value1": meas.value1,
                        "value2": meas.value2,
                        "temporality": meas.temporality
                    }
                    self.write_result_data(temp_file, mongo_client, doc, obj)

                del result
            else:
                temp_file.write("no matches!\n")
