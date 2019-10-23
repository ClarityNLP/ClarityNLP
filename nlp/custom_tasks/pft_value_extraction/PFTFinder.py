import ast
from tasks.task_utilities import BaseTask
from pymongo import MongoClient
import util
from claritynlp_logging import log, ERROR, DEBUG


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
                for s in self.get_document_sentences(doc):
                    obj = ast.literal_eval(pftex(s))
                    if obj and obj['results']:
                        if len(obj['results']) > 0:
                            self.write_result_data(temp_file, mongo_client, doc, obj)

                # writing to log
                self.write_log_data("TASK_COMPLETE", "done writing data")
