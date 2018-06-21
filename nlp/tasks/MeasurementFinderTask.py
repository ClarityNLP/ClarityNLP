from algorithms import *
from pymongo import MongoClient
from .task_utilities import BaseTask

SECTIONS_FILTER = "sections"


class MeasurementFinderTask(BaseTask):
    task_name = "MeasurementFinder"

    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        filters = dict()
        if self.pipeline_config.sections and len(self.pipeline_config.sections) > 0:
            filters[SECTIONS_FILTER] = self.pipeline_config.sections

        for doc in self.docs:
            meas_results = run_measurement_finder_full(doc["report_text"], self.pipeline_config.terms)
            for meas in meas_results:
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

            del meas_results
