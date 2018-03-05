import luigi
from data_access import solr_data
from data_access import pipeline_config as config
from nlp import *
from data_access import jobs
from pymongo import MongoClient
import datetime
import util

provider_assertion_filters = {
    'negex': ["Affirmed"],
    "temporality": ["Recent", "Historical"],
    "experiencer": ["Patient"]
}


def mongo_writer(client, pipeline, job, batch, pipeline_config, term, doc):
    db = client[util.mongo_db]

    inserted = db.pipeline_results.insert_one({
        "pipeline_type": "TermFinder",
        "pipeline_id": pipeline,
        "job_id": job,
        "batch": batch,
        "owner": pipeline_config.owner,
        "sentence": term.sentence,
        "report_type": doc["report_type"],
        "nlpql_feature": pipeline_config.name,
        "inserted_date": datetime.datetime.now(),
        "report_id": doc["report_id"],
        "subject": doc["subject"],
        "report_date": doc["report_date"],
        "section": term.section,
        "term": term.term,
        "start": term.start,
        "end": term.end,
        "concept_code": pipeline_config.concept_code,
        "negation": term.negex,
        "temporality": term.temporality,
        "experiencer": term.experiencer
    }).inserted_id

    return inserted


class TermFinderBatchTask(luigi.Task):
    pipeline = luigi.IntParameter()
    job = luigi.IntParameter()
    start = luigi.IntParameter()
    batch = luigi.IntParameter()
    solr_query = luigi.Parameter()
    segment = segmentation.Segmentation()

    def run(self):
        client = MongoClient(util.mongo_host, util.mongo_port)

        try:
            jobs.update_job_status(str(self.job), util.conn_string, jobs.IN_PROGRESS, "Running TermFinder Batch %s" %
                                   self.batch)

            pipeline_config = config.get_pipeline_config(self.pipeline, util.conn_string)
            docs = solr_data.query(self.solr_query, rows=util.row_count, start=self.start, solr_url=util.solr_url,
                                   tags=pipeline_config.report_tags, mapper_inst=util.report_mapper_inst,
                                   mapper_url=util.report_mapper_url, mapper_key=util.report_mapper_key)
            term_matcher = TermFinder(pipeline_config.terms, pipeline_config.include_synonyms, pipeline_config
                                      .include_descendants, pipeline_config.include_ancestors)

            with self.output().open('w') as outfile:
                for doc in docs:
                    terms_found = term_matcher.get_term_full_text_matches(doc["report_text"])
                    for term in terms_found:
                        inserted = mongo_writer(client, self.pipeline, self.job, self.batch, pipeline_config, term, doc)
                        outfile.write(str(inserted))
                        outfile.write('\n')
        except Exception as ex:
            print(ex)
        finally:
            client.close()

    def output(self):
        return luigi.LocalTarget("%s/pipeline_job%s_term_finder_batch%s.txt" % (util.tmp_dir, str(self.job),
                                                                                str(self.start)))


class ProviderAssertionBatchTask(luigi.Task):
    pipeline = luigi.IntParameter()
    job = luigi.IntParameter()
    start = luigi.IntParameter()
    batch = luigi.IntParameter()
    solr_query = luigi.Parameter()
    segment = segmentation.Segmentation()
    client = MongoClient(util.mongo_host, util.mongo_port)

    def run(self):

        client = MongoClient(util.mongo_host, util.mongo_port)

        try:
            jobs.update_job_status(str(self.job), util.conn_string, jobs.IN_PROGRESS, "Running TermFinder Batch %s" %
                                   self.batch)

            pipeline_config = config.get_pipeline_config(self.pipeline, util.conn_string)
            docs = solr_data.query(self.solr_query, rows=util.row_count, start=self.start, solr_url=util.solr_url,
                                   tags=pipeline_config.report_tags, mapper_inst=util.report_mapper_inst,
                                   mapper_url=util.report_mapper_url, mapper_key=util.report_mapper_key)
            term_matcher = TermFinder(pipeline_config.terms, pipeline_config.include_synonyms, pipeline_config
                                      .include_descendants, pipeline_config.include_ancestors)

            with self.output().open('w') as outfile:
                for doc in docs:
                    terms_found = term_matcher.get_term_full_text_matches(doc["report_text"], provider_assertion_filters)
                    for term in terms_found:
                        inserted = mongo_writer(client, self.pipeline, self.job, self.batch, pipeline_config, term, doc)
                        outfile.write(str(inserted))
                        outfile.write('\n')
        except Exception as ex:
            print(ex)
        finally:
            client.close()

    def output(self):
        return luigi.LocalTarget("%s/pipeline_job%s_provider_assertion_batch%s.txt" % (util.tmp_dir, str(self.job),
                                                                                str(self.start)))
