import copy
import datetime

#import luigi
from pymongo.errors import BulkWriteError

import data_access
from ilock import ILock, ILockException
from data_access import pipeline_config as config
from data_access import solr_data, filesystem_data, memory_data, phenotype_stats
from data_access import update_phenotype_model
from data_access import tuple_processor
from luigi_tools import phenotype_helper
from tasks import *
from claritynlp_logging import log, ERROR, DEBUG

import util
import threading
import multiprocessing
from queue import Queue, Empty


# get the number of CPU cores and use it to constrain the number of worker threads
_cpu_count = multiprocessing.cpu_count()

# user-specified number of workers
_luigi_workers = int(util.luigi_workers)

if _luigi_workers > 0 and _luigi_workers <= _cpu_count:
    # user specified a valid number of worker threads
    _worker_count = _luigi_workers
else:
    if _cpu_count > 4:
        _worker_count = _cpu_count // 2
    elif _cpu_count == 1:
        _worker_count = 1
    else:
        _worker_count = _cpu_count - 1

# special token for terminating worker threads
_TERMINATE_WORKERS = None

log('luigi_module: {0} CPUs, {1} workers'.format(_cpu_count, _worker_count))

# function for parallel execution of the PipelineTask objects of each PhenotypeTask
def _worker(queue, worker_id):
    """
    Continually check the queue for work items; terminate if None appears.
    Work items must implement a run() function.
    """
    
    log('luigi_module: worker {0} running...'.format(worker_id))
    while True:
        try:
            item = queue.get(timeout = 2)
        except Empty:
            # haven't seen the termination signal yet
            continue
        if item is _TERMINATE_WORKERS:
            # replace so that other workers will know to terminate
            queue.put(item)
            # now exit this worker thread
            break
        else:
            # run it
            log('luigi_module: worker {0} now running {1}'.format(worker_id, item))
            # run pipeline batch tasks
            item.run()
            # run collector
            item.run_collector_pipeline()
    log('luigi_module: worker {0} exiting...'.format(worker_id))


# These variables are used to control locking of the Mongo database,
# to force writes to disk.

# name of the shared lock, visible from different ClarityNLP processes
_LOCK_NAME = 'ClarityNLP_Mongo_Lock'

# wait as long as this many seconds to acquire the lock
_LOCK_WAIT_SECS = 10.0

# each ClarityNLP process will make this many attempts to acquire the lock
_MAX_ATTEMPTS = 10


