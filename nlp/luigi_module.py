import copy
import datetime

import luigi
from pymongo.errors import BulkWriteError

import data_access
from data_access import pipeline_config as config
from data_access import solr_data, phenotype_stats
from data_access import update_phenotype_model
from luigi_tools import phenotype_helper
from tasks import *
from claritynlp_logging import log, ERROR, DEBUG

# TODO eventually move this to luigi_tools, but need to make sure successfully can be found in sys.path
# didn't seem like it was with initial efforts


class PhenotypeTask(luigi.Task):
    phenotype = luigi.IntParameter()
    job = luigi.IntParameter()
    owner = luigi.Parameter()

    def requires(self):
        register_tasks()
        tasks = list()
        pipeline_ids = data_access.query_pipeline_ids(int(self.phenotype), util.conn_string)
        phenotype_config = data_access.query_phenotype(int(self.phenotype), util.conn_string)
        phenotype_config['phenotype_id'] = int(self.phenotype)

        log("getting ready to execute pipelines...")
        log(pipeline_ids)
        if len(pipeline_ids) > 0:
            configs = dict()
            for pipeline_id in pipeline_ids:
                pipeline_config = data_access.get_pipeline_config(pipeline_id, util.conn_string)
                pipeline_config['pipeline_id'] = pipeline_id
                configs[pipeline_config['name']] = pipeline_config

            update_phenotype_model(phenotype_config, util.conn_string)
            for pipeline_config in configs.values():
                pipeline_id = pipeline_config['pipeline_id']
                tasks.append(PipelineTask(pipeline=pipeline_id, job=self.job, owner=self.owner,
                                          pipelinetype=pipeline_config.config_type))
        log(tasks)

        return tasks

    def run(self):
        log('dependencies done; run phenotype reconciliation')
        client = util.mongo_client()

        try:
            data_access.update_job_status(str(self.job), util.conn_string, data_access.IN_PROGRESS,
                                          "Finished Pipelines")

            phenotype = data_access.query_phenotype(int(self.phenotype), util.conn_string)
            # log(phenotype)

            db = client[util.mongo_db]

            data_access.update_job_status(str(self.job), util.conn_string, data_access.IN_PROGRESS,
                                          "Filtering Results")

            stats = phenotype_stats(str(self.job), True)
            intermediate_stats = phenotype_stats(str(self.job), False)
            data_access.update_job_status(str(self.job), util.conn_string, data_access.STATS + "_INTERMEDIATE_RESULTS",
                                          str(intermediate_stats["results"]))
            data_access.update_job_status(str(self.job), util.conn_string, data_access.STATS + "_INTERMEDIATE_SUBJECTS",
                                          str(intermediate_stats["subjects"]))
            data_access.update_job_status(str(self.job), util.conn_string, data_access.STATS + "_FINAL_RESULTS",
                                          str(stats["results"]))
            data_access.update_job_status(str(self.job), util.conn_string, data_access.STATS + "_FINAL_SUBJECTS",
                                          str(stats["subjects"]))
            log("writing job stats....")
            log(json.dumps(stats, indent=4))
            # data_access.update_job_status(str(self.job), util.conn_string, data_access.STATS + "_CACHE_QUERY_COUNTS",
            #                               str(util.get_cache_query_count()))
            # data_access.update_job_status(str(self.job), util.conn_string,data_access.STATS + "_CACHE_COMPUTE_COUNTS",
            #                               str(util.get_cache_compute_count()))
            # data_access.update_job_status(str(self.job), util.conn_string, data_access.STATS + "_CACHE_HIT_RATIO",
            #                               str(util.get_cache_hit_ratio()))

            for k in util.properties.keys():
                data_access.update_job_status(str(self.job), util.conn_string, data_access.PROPERTIES + "_" + k,
                                              util.properties[k])
            with self.output().open('w') as outfile:
                phenotype_helper.write_phenotype_results(db, self.job, phenotype, self.phenotype, self.phenotype)
                data_access.update_job_status(str(self.job), util.conn_string, data_access.COMPLETED,
                                              "Job completed successfully")
                outfile.write("DONE!")
                outfile.write('\n')
            log("job {} done!".format(self.job))
        except BulkWriteError as bwe:
            log(bwe.details)
            data_access.update_job_status(str(self.job), util.conn_string, data_access.WARNING, str(bwe.details))
        except Exception as ex:
            traceback.print_exc(file=sys.stdout)
            data_access.update_job_status(str(self.job), util.conn_string, data_access.FAILURE, str(ex))
            log(ex)
        finally:
            client.close()

    def output(self):
        return luigi.LocalTarget("%s/phenotype_job%s_output.txt" % (util.tmp_dir, str(self.job)))


