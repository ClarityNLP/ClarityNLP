from subprocess import call

from luigi import worker, rpc
import requests
import time
import threading

from data_access import *
from luigi_tools.phenotype_helper import *
from claritynlp_logging import log, ERROR
from luigi_module import PhenotypeTask
import luigi


scheduler = rpc.RemoteScheduler(url=util.luigi_scheduler)


def get_active_workers():
    url = util.luigi_scheduler + "/api/task_list?data={%22status%22:%22RUNNING%22}"
    log(url)
    req = requests.get(url)
    if req.status_code == 200:
        json_res = req.json()
        keys = (json_res['response'].keys())
        return len(keys)

    return 0


def run_pipeline(pipeline_type: str, pipeline_id: str, job_id: int, owner: str):
    log("PLEASE RUN PIPELINE THROUGH PHENOTYPES", ERROR)
    # active = get_active_workers()
    # total = int(util.luigi_workers)
    # while active >= total:
    #     time.sleep(10)
    #     active = get_active_workers()
    #
    # luigi_log = (util.log_dir + '/luigi_%s.log') % (str(job_id))
    #
    # scheduler_ = util.luigi_scheduler
    # log("running job %s on pipeline %s; logging here %s" % (str(job_id), str(pipeline_id), luigi_log))
    # func = "PYTHONPATH='.' luigi --workers %s --module luigi_module %s  --pipeline %s --job %s --owner %s " \
    #        "--pipelinetype %s --scheduler-url %s > %s 2>&1 &" % (str(util.luigi_workers), "PipelineTask", pipeline_id,
    #                                                              str(job_id), owner, pipeline_type, scheduler_,
    #                                                              luigi_log)
    # try:
    #     call(func, shell=True)
    # except Exception as ex:
    #     log(ex, file=sys.stderr)
    #     log("unable to execute %s" % func, file=sys.stderr)


def run_task(task):
    worker_num = int(util.luigi_workers)
    # multiprocess = worker_num > 1

    w = worker.Worker(scheduler=scheduler, no_install_shutdown_handler=True, worker_processes=worker_num)
    w.add(task, multiprocess=True, processes=2)
    w.run()


def threaded_func(arg0, arg1, arg2):
    time.sleep(2)
    active = get_active_workers() * 3
    log("{}=MAX LUIGI WORKERS".format(util.luigi_workers))
    num_workers = int(util.luigi_workers)
    n = 0
    if active > num_workers:
        while active > num_workers and n < 30:
            log("{}=ACTIVE LUIGI WORKERS; SLEEPING..".format(active))
            time.sleep(5)
            active = get_active_workers()
            n += 1

    log("running job %s on phenotype %s" % (str(arg0), str(arg2)))
    task = PhenotypeTask(job=arg0, owner=arg1, phenotype=arg2)
    run_task(task)


def threaded_phenotype_task(job_id, owner, phenotype_id):
    thread = threading.Thread(target=threaded_func, args=(job_id, owner, phenotype_id))
    thread.start()


def run_phenotype_job(phenotype_id: str, job_id: str, owner: str):
    # active = get_active_workers()

    # luigi_log = (util.log_dir + '/luigi_%s.log') % (str(job_id))

    # scheduler = util.luigi_scheduler
    # log("running job %s on phenotype %s; logging here %s" % (str(job_id), str(phenotype_id), luigi_log))
    # func = "PYTHONPATH='.' luigi --workers %s --module luigi_module %s --phenotype %s --job %s --owner %s" \
    #        " --scheduler-url %s > %s 2>&1 &" % (str(util.luigi_workers), "PhenotypeTask", phenotype_id, str(job_id),
    #                                                owner, scheduler, luigi_log)
    try:
        # if environ.get("USE_GUNICORN", "false") == "true":
        #     # call(func, shell=True)
        #     luigi.build([PhenotypeTask(job=job_id, owner=owner, phenotype=str(phenotype_id))],
        #                  workers=str(util.luigi_workers), scheduler_url=scheduler)
        # else:
        #     call(func, shell=True)

        threaded_phenotype_task(job_id, owner, phenotype_id)
    except Exception as ex:
        log(ex, file=sys.stderr, level=ERROR)
        log("unable to execute python task", file=sys.stderr, level=ERROR)


def run_phenotype(phenotype_model: PhenotypeModel, phenotype_id: str, job_id: int, background=True):
    pipelines = get_pipelines_from_phenotype(phenotype_model)
    pipeline_ids = []
    if pipelines and len(pipelines) > 0:
        for pipeline in pipelines:
            pipeline_id = insert_pipeline_config(pipeline, util.conn_string)
            insert_phenotype_mapping(phenotype_id, pipeline_id, util.conn_string)
            pipeline_ids.append(pipeline_id)

        run_phenotype_job(phenotype_id, str(job_id), phenotype_model.owner)
    return pipeline_ids


def run_ner_pipeline(pipeline_id, job_id, owner):
    # luigi.run(['PipelineTask', '--pipeline', pipeline_id, '--job', str(job_id), '--owner', owner, '--pipelinetype',
    #            'TermFinder'])
    log("PLEASE RUN PIPELINE THROUGH PHENOTYPES", ERROR)


def run_provider_assertion_pipeline(pipeline_id, job_id, owner):
    # luigi.run(['PipelineTask', '--pipeline', pipeline_id, '--job', str(job_id), '--owner', owner, '--pipelinetype',
    #            'ProviderAssertion'])
    log("PLEASE RUN PIPELINE THROUGH PHENOTYPES", ERROR)


def run_value_extraction_pipeline(pipeline_id, job_id, owner):
    # luigi.run(['PipelineTask', '--pipeline', pipeline_id, '--job', str(job_id), '--owner', owner, '--pipelinetype',
    #            'ValueExtractor'])
    log("PLEASE RUN PIPELINE THROUGH PHENOTYPES", ERROR)


if __name__ == "__main__":
    log("luigi running", DEBUG)
    # test_model = get_sample_phenotype()
    # test_model.debug = True
    # p_id = insert_phenotype_model(test_model, util.conn_string)
    # the_job_id = jobs.create_new_job(jobs.NlpJob(job_id=-1, name="Test Phenotype", description=test_model.description,
    #                                              owner=test_model.owner, status=jobs.STARTED, date_ended=None,
    #                                              phenotype_id=p_id, pipeline_id=-1,
    #                                              date_started=datetime.datetime.now(),
    #                                              job_type='PHENOTYPE'), util.conn_string)
    #
    # run_phenotype(test_model, p_id, the_job_id)