class PhenotypeTask(): #luigi.Task):
    worker_timeout = 60 * 60 * 4
    #phenotype = luigi.IntParameter()
    #job = luigi.IntParameter()
    #owner = luigi.Parameter()

    #def requires(self):
    def __init__(self, job, phenotype, owner):
        self.job = job
        self.phenotype = phenotype
        self.owner = owner
        self.pipeline_tasks = list()
        self.pipelines_finished = False
        
        register_tasks()
        pipeline_ids = data_access.query_pipeline_ids(int(self.phenotype), util.conn_string)
        phenotype_config = data_access.query_phenotype(int(self.phenotype), util.conn_string)
        phenotype_config['phenotype_id'] = int(self.phenotype)

        log("getting ready to execute pipelines...")
        log('pipeline_ids: {0}'.format(pipeline_ids))
        if len(pipeline_ids) > 0:
            configs = dict()
            for pipeline_id in pipeline_ids:
                pipeline_config = data_access.get_pipeline_config(pipeline_id, util.conn_string)
                pipeline_config['pipeline_id'] = pipeline_id
                configs[pipeline_config['name']] = pipeline_config

            update_phenotype_model(phenotype_config, util.conn_string)
            for pipeline_config in configs.values():
                pipeline_id = pipeline_config['pipeline_id']
                pipeline_task_obj = PipelineTask(pipeline=pipeline_id, job=self.job, owner=self.owner,
                                                 pipelinetype=pipeline_config.config_type)
                # save tasks on a list for later execution
                self.pipeline_tasks.append(pipeline_task_obj)

        log('task list: {0}'.format(self.pipeline_tasks))

    def run_pipelines_in_parallel(self):
        """
        Parallel execution of the PipelineTask objects in self.pipeline_tasks.
        """

        task_queue = Queue()
        
        # create and start the worker threads
        log('luigi_module: creating {0} worker threads'.format(_worker_count))        
        workers = [threading.Thread(target=_worker, args=(task_queue, i)) for i in range(_worker_count)]
        for worker in workers:
            worker.start()
        
        for task in self.pipeline_tasks:
            task_queue.put(task)

        # terminate each worker after its PipelineTask object has completed execution
        task_queue.put(_TERMINATE_WORKERS)
        for worker in workers:
            worker.join()

        self.pipelines_finished = True
        
        
    #def run(self):
    def run_reconciliation(self):

        # all pipeline tasks must have finished prior to this
        assert self.pipelines_finished

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

            with open(self.output(), 'w') as outfile:
                phenotype_helper.write_phenotype_results(db, self.job, phenotype, self.phenotype, self.phenotype)

                # do tuple processing now that all tasks have completed
                succeeded = tuple_processor.process_tuples(db['phenotype_results'], int(self.job))
                if not succeeded:
                    log('*** ERROR: tuple processing failed ***')

                # force all mongo writes to complete by calling fsync on the admin db, then releasing the lock

                wrote_docs = False
                for tries in range(1, _MAX_ATTEMPTS):

                    try:
                        with ILock(_LOCK_NAME, timeout=_LOCK_WAIT_SECS):

                            # only a SINGLE ClarityNLP process can execute this code at any time
                            
                            # force writes to disk by locking the Mongo admin database
                            log('*** Job {0}: FORCING MONGO WRITES ***'.format(self.job))
                        
                            admin_db = client['admin']
                            fsync_result = admin_db.command('fsync', lock=True)
                            assert 1 == fsync_result['lockCount']
                            unlock_result = admin_db.command('fsyncUnlock')
                            assert 0 == unlock_result['lockCount']
                            
                            log('*** Job {0}: ALL MONGO WRITES COMPLETED ***'.format(self.job))

                            wrote_docs = True

                    except ILockException:
                        # timed out before acquiring the lock, will try again
                        pass

                    if wrote_docs:
                        break

                if not wrote_docs:
                    log('Job {0} failed to lock the Mongo admin database.'.format(self.job))
                        
                data_access.update_job_status(str(self.job), util.conn_string, data_access.COMPLETED,
                                          "Job completed successfully")

                # the solr "url" determines where to find the documents
                if memory_data.IN_MEMORY_DATA == util.solr_url:
                    memory_data._clear_buffer(self.job)
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
        #output_file = "%s/phenotype_job%s_output.txt" % (util.tmp_dir, str(self.job))
        output_file = '{0}/phenotype_job{1}_output.txt'.format(util.tmp_dir, str(self.job))
        return output_file
        #return luigi.LocalTarget("%s/phenotype_job%s_output.txt" % (util.tmp_dir, str(self.job)))


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

    # the solr "url" determines where to find the documents
    if util.solr_url.startswith('http'):
        data_store = solr_data
    elif memory_data.IN_MEMORY_DATA == util.solr_url:
        data_store = memory_data
        if not pipeline_config.report_source and len(pipeline_config.report_source) == 0:
            pipeline_config.report_source = str(job_id)
        pipeline_config.sources = [pipeline_config.report_source]
    else:
        data_store = filesystem_data

    #print('sources {}'.format(pipeline_config.sources))

    total_docs = data_store.query_doc_size(solr_query,
                                           mapper_inst=util.report_mapper_inst,
                                           mapper_url=util.report_mapper_url,
                                           mapper_key=util.report_mapper_key,
                                           solr_url=util.solr_url,
                                           types=pipeline_config.report_types,
                                           filter_query=pipeline_config.filter_query,
                                           tags=pipeline_config.report_tags,
                                           report_type_query=pipeline_config.report_type_query,
                                           sources=pipeline_config.sources,
                                           cohort_ids=pipeline_config.cohort,
                                           job_results_filters=pipeline_config.job_results)
        
    #log('*** luigi_module: query_doc_size returned {0} docs, pipeline_id {1}, job_id {2} ***'.
    #    format(total_docs, pipeline_id, job_id))
        
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

    collector_name = str(pipelinetype)
    log('get collector: {0}'.format(collector_name))    
    if collector_name in registered_collectors:
        collector_class = registered_collectors[collector_name]
        if collector_class:
            log('run collector')
            collector = collector_class()
            collector.run(pipeline, job, owner, pipelinetype, pipeline_config)
            collector.cleanup(pipeline, job, owner, pipelinetype, pipeline_config)

    jobs.update_job_status(str(job), util.conn_string, jobs.COMPLETED, "Finished %s Pipeline" % pipelinetype)


