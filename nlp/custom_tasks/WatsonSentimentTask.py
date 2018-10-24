from tasks.task_utilities import BaseTask
from pymongo import MongoClient
import requests


class WatsonSentimentTask(BaseTask):
    task_name = "WatsonSentiment"

    # define sampleTask:
    # Clarity.WatsonSentiment({
    #   documentset: [ProviderNotes],
    #   "api_key": "{your_api_key}",
    #   "authorization":"{your_authorization}"
    # });

    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        for doc in self.docs:

            sentence_list = self.get_document_sentences(doc)

            for sentence in sentence_list:
                if any(word.lower() in sentence.lower() for word in self.pipeline_config.terms):
                    headers = {'Content-Type': 'application/json', 'apikey': self.pipeline_config.custom_arguments['api_key'], 'authorization': self.pipeline_config.custom_arguments['authorization']}
                    self.write_log_data("INFO", self.pipeline_config.custom_arguments['api_key'])

                    payload = {"text": sentence}
                    response = requests.post('https://gateway.watsonplatform.net/tone-analyzer/api/v3/tone?version=2017-09-21', headers=headers, json=payload)
                    if response.status_code == 200:
                        json_response = response.json()
                        tones = json_response['document_tone']['tones']
                        for tone in tones:
                            obj = {
                                'tone_name': tone['tone_name'],
                                'tone_score': tone['score'],
                                'sentence': sentence
                            }

                            # writing results
                            self.write_result_data(temp_file, mongo_client, doc, obj)

                    else:
                        # writing to log (optional)
                        self.write_log_data("OOPS", "No sentiment this time!")
