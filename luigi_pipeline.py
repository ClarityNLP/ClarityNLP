import luigi
from data_access import solr_data
from data_access import pipeline_config as config
from data_access import jobs
import util
from tasks import TermFinderBatchTask


class TermFinderPipeline(luigi.Task):
    pipeline = luigi.IntParameter()
    job = luigi.IntParameter()
    owner = luigi.Parameter()

    def requires(self):
        pipeline_config = config.get_pipeline_config(self.pipeline, util.conn_string)
        solr_query = config.get_query(pipeline_config)
        total_docs = solr_data.query_doc_size(solr_query, solr_url=util.solr_url)
        doc_limit = config.get_limit(total_docs, pipeline_config)
        ranges = range(0, (doc_limit + util.row_count), util.row_count)
        matches = [TermFinderBatchTask(pipeline=self.pipeline, job=self.job, start=n, solr_query=solr_query, batch=n) for n in
                   ranges]

        return matches

    def run(self):
        jobs.update_job_status(str(self.job), util.conn_string, jobs.COMPLETED, "Finished TermFinder Pipeline")


def run_ner_pipeline(pipeline_id, job_id, owner):
    luigi.run(['TermFinderPipeline', '--pipeline', pipeline_id, '--job', str(job_id), '--owner', owner])


if __name__ == "__main__":
    run_ner_pipeline(str(1), str(1), 'test')