class PipelineTask(): #luigi.Task):
    worker_timeout = 60 * 60 * 4
    # pipeline = luigi.IntParameter()
    # job = luigi.IntParameter()
    # owner = luigi.Parameter()
    # pipelinetype = luigi.Parameter()
    # solr_query = '*:*'

    #def requires(self):
    def __init__(self, job, pipeline, owner, pipelinetype, solr_query='*:*'):
        self.job = job
        self.pipeline = pipeline
        self.owner = owner
        self.pipelinetype = pipelinetype
        self.solr_query = solr_query

        # list of pipeline tasks, one for each document batch
        self.batch_task_list = []

        self.batches_finished = False

    #def run_batch_tasks(self):
    def run(self):

        self.batch_task_list = []
        self.batches_finished = False
        
        try:
            self.solr_query, total_docs, doc_limit, ranges = initialize_task_and_get_documents(self.pipeline, self.job,
                                                                                               self
                                                                                               .owner)
            task = registered_pipelines[str(self.pipelinetype)]

            # construct task list, each of which will process a unique batch of documents
            if task.parallel_task:
                self.batch_task_list = [task(pipeline=self.pipeline,
                                             job=self.job,
                                             start=n,
                                             solr_query=self.solr_query,
                                             batch=n) for n in ranges]
            else:
                self.batch_task_list = [task(pipeline=self.pipeline,
                                             job=self.job,
                                             start=0,
                                             solr_query=self.solr_query,
                                             batch=0)]
            if len(self.batch_task_list) > 0:
                log('task_obj type: {0}'.format(type(self.batch_task_list[0])))

        except Exception as ex:
            traceback.print_exc(file=sys.stderr)
            jobs.update_job_status(str(self.job), util.conn_string, jobs.WARNING, ''.join(traceback.format_stack()))
            log(ex)

        # all batches for this pipeline task run serially
        for task in self.batch_task_list:
            task.run()

        self.batches_finished = True

    #def run(self):
    def run_collector_pipeline(self):
        # all batches for this PipelineTask must have run to completion
        assert self.batches_finished
        
        log('running collector pipeline')
        run_pipeline(self.pipeline, self.pipelinetype, self.job, self.owner)
        return self.complete()

    def complete(self):
        status = jobs.get_job_status(str(self.job), util.conn_string)
        return status['status'] == jobs.COMPLETED or status['status'] == jobs.WARNING or status[
            'status'] == jobs.FAILURE


# if __name__ == "__main__":
#     owner = "tester"
#     p_id = "11469"
#     the_job_id = data_access.create_new_job(
#         data_access.NlpJob(job_id=-1, name="Test Phenotype", description="Test Phenotype",
#                            owner=owner, status=data_access.STARTED, date_ended=None,
#                            phenotype_id=int(p_id), pipeline_id=-1, date_started=datetime.datetime.now(),
#                            job_type='PHENOTYPE'), util.conn_string)
#     luigi.run(['PhenotypeTask', '--phenotype', p_id, '--job', str(the_job_id), '--owner', 'tester'])
