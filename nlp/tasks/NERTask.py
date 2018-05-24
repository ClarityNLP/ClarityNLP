import luigi
from data_access import solr_data
from data_access import pipeline_config as config
from nlp import get_standard_entities, segmentation
from data_access import jobs
from pymongo import MongoClient
import datetime
import util
import traceback
import sys

SECTIONS_FILTER = "sections"


def mongo_writer(client, pipeline, job, batch, pipeline_config: config.PipelineConfig, val, doc, type):
    db = client[util.mongo_db]

    obj = {
        "pipeline_type": type,
        "pipeline_id": pipeline,
        "job_id": job,
        "batch": batch,
        "owner": pipeline_config.owner,
        "sentence": val.sentence,
        "report_type": doc["report_type"],
        "nlpql_feature": pipeline_config.name,
        "inserted_date": datetime.datetime.now(),
        "report_id": doc["report_id"],
        "subject": doc["subject"],
        "report_date": doc["report_date"],
        "section": "",
        "concept_code": pipeline_config.concept_code,
        "term": val.text,
        "text": val.text,
        "start": val.start,
        "end": val.end,
        "label": val.label,
        "description": val.description,
        "phenotype_final": False
    }

    inserted = config.insert_pipeline_results(pipeline_config, db, obj)

    return inserted


class NERTask(luigi.Task):
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
                                   "Running NamedEntityRecognition Batch %s" %
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
                                       "Finding terms with NamedEntityRecognition")
                # TODO incorporate sections and filters
                for doc in docs:
                    res = get_standard_entities(doc["report_text"])
                    for val in res:
                        inserted = mongo_writer(client, self.pipeline, self.job, self.batch, pipeline_config, val, doc,
                                                "NamedEntityRecognition")
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
        return luigi.LocalTarget("%s/pipeline_job%s_ner_batch%s.txt" % (util.tmp_dir, str(self.job),
                                                                                       str(self.start)))
