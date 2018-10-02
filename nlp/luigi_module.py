from pymongo.errors import BulkWriteError
import luigi
import data_access
from luigi_tools import phenotype_helper
import copy
from tasks import *
from algorithms import get_related_terms
import sys
import traceback
import datetime
from data_access import pipeline_config as config
from data_access import solr_data


# TODO eventually move this to luigi_tools, but need to make sure successfully can be found in sys.path
# didn't seem like it was with initial efforts

class PhenotypeTask(luigi.Task):
    phenotype = luigi.IntParameter()
    job = luigi.IntParameter()
    owner = luigi.Parameter()
    client = MongoClient(util.mongo_host, util.mongo_port)

    def requires(self):
        register_tasks()
        tasks = list()
        pipeline_ids = data_access.query_pipeline_ids(int(self.phenotype), util.conn_string)
        print("getting ready to execute pipelines...")
        print(pipeline_ids)
        if len(pipeline_ids) > 0:
            for pipeline_id in pipeline_ids:
                pipeline_config = data_access.get_pipeline_config(pipeline_id, util.conn_string)
                tasks.append(PipelineTask(pipeline=pipeline_id, job=self.job, owner=self.owner,
                                          pipelinetype=pipeline_config.config_type))
        print(tasks)

        return tasks

    def run(self):
        print('dependencies done; run phenotype reconciliation')
        client = MongoClient(util.mongo_host, util.mongo_port)

        try:
            data_access.update_job_status(str(self.job), util.conn_string, data_access.IN_PROGRESS,
                                          "Finished Pipelines")

            phenotype = data_access.query_phenotype(int(self.phenotype), util.conn_string)
            print(phenotype)

            db = client[util.mongo_db]

            data_access.update_job_status(str(self.job), util.conn_string, data_access.IN_PROGRESS,
                                          "Filtering Results")

            with self.output().open('w') as outfile:
                phenotype_helper.write_phenotype_results(db, self.job, phenotype, self.phenotype, self.phenotype)
                data_access.update_job_status(str(self.job), util.conn_string, data_access.COMPLETED,
                                              "Job completed successfully")
                outfile.write("DONE!")
                outfile.write('\n')
        except BulkWriteError as bwe:
            print(bwe.details)
            data_access.update_job_status(str(self.job), util.conn_string, data_access.WARNING, str(bwe.details))
        except Exception as ex:
            traceback.print_exc(file=sys.stdout)
            data_access.update_job_status(str(self.job), util.conn_string, data_access.FAILURE, str(ex))
            print(ex)
        finally:
            client.close()

    def output(self):
        return luigi.LocalTarget("%s/phenotype_job%s_output.txt" % (util.tmp_dir, str(self.job)))


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
    solr_query = config.get_query(custom_query=pipeline_config.custom_query, terms=added)
    total_docs = solr_data.query_doc_size(solr_query, mapper_inst=util.report_mapper_inst,
                                          mapper_url=util.report_mapper_url,
                                          mapper_key=util.report_mapper_key, solr_url=util.solr_url,
                                          types=pipeline_config.report_types, filter_query=pipeline_config.filter_query,
                                          tags=pipeline_config.report_tags,
                                          report_type_query=pipeline_config.report_type_query,
                                          sources=pipeline_config.sources,
                                          cohort_ids=pipeline_config.cohort,
                                          job_results_filters=pipeline_config.job_results)
    doc_limit = config.get_limit(total_docs, pipeline_config)
    ranges = range(0, (doc_limit + util.row_count), util.row_count)
    jobs.update_job_status(str(job_id), util.conn_string, jobs.IN_PROGRESS, "Running batch tasks")

    return solr_query, total_docs, doc_limit, ranges


class PipelineTask(luigi.Task):
    pipeline = luigi.IntParameter()
    job = luigi.IntParameter()
    owner = luigi.Parameter()
    pipelinetype = luigi.Parameter()
    solr_query = '*:*'

    def requires(self):
        try:
            self.solr_query, total_docs, doc_limit, ranges = initialize_task_and_get_documents(self.pipeline, self.job, self
                                                                                          .owner)

            task = registered_pipelines[str(self.pipelinetype)]
            matches = [task(pipeline=self.pipeline, job=self.job, start=n, solr_query=self.solr_query, batch=n)
                       for n in ranges]

            return matches
        except Exception as ex:
            traceback.print_exc(file=sys.stderr)
            jobs.update_job_status(str(self.job), util.conn_string, jobs.WARNING, ''.join(traceback.format_stack()))
            print(ex)
        return list()

    def run(self):
        pipeline_config = data_access.get_pipeline_config(self.pipeline, util.conn_string)

        print('get collector')
        collector_name = str(self.pipelinetype)
        if collector_name in registered_collectors:
            collector_class = registered_collectors[collector_name]
            if collector_class:
                print('run collector')
                collector = collector_class()
                collector.run(self.pipeline, self.job, self.owner, self.pipelinetype, pipeline_config)
                collector.cleanup(self.pipeline, self.job, self.owner, self.pipelinetype, pipeline_config)

        jobs.update_job_status(str(self.job), util.conn_string, jobs.COMPLETED, "Finished %s Pipeline" % self
                               .pipelinetype)

    def complete(self):
        status = jobs.get_job_status(str(self.job), util.conn_string)
        return status['status'] == jobs.COMPLETED or status['status'] == jobs.WARNING


if __name__ == "__main__":
    owner = "tester"
    p_id = "10521"
    the_job_id = data_access.create_new_job(
        data_access.NlpJob(job_id=-1, name="Test Phenotype", description="Test Phenotype",
                           owner=owner, status=data_access.STARTED, date_ended=None,
                           phenotype_id=int(p_id), pipeline_id=-1, date_started=datetime.datetime.now(),
                           job_type='PHENOTYPE'), util.conn_string)
    luigi.run(['PhenotypeTask', '--phenotype', p_id, '--job', str(the_job_id), '--owner', 'tester'])
