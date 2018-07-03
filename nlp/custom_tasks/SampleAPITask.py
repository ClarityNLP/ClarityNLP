from tasks.task_utilities import BaseTask
from pymongo import MongoClient
import requests


class SampleAPITask(BaseTask):
    task_name = "ChuckNorrisJokeTask"

    # NLPQL

    # define sampleTask:
    # Clarity.ChuckNorrisJokeTask({
    #   documentset: [ProviderNotes]
    # });

    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        for doc in self.docs:

            # get a joke for each document
            # ¯\_(ツ)_/¯

            response = requests.post('http://api.icndb.com/jokes/random')
            if response.status_code == 200:
                json_response = response.json()
                if json_response['type'] == 'success':
                    val = json_response['value']
                    obj = {
                        'joke': val['joke']
                    }

                    # writing results
                    self.write_result_data(temp_file, mongo_client, doc, obj)

            else:
                # writing to log (optional)
                self.write_log_data("OOPS", "No jokes this time!")
