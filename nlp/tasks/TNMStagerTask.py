from pymongo import MongoClient
from algorithms import run_tnm_stager_full
from .task_utilities import BaseTask


class TNMStagerTask(BaseTask):

    task_name = "TNMStager"

    def run_custom_task(self, temp_file, mongo_client: MongoClient):
            for doc in self.docs:
                results = run_tnm_stager_full(doc["report_text"], term_list=self.pipeline_config.terms)
                for obj in results:
                    self.write_result_data(temp_file, mongo_client, doc, obj)

