from tasks.task_utilities import BaseTask
from pymongo import MongoClient
import requests


class SentimentAPITask(BaseTask):
    task_name = "AzureSentiment"

    # NLPQL

    # define sampleTask:
    # Clarity.AzureSentiment({
    #   documentset: [ProviderNotes]
    # });

    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        for doc in self.docs:
            txt = self.get_document_text(doc)
            headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': 'f2c27101438f40928132a93b9257abb9'}
            payload = {"documents": [{"language": "en", "id": "1", "text": txt}]}
            response = requests.post('https://eastus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment', headers=headers, data=payload)
            if response.status_code == 200:
                json_response = response.json()
                if json_response['errors'] == []:
                    val = json_response['documents']
                    obj = {
                        'score': val['score']
                    }

                    # writing results
                    self.write_result_data(temp_file, mongo_client, doc, obj)

            else:
                # writing to log (optional)
                self.write_log_data("OOPS", "No sentiment this time!")
