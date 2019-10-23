from subprocess import call, STDOUT

import luigi
import requests
import time

from data_access import *
from luigi_tools.phenotype_helper import *
from queue import Queue


# q = Queue()


def get_active_workers():
    url = util.luigi_scheduler + "/api/task_list?data={%22status%22:%22RUNNING%22}"
    print(url)
    req = requests.get(url)
    if req.status_code == 200:
        json_res = req.json()
        keys = (json_res['response'].keys())
        return len(keys)

    return 0

from subprocess import call, STDOUT

import luigi
import requests
import time

from data_access import *
from luigi_tools.phenotype_helper import *
from queue import Queue


# q = Queue()


def get_active_workers():
    url = util.luigi_scheduler + "/api/task_list?data={%22status%22:%22RUNNING%22}"
    print(url)
    req = requests.get(url)
    if req.status_code == 200:
        json_res = req.json()
        keys = (json_res['response'].keys())
        return len(keys)

    return 0


def run_pipeline(pipeline_type: str, pipeline_id: str, job_id: int, owner: str, background=True):
    active = get_active_workers()
    total = int(util.luigi_workers)
    while active >= total:
        time.sleep(10)
        active = get_active_workers()

    luigi_log = (util.log_dir + '/luigi_%s.log') % (str(job_id))

    scheduler = util.luigi_scheduler
    print("running job %s on pipeline %s; logging here %s" % (str(job_id), str(pipeline_id), luigi_log))
    func = "PYTHONPATH='.' luigi --workers %s --module luigi_module %s  --pipeline %s --job %s --owner %s " \
           "--pipelinetype %s --scheduler-url %s > %s 2>&1 &" % (str(util.luigi_workers), "PipelineTask", pipeline_id,
                                                                 str(job_id), owner, pipeline_type, scheduler,
                                                                 luigi_log)
    try:
        # q.put(func)
        # call(func, shell=True, stderr=STDOUT, stdout=STDOUT, universal_newlines=True)
        run_luigi("PipelineTask", pipeline_id, job_id, luigi_log, owner, scheduler, job_type="pipeline",
                  background=background)
    except Exception as ex:
        print(ex, file=sys.stderr)
        print("unable to execute %s" % func, file=sys.stderr)


def run_phenotype_job(phenotype_id: str, job_id: str, owner: str, background=True):
    active = get_active_workers()
    total = int(util.luigi_workers)
    while active >= total:
        active = get_active_workers()
        time.sleep(2)

    luigi_log = (util.log_dir + '/luigi_%s.log') % (str(job_id))

    scheduler = util.luigi_scheduler
    print("running job %s on phenotype %s; logging here %s" % (str(job_id), str(phenotype_id), luigi_log))
    # func = "PYTHONPATH='.' luigi --workers %s --module luigi_module %s --phenotype %s --job %s --owner %s" \
    #        " --scheduler-url %s > %s 2>&1 &" % (str(util.luigi_workers), "PhenotypeTask", phenotype_id, str(job_id),
    #                                             owner, scheduler, luigi_log)
    try:
        # q.put(func)
        # call(func, shell=True, stderr=STDOUT, stdout=STDOUT, universal_newlines=True)
        # task_id, job_id, luigi_log, owner, scheduler
        run_luigi("PhenotypeTask", phenotype_id, job_id, luigi_log, owner, scheduler, background=background)
    except Exception as ex:
        print(ex, file=sys.stderr)
        print("unable to execute %s" % str(phenotype_id), file=sys.stderr)


def run_phenotype(phenotype_model: PhenotypeModel, phenotype_id: str, job_id: int, background=True):
    pipelines = get_pipelines_from_phenotype(phenotype_model)
    pipeline_ids = []
    if pipelines and len(pipelines) > 0:
        for pipeline in pipelines:
            pipeline_id = insert_pipeline_config(pipeline, util.conn_string)
            insert_phenotype_mapping(phenotype_id, pipeline_id, util.conn_string)
            pipeline_ids.append(pipeline_id)

        run_phenotype_job(phenotype_id, str(job_id), phenotype_model.owner, background=background)
    return pipeline_ids


def run_ner_pipeline(pipeline_id, job_id, owner):
    luigi.run(['PipelineTask', '--pipeline', pipeline_id, '--job', str(job_id), '--owner', owner, '--pipelinetype',
               'TermFinder'])


def run_provider_assertion_pipeline(pipeline_id, job_id, owner):
    luigi.run(['PipelineTask', '--pipeline', pipeline_id, '--job', str(job_id), '--owner', owner, '--pipelinetype',
               'ProviderAssertion'])


def run_value_extraction_pipeline(pipeline_id, job_id, owner):
    luigi.run(['PipelineTask', '--pipeline', pipeline_id, '--job', str(job_id), '--owner', owner, '--pipelinetype',
               'ValueExtractor'])


def run_luigi(task_name, task_id, job_id, luigi_log, owner, scheduler, job_type="phenotype", background=True):

    if background:
        func = "PYTHONPATH='.' luigi --workers %s --module luigi_module %s --%s %s --job %s --owner %s" \
               " --scheduler-url %s > %s 2>&1 &" % (str(util.luigi_workers), task_name, job_type, task_id, str(job_id),
                                                    owner, scheduler, luigi_log)
        call(func, shell=True, stderr=STDOUT, stdout=STDOUT, universal_newlines=True)
    else:
        args = [task_name, '--workers', str(util.luigi_workers), "--{}".format(job_type), task_id, '--job', job_id,
                '--owner', owner, '--scheduler-url', scheduler]
        luigi.run(args)


