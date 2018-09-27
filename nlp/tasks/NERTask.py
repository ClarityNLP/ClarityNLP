from pymongo import MongoClient

from algorithms import get_standard_entities
from .task_utilities import BaseTask

SECTIONS_FILTER = "sections"


class NERTask(BaseTask):
    task_name = "NamedEntityRecognition"

    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        pipeline_config = self.pipeline_config

        filters = dict()
        if pipeline_config.sections and len(pipeline_config.sections) > 0:
            filters[SECTIONS_FILTER] = pipeline_config.sections

        # TODO incorporate sections and filters
        for doc in self.docs:
            res = get_standard_entities(self.get_document_text(doc))
            for val in res:
                obj = {
                    "term": val.text,
                    "text": val.text,
                    "start": val.start,
                    "end": val.end,
                    "label": val.label,
                    "description": val.description
                }
                self.write_result_data(temp_file, mongo_client, doc, obj)
