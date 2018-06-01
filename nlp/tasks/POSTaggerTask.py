import luigi
from data_access import solr_data
from data_access import pipeline_config as config
from algorithms import get_tags, segmentation
from data_access import jobs
from pymongo import MongoClient
from .task_utilties import pipeline_mongo_writer
import util
import traceback
import sys

SECTIONS_FILTER = "sections"


class POSTaggerTask(luigi.Task):
    pipeline = luigi.IntParameter()
    job = luigi.IntParameter()
    start = luigi.IntParameter()
    batch = luigi.IntParameter()
    solr_query = luigi.Parameter()
    segment = segmentation.Segmentation()

    def run(self):
        client = MongoClient(util.mongo_host, util.mongo_port)

        try:
            jobs.update_job_status(str(self.job), util.conn_string, jobs.IN_PROGRESS,
                                   "Running POSTagger Batch %s" %
                                   self.batch)

            pipeline_config = config.get_pipeline_config(self.pipeline, util.conn_string)

            jobs.update_job_status(str(self.job), util.conn_string, jobs.IN_PROGRESS, "Running Solr query")
            docs = solr_data.query(self.solr_query, rows=util.row_count, start=self.start, solr_url=util.solr_url,
                                   tags=pipeline_config.report_tags, mapper_inst=util.report_mapper_inst,
                                   mapper_url=util.report_mapper_url, mapper_key=util.report_mapper_key,
                                   cohort_ids=pipeline_config.cohort)

            filters = dict()
            if pipeline_config.sections and len(pipeline_config.sections) > 0:
                filters[SECTIONS_FILTER] = pipeline_config.sections

            with self.output().open('w') as outfile:
                jobs.update_job_status(str(self.job), util.conn_string, jobs.IN_PROGRESS,
                                       "Running POSTagger")
                # TODO incorporate sections and filters
                for doc in docs:
                    res = get_tags(doc["report_text"])
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
                        inserted = pipeline_mongo_writer(client, self.pipeline, "POSTagger", self.job,
                                                         self.batch,
                                                         pipeline_config, doc, obj)
                        outfile.write(str(inserted))
                        outfile.write('\n')
                    del res
            del docs
        except Exception as ex:
            traceback.print_exc(file=sys.stderr)
            jobs.update_job_status(str(self.job), util.conn_string, jobs.WARNING, ''.join(traceback.format_stack()))
            print(ex)
        finally:
            client.close()

    def output(self):
        return luigi.LocalTarget("%s/pipeline_job%s_pos_batch%s.txt" % (util.tmp_dir, str(self.job),
                                                                        str(self.start)))
