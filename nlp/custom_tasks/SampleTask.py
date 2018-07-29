from tasks.task_utilities import BaseTask
from pymongo import MongoClient
import util


class SampleTask(BaseTask):
    task_name = "MyCustomTask"

    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        for doc in self.docs:
            txt = self.get_document_text(doc)

            # My custom stuff here
            length = len(txt)
            if length > 0:
                sentences = self.get_document_sentences(doc)

                obj = dict()
                obj['value'] = length
                obj['first_character'] = txt[0]
                obj['last_character'] = txt[-1]
                if len(sentences) > 0:
                    obj['first_sentence'] = sentences[0]
                    obj['last_sentence'] = sentences[-1]

                # writing results
                self.write_result_data(temp_file, mongo_client, doc, obj)

                # writing to log
                self.write_log_data("Whatever", "done writing sample data")


