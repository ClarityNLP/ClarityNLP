import sys

import luigi
from pymongo import MongoClient

from data_access import jobs
from data_access import pipeline_config as config
from data_access import solr_data
from algorithms import *
from .task_utilties import pipeline_mongo_writer

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

        current_doc = None
        try:
            jobs.update_job_status(str(self.job), util.conn_string, jobs.IN_PROGRESS,
                                   "Running ValueExtractor Batch %s" %
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
                                       "Finding terms with ValueExtractor")
                # TODO incorporate sections and filters
                for doc in docs:
                    current_doc = doc
                    result = run_value_extractor_full(pipeline_config.terms, doc["report_text"], float(pipeline_config.
                                                                                                       minimum_value),
                                                      float(pipeline_config.maximum_value), pipeline_config.
                                                      case_sensitive)
                    if result:
                        for meas in result:
                            value = meas['X']

                            obj = {
                                "sentence": meas.sentence,
                                "text": meas.text,
                                "start": meas.start,
                                "value": value,
                                "end": meas.end,
                                "term": meas.subject,
                                "dimension_X": meas.X,
                                "dimension_Y": meas.Y,
                                "dimension_Z": meas.Z,
                                "units": meas.units,
                                "location": meas.location,
                                "condition": meas.condition,
                                "value1": meas.value1,
                                "value2": meas.value2,
                                "temporality": meas.temporality
                            }
                            inserted = pipeline_mongo_writer(client, self.pipeline, "ValueExtractor", self.job,
                                                             self.batch,
                                                             pipeline_config, doc, obj)
                            outfile.write(str(inserted))
                            outfile.write('\n')
                        del result
                    else:
                        outfile.write("no matches!\n")
            del docs
        except AssertionError as a:
            print(a)
            print(current_doc)
        except Exception as ex:
            traceback.print_exc(file=sys.stderr)
            jobs.update_job_status(str(self.job), util.conn_string, jobs.WARNING,
                                   'Report ID: ' + current_doc['report_id'] + '\n'
                                                                              ''.join(traceback.format_stack()))
            print(ex)
            # print(current_doc)
        finally:
            client.close()

    def output(self):
        return luigi.LocalTarget("%s/pipeline_job%s_value_extractor_batch%s.txt" % (util.tmp_dir, str(self.job),
                                                                                    str(self.start)))
