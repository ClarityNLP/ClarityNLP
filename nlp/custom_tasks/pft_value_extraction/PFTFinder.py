import ast
from tasks.task_utilities import BaseTask
from pymongo import MongoClient
import util

try:
    from .pft_algo import pft_extractor as pftex
except Exception as e:
    from pft_algo import pft_extractor as pftex


class PFTFinder(BaseTask):
    task_name = "PFTFinder"

    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        for doc in self.docs:
            txt = self.get_document_text(doc)

            # My custom stuff here
            length = len(txt)
            if length > 0:
                obj = ast.literal_eval(pftex(txt))

                # writing results
                self.write_result_data(temp_file, mongo_client, doc, obj)

                # writing to log
                self.write_log_data("PFT", "done writing data")