if __name__ == "__main__":
    test_model = get_sample_phenotype()
    test_model.debug = True
    p_id = insert_phenotype_model(test_model, util.conn_string)
    the_job_id = jobs.create_new_job(jobs.NlpJob(job_id=-1, name="Test Phenotype", description=test_model.description,
                                                 owner=test_model.owner, status=jobs.STARTED, date_ended=None,
                                                 phenotype_id=p_id, pipeline_id=-1,
                                                 date_started=datetime.datetime.now(),
                                                 job_type='PHENOTYPE'), util.conn_string)

    run_phenotype(test_model, p_id, the_job_id)


def run_pipeline(pipeline_type: str, pipeline_id: str, job_id: int, owner: str, background=True):
    active = get_active_workers()
    total = int(util.luigi_workers)
    while active >= total:
        time.sleep(10)
        active = get_active_workers()

    luigi_log = (util.log_dir + '/luigi_%s.log') % (str(job_id))

    scheduler = util.luigi_scheduler
    print("running job %s on pipeline %s; logging here %s" % (str(job_id), str(pipeline_id), luigi_log))
    func = "PYTHONPATH='.' luigi --workers %s --module luigi_module %s  --pipeline %s --job %s --owner %s " \
           "--pipelinetype %s --scheduler-url %s > %s 2>&1 &" % (str(util.luigi_workers), "PipelineTask", pipeline_id,
                                                                 str(job_id), owner, pipeline_type, scheduler,
                                                                 luigi_log)
    try:
        # q.put(func)
        # call(func, shell=True, stderr=STDOUT, stdout=STDOUT, universal_newlines=True)
        run_luigi("PipelineTask", pipeline_id, job_id, luigi_log, owner, scheduler, job_type="pipeline")
    except Exception as ex:
        print(ex, file=sys.stderr)
        print("unable to execute %s" % func, file=sys.stderr)


def run_phenotype_job(phenotype_id: str, job_id: str, owner: str, background=True):
    active = get_active_workers()
    total = int(util.luigi_workers)
    while active >= total:
        active = get_active_workers()
        time.sleep(2)

    luigi_log = (util.log_dir + '/luigi_%s.log') % (str(job_id))

    scheduler = util.luigi_scheduler
    print("running job %s on phenotype %s; logging here %s" % (str(job_id), str(phenotype_id), luigi_log))
    # func = "PYTHONPATH='.' luigi --workers %s --module luigi_module %s --phenotype %s --job %s --owner %s" \
    #        " --scheduler-url %s > %s 2>&1 &" % (str(util.luigi_workers), "PhenotypeTask", phenotype_id, str(job_id),
    #                                             owner, scheduler, luigi_log)
    try:
        # q.put(func)
        # call(func, shell=True, stderr=STDOUT, stdout=STDOUT, universal_newlines=True)
        # task_id, job_id, luigi_log, owner, scheduler
        run_luigi("PhenotypeTask", phenotype_id, job_id, luigi_log, owner, scheduler, background=background)
    except Exception as ex:
        print(ex, file=sys.stderr)
        print("unable to execute %s" % str(phenotype_id), file=sys.stderr)


def run_phenotype(phenotype_model: PhenotypeModel, phenotype_id: str, job_id: int):
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
    luigi.run(['PipelineTask', '--pipeline', pipeline_id, '--job', str(job_id), '--owner', owner, '--pipelinetype',
               'TermFinder'])


def run_provider_assertion_pipeline(pipeline_id, job_id, owner):
    luigi.run(['PipelineTask', '--pipeline', pipeline_id, '--job', str(job_id), '--owner', owner, '--pipelinetype',
               'ProviderAssertion'])


def run_value_extraction_pipeline(pipeline_id, job_id, owner):
    luigi.run(['PipelineTask', '--pipeline', pipeline_id, '--job', str(job_id), '--owner', owner, '--pipelinetype',
               'ValueExtractor'])


def run_luigi(task_name, task_id, job_id, luigi_log, owner, scheduler, job_type="phenotype", background=True):

    if background:
        func = "PYTHONPATH='.' luigi --workers %s --module luigi_module %s --%s %s --job %s --owner %s" \
               " --scheduler-url %s > %s 2>&1 &" % (str(util.luigi_workers), task_name, job_type, task_id, str(job_id),
                                                    owner, scheduler, luigi_log)
        call(func, shell=True, stderr=STDOUT, stdout=STDOUT, universal_newlines=True)
    else:
        args = [task_name, '--workers', str(util.luigi_workers), "--{}".format(job_type), task_id, '--job', job_id,
                '--owner', owner, '--scheduler-url', scheduler]
        luigi.run(args)


if __name__ == "__main__":
    test_model = get_sample_phenotype()
    test_model.debug = True
    p_id = insert_phenotype_model(test_model, util.conn_string)
    the_job_id = jobs.create_new_job(jobs.NlpJob(job_id=-1, name="Test Phenotype", description=test_model.description,
                                                 owner=test_model.owner, status=jobs.STARTED, date_ended=None,
                                                 phenotype_id=p_id, pipeline_id=-1,
                                                 date_started=datetime.datetime.now(),
                                                 job_type='PHENOTYPE'), util.conn_string)

    run_phenotype(test_model, p_id, the_job_id)
