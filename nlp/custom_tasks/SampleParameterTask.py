from tasks.task_utilities import BaseTask
from pymongo import MongoClient
import util
from claritynlp_logging import log, ERROR, DEBUG



class SampleParameterTask(BaseTask):
    task_name = "ParameterTask"

    # NLPQL

    # define withParams:
    #     Clarity.ParameterTask({
    #         documentset: [ProviderNotes],
    #         "greeting": "hello",
    #         "bye": "adios!",
    #         "great": true,
    #         "big_value": 100000,
    #         "small_value": 0.1
    #     });

    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        for doc in self.docs:
            txt = self.get_document_text(doc)

            length = len(txt)
            if length > 0:
                sentences = self.get_document_sentences(doc)

                for s in sentences:
                    if len(s) > 0:
                        tokens = s.split()
                        greet = self.pipeline_config.custom_arguments['greeting']
                        log(greet + ' world!')
                        obj = {
                            "greeting": greet + tokens[0],
                            "bye": self.pipeline_config.custom_arguments["bye"] + tokens[-1],
                            "big_value": self.pipeline_config.custom_arguments['big_value'],
                            "small_value": self.pipeline_config.custom_arguments["small_value"],
                            "what_is_this": "parameters!"
                        }
                        self.write_result_data(temp_file, mongo_client, doc, obj)

