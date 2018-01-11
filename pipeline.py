import luigi
from luigi.contrib import mongodb as luigi_mongo
from data_access import solr_data
from data_access import pipeline_config as config
from pymongo import MongoClient
from nlp import segmentation
import util

row_count = 500
client = MongoClient(util.mongo_host, util.mongo_port)

# TODO get scheduler type and additonal config


class CleanDocsToSentences(luigi.Task):
    pipeline = luigi.IntParameter()
    job = luigi.IntParameter()
    start = luigi.IntParameter()
    solr_query = luigi.Parameter()

    def run(self):
        docs = solr_data.query(self.solr_query, rows=row_count, start=self.start, solr_url=util.solr_url)

        with self.output().open('w') as outfile:
            for doc in docs:
                sentences = segmentation.parse_sentences(doc["report_text"])
                for sentence in sentences:
                    outfile.write(sentence)

    def output(self):
        return luigi.LocalTarget("%s/pipeline_job%s_batch%s.txt" % (util.tmp_dir, str(self.job), str(self.start)))


class NERPipeline(luigi.Task):
    pipeline = luigi.IntParameter()
    job = luigi.IntParameter()
    owner = luigi.Parameter()

    def requires(self):
        pipeline_config = config.get_pipeline_config(self.pipeline, util.conn_string)
        solr_query = config.get_query(pipeline_config)
        total_docs = solr_data.query_doc_size(solr_query, solr_url=util.solr_url)
        doc_limit = config.get_limit(total_docs, pipeline_config)
        ranges = range(0, (doc_limit + row_count), row_count)
        return [CleanDocsToSentences(pipeline=self.pipeline, job=self.job, start=n, solr_query=solr_query)
               for n in ranges]

    def run(self):
        for t in self.input():
            print(t)


def run_ner_pipeline(pipeline_id: str, job_id: int, owner: str):
    luigi.run(['NERPipeline', '--pipeline', pipeline_id, '--job', str(job_id), '--owner', owner, '--local-scheduler'])


if __name__ == "__main__":
    luigi.run(['NERPipeline', '--pipeline', '1', '--job', '1234', '--owner', 'user', '--local-scheduler'])
