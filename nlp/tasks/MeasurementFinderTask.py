from pymongo import MongoClient

from algorithms import *
from .task_utilities import BaseTask

SECTIONS_FILTER = "sections"


class MeasurementFinderTask(BaseTask):
    task_name = "MeasurementFinder"

    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        filters = dict()
        if self.pipeline_config.sections and len(self.pipeline_config.sections) > 0:
            filters[SECTIONS_FILTER] = self.pipeline_config.sections

        for doc in self.docs:
            meas_results = run_measurement_finder_full(self.get_document_text(doc), self.pipeline_config.terms)
            for meas in meas_results:
                value = meas['X']
                obj = {
                    "sentence": meas.sentence,
                    "text": meas.text,
                    "start": meas.start,
                    "value": value,
                    "end": meas.end,
                    "term":meas.matching_terms,
                    "meas_object":meas.subject,
                    "dimension_X": meas.X,
                    "dimension_Y": meas.Y,
                    "dimension_Z": meas.Z,
                    "units": meas.units,
                    "location": meas.location,
                    "condition": meas.condition,
                    "value1": meas.value1,
                    "value2": meas.value2,
                    "temporality": meas.temporality,
                    "min_value": meas.min_value,
                    "max_value": meas.max_value,
                    "result_display": {
                        "date": doc[util.solr_report_date_field],
                        "result_content": "{0} {1} {2}".format(meas.text,
                                                               value,
                                                               meas.units),
                        "sentence": meas.sentence,
                        "highlights": [meas.text, value, meas.units],
                        "start": [meas.start],
                        "end": [meas.end]
                    }
                }

                self.write_result_data(temp_file, mongo_client, doc, obj)

            del meas_results