def initialize_task_and_get_documents(pipeline_id, job_id, owner):
    jobs.update_job_status(str(job_id), util.conn_string, jobs.IN_PROGRESS,
                           "Initializing task -- pipeline: %s, job: %s, owner: %s" % (str(pipeline_id), str(job_id),
                                                                                      str(owner)))

    pipeline_config = config.get_pipeline_config(pipeline_id, util.conn_string)
    added = copy.copy(pipeline_config.terms)

    for term in pipeline_config.terms:
        related_terms = get_related_terms(util.conn_string, term, pipeline_config.include_synonyms, pipeline_config
                                          .include_descendants, pipeline_config.include_ancestors, escape=False)
        if related_terms and len(related_terms) > 0:
            added.extend(related_terms)

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
    jobs.update_job_status(str(job_id), util.conn_string, jobs.STATS + "_PIPELINE_" + str(pipeline_id) + "_SOLR_DOCS",
                           str(total_docs))
    doc_limit = config.get_limit(total_docs, pipeline_config)
    jobs.update_job_status(str(job_id), util.conn_string, jobs.STATS + "_PIPELINE_" + str(pipeline_id) +
                           "_DOCUMENT_LIMIT",
                           str(doc_limit))
    jobs.update_job_status(str(job_id), util.conn_string, jobs.STATS + "_PIPELINE_" + str(pipeline_id) +
                           "_EVALUATED_DOCS",
                           str(min(doc_limit, total_docs)))
    ranges = range(0, (doc_limit + int(util.row_count)), int(util.row_count))

    return solr_query, total_docs, doc_limit, ranges


def run_pipeline(pipeline, pipelinetype, job, owner):
    pipeline_config = data_access.get_pipeline_config(pipeline, util.conn_string)

    log('get collector')
    collector_name = str(pipelinetype)
    if collector_name in registered_collectors:
        collector_class = registered_collectors[collector_name]
        if collector_class:
            log('run collector')
            collector = collector_class()
            collector.run(pipeline, job, owner, pipelinetype, pipeline_config)
            collector.cleanup(pipeline, job, owner, pipelinetype, pipeline_config)

    jobs.update_job_status(str(job), util.conn_string, jobs.COMPLETED, "Finished %s Pipeline" % pipelinetype)


class PipelineTask(luigi.Task):
    pipeline = luigi.IntParameter()
    job = luigi.IntParameter()
    owner = luigi.Parameter()
    pipelinetype = luigi.Parameter()
    solr_query = '*:*'

    def requires(self):
        try:
            self.solr_query, total_docs, doc_limit, ranges = initialize_task_and_get_documents(self.pipeline, self.job,
                                                                                               self
                                                                                               .owner)

            task = registered_pipelines[str(self.pipelinetype)]
            if task.parallel_task:
                matches = [task(pipeline=self.pipeline, job=self.job, start=n, solr_query=self.solr_query, batch=n)
                           for n in ranges]
            else:
                matches = [task(pipeline=self.pipeline, job=self.job, start=0, solr_query=self.solr_query, batch=0)]

            return matches
        except Exception as ex:
            traceback.print_exc(file=sys.stderr)
            jobs.update_job_status(str(self.job), util.conn_string, jobs.WARNING, ''.join(traceback.format_stack()))
            log(ex)
        return list()

    def run(self):
        run_pipeline(self.pipeline, self.pipelinetype, self.job, self.owner)

    def complete(self):
        status = jobs.get_job_status(str(self.job), util.conn_string)
        return status['status'] == jobs.COMPLETED or status['status'] == jobs.WARNING or status[
            'status'] == jobs.FAILURE


if __name__ == "__main__":
    owner = "tester"
    p_id = "11469"
    the_job_id = data_access.create_new_job(
        data_access.NlpJob(job_id=-1, name="Test Phenotype", description="Test Phenotype",
                           owner=owner, status=data_access.STARTED, date_ended=None,
                           phenotype_id=int(p_id), pipeline_id=-1, date_started=datetime.datetime.now(),
                           job_type='PHENOTYPE'), util.conn_string)
    luigi.run(['PhenotypeTask', '--phenotype', p_id, '--job', str(the_job_id), '--owner', 'tester'])
