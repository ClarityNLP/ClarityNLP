from tasks.task_utilities import BaseTask
from pymongo import MongoClient
import requests


class AzureSentimentTask(BaseTask):
    task_name = "AzureSentiment"

    # NLPQL

    # define sampleTask:
    # Clarity.AzureSentiment({
    #   documentset: [ProviderNotes],
    #   "api_key": "{your_api_key}"
    # });

    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        for doc in self.docs:

            headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': self.pipeline_config.custom_arguments['api_key']}

            sentence_list = self.get_document_sentences(doc)

            if self.pipeline_config.terms:
                for sentence in sentence_list:
                    if any(word.lower() in sentence.lower() for word in self.pipeline_config.terms):
                        payload = {"documents": [{"language": "en", "id": "1", "text": sentence}]}
                        self.write_log_data("RUNNING", "Processing Azure with Termset")
                        response = requests.post('https://eastus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment', headers=headers, json=payload)
                        if response.status_code == 200:
                            json_response = response.json()
                            val = json_response['documents'][0]
                            obj = {
                                'sentiment_score': val['score'],
                                'sentence': sentence
                            }

                            # writing results
                            self.write_result_data(temp_file, mongo_client, doc, obj)

                        else:
                            # writing to log (optional)
                            self.write_log_data("OOPS", "No sentiment this time!")
            else:
                for sentence in sentence_list:
                    payload = {"documents": [{"language": "en", "id": "1", "text": sentence}]}
                    self.write_log_data("RUNNING", "Processing Azure without Termset")
                    response = requests.post('https://eastus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment', headers=headers, json=payload)
                    if response.status_code == 200:
                        json_response = response.json()
                        val = json_response['documents'][0]
                        obj = {
                            'sentiment_score': val['score'],
                            'sentence': sentence
                        }

                        # writing results
                        self.write_result_data(temp_file, mongo_client, doc, obj)

                    else:
                        # writing to log (optional)
                        self.write_log_data("OOPS", "No sentiment this time!")
