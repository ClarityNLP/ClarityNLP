import copy
from tasks import *
try:
    from .nlp import get_related_terms
except Exception as e:
    print(e)
    from nlp import get_related_terms

luigi_pipeline_types = {
    "TermFinder": TermFinderBatchTask,
    "ProviderAssertion": ProviderAssertionBatchTask,
    "MeasurementFinder": MeasurementFinderTask,
    "ValueExtractor": ValueExtractorTask
}


def initialize_task_and_get_documents(pipeline_id, job_id, owner):
    jobs.update_job_status(str(job_id), util.conn_string, jobs.IN_PROGRESS,
                           "Initializing task -- pipeline: %s, job: %s, owner: %s" % (str(pipeline_id), str(job_id),
                                                                                      str(owner)))

    pipeline_config = config.get_pipeline_config(pipeline_id, util.conn_string)

    jobs.update_job_status(str(job_id), util.conn_string, jobs.IN_PROGRESS, "Getting related terms")
    added = copy.copy(pipeline_config.terms)

    for term in pipeline_config.terms:
        related_terms = get_related_terms(util.conn_string, term, pipeline_config.include_synonyms, pipeline_config
                                          .include_descendants, pipeline_config.include_ancestors, escape=False)
        if related_terms and len(related_terms) > 0:
            added.extend(related_terms)

    jobs.update_job_status(str(job_id), util.conn_string, jobs.IN_PROGRESS, "Getting Solr doc size")
    solr_query = config.get_query(added)
    total_docs = solr_data.query_doc_size(solr_query, mapper_inst=util.report_mapper_inst,
                                          mapper_url=util.report_mapper_url,
                                          mapper_key=util.report_mapper_key, solr_url=util.solr_url,
                                          tags=pipeline_config.report_tags, report_type_query=pipeline_config.report_type_query)
    doc_limit = config.get_limit(total_docs, pipeline_config)
    ranges = range(0, (doc_limit + util.row_count), util.row_count)
    jobs.update_job_status(str(job_id), util.conn_string, jobs.IN_PROGRESS, "Running batch tasks")

    return solr_query, total_docs, doc_limit, ranges


class PipelineTask(luigi.Task):
    pipeline = luigi.IntParameter()
    job = luigi.IntParameter()
    owner = luigi.Parameter()
    pipelinetype = luigi.Parameter()

    def requires(self):
        solr_query, total_docs, doc_limit, ranges = initialize_task_and_get_documents(self.pipeline, self.job, self
                                                                                      .owner)
        task = luigi_pipeline_types[str(self.pipelinetype)]
        matches = [task(pipeline=self.pipeline, job=self.job, start=n, solr_query=solr_query, batch=n)
                   for n in ranges]

        return matches

    def run(self):
        jobs.update_job_status(str(self.job), util.conn_string, jobs.COMPLETED, "Finished %s Pipeline" % self
                               .pipelinetype)

    def complete(self):
        status = jobs.get_job_status(str(self.job), util.conn_string)
        return status['status'] == jobs.COMPLETED


def run_ner_pipeline(pipeline_id, job_id, owner):
    luigi.run(['PipelineTask', '--pipeline', pipeline_id, '--job', str(job_id), '--owner', owner, '--pipelinetype',
               'TermFinder'])


def run_provider_assertion_pipeline(pipeline_id, job_id, owner):
    luigi.run(['PipelineTask', '--pipeline', pipeline_id, '--job', str(job_id), '--owner', owner, '--pipelinetype',
               'ProviderAssertion'])


def run_value_extraction_pipeline(pipeline_id, job_id, owner):
    luigi.run(['PipelineTask', '--pipeline', pipeline_id, '--job', str(job_id), '--owner', owner, '--pipelinetype',
               'ValueExtractor'])


if __name__ == "__main__":
    run_value_extraction_pipeline(str(223), str(222), 'test')
