import copy
from tasks import *
try:
    from .nlp import get_related_terms
except Exception as e:
    print(e)
    from nlp import get_related_terms


class TermFinderPipeline(luigi.Task):
    pipeline = luigi.IntParameter()
    job = luigi.IntParameter()
    owner = luigi.Parameter()

    def requires(self):

        pipeline_config = config.get_pipeline_config(self.pipeline, util.conn_string)
        added = copy.copy(pipeline_config.terms)
        for term in pipeline_config.terms:
            related_terms = get_related_terms(util.conn_string, term, pipeline_config.include_synonyms, pipeline_config
                                              .include_descendants, pipeline_config.include_ancestors, escape=False)
            if related_terms and len(related_terms) > 0:
                added.extend(related_terms)
        solr_query = config.get_query(added)
        total_docs = solr_data.query_doc_size(solr_query, mapper_inst=util.report_mapper_inst,
                                              mapper_url=util.report_mapper_url,
                                              mapper_key=util.report_mapper_key, solr_url=util.solr_url,
                                              tags=pipeline_config.report_tags)
        doc_limit = config.get_limit(total_docs, pipeline_config)
        ranges = range(0, (doc_limit + util.row_count), util.row_count)
        matches = [TermFinderBatchTask(pipeline=self.pipeline, job=self.job, start=n, solr_query=solr_query, batch=n) for n in
                   ranges]

        return matches

    def run(self):
        jobs.update_job_status(str(self.job), util.conn_string, jobs.COMPLETED, "Finished TermFinder Pipeline")

# @luigi.Task.event_handler(luigi.Event.FAILURE)
# def mourn_failure(self, exception):
#     """
#     Report failure event
#     Uses "-!--!--!--!--!--!--!--!--!--!-"  as indicator
#     """
#
#     print(26 * '-!-')
#     print("Boo!, {c} failed.  :(".format(c=self.__class__.__name__))
#     print(".. with this exception: '{e}'".format(e=str(exception)))
#     print(26 * '-!-')


class ProviderAssertionPipeline(luigi.Task):
    pipeline = luigi.IntParameter()
    job = luigi.IntParameter()
    owner = luigi.Parameter()

    def requires(self):

        pipeline_config = config.get_pipeline_config(self.pipeline, util.conn_string)
        added = copy.copy(pipeline_config.terms)
        for term in pipeline_config.terms:
            related_terms = get_related_terms(util.conn_string, term, pipeline_config.include_synonyms,
                                              pipeline_config
                                              .include_descendants, pipeline_config.include_ancestors,
                                              escape=False)
            if related_terms and len(related_terms) > 0:
                added.extend(related_terms)
        solr_query = config.get_query(added)
        total_docs = solr_data.query_doc_size(solr_query, mapper_inst=util.report_mapper_inst,
                                              mapper_url=util.report_mapper_url,
                                              mapper_key=util.report_mapper_key, solr_url=util.solr_url,
                                              tags=pipeline_config.report_tags)
        doc_limit = config.get_limit(total_docs, pipeline_config)
        ranges = range(0, (doc_limit + util.row_count), util.row_count)
        matches = [
            ProviderAssertionBatchTask(pipeline=self.pipeline, job=self.job, start=n, solr_query=solr_query, batch=n)
            for n in
            ranges]

        return matches

    def run(self):
        jobs.update_job_status(str(self.job), util.conn_string, jobs.COMPLETED, "Finished ProviderAssertion Pipeline")


def run_ner_pipeline(pipeline_id, job_id, owner):
    luigi.run(['TermFinderPipeline', '--pipeline', pipeline_id, '--job', str(job_id), '--owner', owner])


def run_provider_assertion_pipeline(pipeline_id, job_id, owner):
    luigi.run(['ProviderAssertionPipeline', '--pipeline', pipeline_id, '--job', str(job_id), '--owner', owner])


if __name__ == "__main__":
    run_provider_assertion_pipeline(str(116), str(1), 'test')
