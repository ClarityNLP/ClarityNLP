import luigi
from data_access import solr_data
from data_access import pipeline_config as config
from nlp import *
from data_access import jobs
from pymongo import MongoClient
import util
from .MeasurementFinderTask import mongo_writer


SECTIONS_FILTER = "sections"


class ValueExtractorTask(luigi.Task):
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
                                   "Running ValueExtractor Batch %s" %
                                   self.batch)

            pipeline_config = config.get_pipeline_config(self.pipeline, util.conn_string)

            jobs.update_job_status(str(self.job), util.conn_string, jobs.IN_PROGRESS, "Running Solr query")
            docs = solr_data.query(self.solr_query, rows=util.row_count, start=self.start, solr_url=util.solr_url,
                                   tags=pipeline_config.report_tags, mapper_inst=util.report_mapper_inst,
                                   mapper_url=util.report_mapper_url, mapper_key=util.report_mapper_key)

            filters = dict()
            if pipeline_config.sections and len(pipeline_config.sections) > 0:
                filters[SECTIONS_FILTER] = pipeline_config.sections

            with self.output().open('w') as outfile:
                jobs.update_job_status(str(self.job), util.conn_string, jobs.IN_PROGRESS,
                                       "Finding terms with ValueExtractor")
                # TODO incorporate sections and filters
                for doc in docs:
                    result = process_sentence_full(pipeline_config.terms, doc["report_text"], float(pipeline_config.
                                                   minimum_value), float(pipeline_config.maximum_value), pipeline_config.
                                                   case_sensitive)
                    if result:
                        for val in result:
                            inserted = mongo_writer(client, self.pipeline, self.job, self.batch, pipeline_config, val, doc,
                                                    "ValueExtractor")
                            outfile.write(str(inserted))
                            outfile.write('\n')
                    else:
                        outfile.write("no matches!\n")
        except Exception as ex:
            jobs.update_job_status(str(self.job), util.conn_string, jobs.FAILURE, str(ex))
            print(ex)
        finally:
            client.close()

    def output(self):
        return luigi.LocalTarget("%s/pipeline_job%s_value_extractor_batch%s.txt" % (util.tmp_dir, str(self.job),
                                                                                str(self.start)))
