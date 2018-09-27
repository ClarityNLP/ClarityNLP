from pymongo import MongoClient

from algorithms import get_tags
from .task_utilities import BaseTask

SECTIONS_FILTER = "sections"


class POSTaggerTask(BaseTask):

    task_name = "POSTagger"

    def run_custom_task(self, temp_file, mongo_client: MongoClient):

            # TODO incorporate sections and filters
            for doc in self.docs:
                res = get_tags(self.get_document_text(doc))
                for val in res:
                    obj = {
                        "sentence": val.sentence,
                        "term": val.text,
                        "text": val.text,
                        "lemma": val.lemma,
                        "pos": val.pos,
                        "tag": val.tag,
                        "dep": val.dep,
                        "shape": val.shape,
                        "is_alpha": val.is_alpha,
                        "is_stop": val.is_stop,
                        "description": val.description
                    }
                    self.write_result_data(temp_file, mongo_client, doc, obj)

                del res
