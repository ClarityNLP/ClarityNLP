import datetime
import sys
import traceback

import luigi
from pymongo import MongoClient
from algorithms import segmentation
import util
from data_access import jobs
from data_access import pipeline_config
from data_access import pipeline_config as config
from data_access import solr_data


def pipeline_mongo_writer(client, pipeline_id, pipeline_type, job, batch, p_config: pipeline_config.PipelineConfig,
                          doc, data_fields: dict):
    db = client[util.mongo_db]

    data_fields["pipeline_type"] = pipeline_type
    data_fields["pipeline_id"] = pipeline_id
    data_fields["job_id"] = job
    data_fields["batch"] = batch
    data_fields["owner"] = p_config.owner
    data_fields["nlpql_feature"] = p_config.name
    data_fields["inserted_date"] = datetime.datetime.now()
    data_fields["report_id"] = doc["report_id"]
    data_fields["subject"] = doc["subject"]
    data_fields["report_date"] = doc["report_date"]
    data_fields["concept_code"] = p_config.concept_code
    data_fields["phenotype_final"] = False

    inserted = config.insert_pipeline_results(p_config, db, data_fields)

    return inserted


class BaseTask(luigi.Task):

    pipeline = luigi.IntParameter()
    job = luigi.IntParameter()
    start = luigi.IntParameter()
    solr_query = luigi.Parameter()
    batch = luigi.IntParameter()
    task_name = "ClarityNLPLuigiTask"
    docs = list()
    pipeline_config = config.PipelineConfig('', '')
    segment = segmentation.Segmentation()

    def run(self):
        task_family_name = str(self.task_family)
        if self.task_name == "ClarityNLPLuigiTask":
            self.task_name = task_family_name
        client = MongoClient(util.mongo_host, util.mongo_port)

        try:
            jobs.update_job_status(str(self.job), util.conn_string, jobs.IN_PROGRESS, "Running Batch %s" %
                                   self.batch)

            self.pipeline_config = config.get_pipeline_config(self.pipeline, util.conn_string)
            jobs.update_job_status(str(self.job), util.conn_string, jobs.IN_PROGRESS, "Running Solr query")
            self.docs = solr_data.query(self.solr_query, rows=util.row_count, start=self.start, solr_url=util.solr_url,
                                        tags=self.pipeline_config.report_tags, mapper_inst=util.report_mapper_inst,
                                        mapper_url=util.report_mapper_url, mapper_key=util.report_mapper_key,
                                        types=self.pipeline_config.report_types,
                                        filter_query=self.pipeline_config.filter_query)

            with self.output().open('w') as temp_file:
                jobs.update_job_status(str(self.job), util.conn_string, jobs.IN_PROGRESS,
                                       "Running %s main task" % self.task_name)
                self.run_custom_task(temp_file, client)
                temp_file.write("Done writing custom task!")

            self.docs = list()
        except Exception as ex:
            traceback.print_exc(file=sys.stderr)
            jobs.update_job_status(str(self.job), util.conn_string, jobs.WARNING, ''.join(traceback.format_stack()))
            print(ex)
        finally:
            client.close()

    def output(self):
        return luigi.LocalTarget("%s/pipeline_job%s_%s_batch%s.txt" % (util.tmp_dir, str(self.job), self.task_name,
                                                                       str(self.start)))

    def set_name(self, name):
        self.task_name = name

    def write_result_data(self, temp_file, mongo_client, doc, data: dict):
        inserted = pipeline_mongo_writer(mongo_client, self.pipeline, self.task_name, self.job, self.batch,
                                         self.pipeline_config, doc, data)
        if temp_file is not None:
            temp_file.write(str(inserted))
            temp_file.write('\n')
        return inserted

    def write_multiple_result_data(self, temp_file, mongo_client, doc, data: list):
        ids = list()
        for d in data:
            inserted = pipeline_mongo_writer(mongo_client, self.pipeline, self.task_name, self.job, self.batch,
                                         self.pipeline_config, doc, d)
            ids.append(inserted)
            if temp_file is not None:
                temp_file.write(str(inserted))
                temp_file.write('\n')

        return ids

    def write_log_data(self, job_status, status_message):
        jobs.update_job_status(str(self.job), util.conn_string, job_status, status_message)

    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        print("Implement your custom functionality here ")

    def get_document_text(self, doc):
        if doc and 'report_text' in doc:
            return doc['report_text']
        else:
            return ''

    def get_document_sentences(self, doc):
        txt = self.get_document_text(doc)
        sentence_list = self.segment.parse_sentences(txt)
        return sentence_list

