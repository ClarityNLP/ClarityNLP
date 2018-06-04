import sys
import traceback

import luigi
from pymongo import MongoClient

import util
from algorithms import run_tnm_stager_full

from data_access import jobs
from data_access import pipeline_config as config
from data_access import solr_data
from .task_utilities import pipeline_mongo_writer

task_name = "TNMStager"


class TNMStagerTask(luigi.Task):
    pipeline = luigi.IntParameter()
    job = luigi.IntParameter()
    start = luigi.IntParameter()
    batch = luigi.IntParameter()
    solr_query = luigi.Parameter()

    def run(self):
        client = MongoClient(util.mongo_host, util.mongo_port)
        try:
            jobs.update_job_status(str(self.job), util.conn_string, jobs.IN_PROGRESS,
                                   "Running %s Batch %s" %
                                   (self.batch, task_name))

            pipeline_config = config.get_pipeline_config(self.pipeline, util.conn_string)

            jobs.update_job_status(str(self.job), util.conn_string, jobs.IN_PROGRESS, "Running Solr query")
            docs = solr_data.query(self.solr_query, rows=util.row_count, start=self.start, solr_url=util.solr_url,
                                   tags=pipeline_config.report_tags,
                                   report_type_query=pipeline_config.report_type_query,
                                   mapper_inst=util.report_mapper_inst,
                                   mapper_url=util.report_mapper_url, mapper_key=util.report_mapper_key,
                                   cohort_ids=pipeline_config.cohort)

            with self.output().open('w') as outfile:
                jobs.update_job_status(str(self.job), util.conn_string, jobs.IN_PROGRESS,
                                       "Finding items with %s" % task_name)
                for doc in docs:
                    results = run_tnm_stager_full(doc["report_text"], term_list=pipeline_config.terms)
                    for obj in results:
                        inserted = pipeline_mongo_writer(client, self.pipeline, task_name, self.job, self.batch,
                                                         pipeline_config, doc, obj)
                        outfile.write(str(inserted))
                        outfile.write('\n')

            del docs
        except Exception as ex:
            traceback.print_exc(file=sys.stderr)
            jobs.update_job_status(str(self.job), util.conn_string, jobs.WARNING, ''.join(traceback.format_stack()))
            print(ex)
        finally:
            client.close()

    def output(self):
        return luigi.LocalTarget("%s/pipeline_job%s_%s_batch%s.txt" % (util.tmp_dir, str(self.job), task_name.lower(),
                                                                       str(self.start)))
