from tasks.task_utilities import BaseTask
from pymongo import MongoClient
from algorithms import run_transfusion_note_reader
import util
import json


# //phenotype name
# phenotype "transfusionTesting" version "2";
#
# //include Clarity main NLP libraries
# include ClarityCore version "1.0" called Clarity;
#
# documentset ColumbiaNotes:
# Clarity.createDocumentSet({
# 		"filter_query":"source:Columbia",
#        "report_types":["Nursing"]});
#
# define transfusionParser:
# 	Clarity.TransfusionNursingNotesParser({
# 	documentset: [ColumbiaNotes]
# 	});

class ColumbiaTransfusionTask(BaseTask):
    task_name = "TransfusionNursingNotesParser"

    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        for doc in self.docs:
            text = self.get_document_text(doc)
            json_str = run_transfusion_note_reader(text)

            if json_str:
                json_list = json.loads(json_str)
                for item in json_list:
                    obj = item['vitals']
                    obj['reaction'] = item['reaction']
                    obj['elapsedMinutes'] = item['elapsedMinutes']
                    obj['transfusionStart'] = item['transfusionStart']
                    obj['transfusionEnd'] = item['transfusionEnd']
                    obj['bloodProductOrdered'] = item['bloodProductOrdered']
                    self.write_result_data(temp_file, mongo_client, doc, obj)
