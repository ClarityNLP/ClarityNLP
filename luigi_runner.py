from subprocess import call
import util
import sys
from data_access import *

luigi_log = util.log_dir + '/luigi.log'


def run_pipeline(pipeline_type: str, pipeline_id: str, job_id: int, owner: str):
    scheduler = util.luigi_scheduler
    print("running job %s on pipeline %s; logging here %s" % (str(job_id), str(pipeline_id), luigi_log))
    func = "PYTHONPATH='.' luigi --workers %s --module luigi_pipeline %s  --pipeline %s --job %s --owner %s --pipelinetype %s --scheduler-url %s > %s 2>&1 &" % (
        str(util.luigi_workers), "PipelineTask", pipeline_id, str(job_id), owner, pipeline_type, scheduler, luigi_log)
    try:
        call(func, shell=True)
    except Exception as ex:
        print(ex, file=sys.stderr)
        print("unable to execute %s" % func, file=sys.stderr)


def run_phenotype_job(phenotype_id: str, job_id: str, owner: str):
    scheduler = util.luigi_scheduler
    print("running job %s on phenotype %s; logging here %s" % (str(job_id), str(phenotype_id), luigi_log))
    func = "PYTHONPATH='.' luigi --workers %s --module luigi_phenotype %s --phenotype %s --job %s --owner %s --scheduler-url %s > %s 2>&1 &" % (
        str(util.luigi_workers), "PhenotypeTask", phenotype_id, str(job_id), owner, scheduler, luigi_log)
    try:
        call(func, shell=True)
    except Exception as ex:
        print(ex, file=sys.stderr)
        print("unable to execute %s" % func, file=sys.stderr)


def get_pipelines_from_phenotype(model: PhenotypeModel):
    pipelines = list()
    if model and model.data_entities and len(model.data_entities) > 0:
        for e in model.data_entities:
            # self.config_type = config_type
            # self.name = name
            # self.description = description
            # self.terms = terms
            # self.limit = limit
            # self.concept_code = concept_code
            # self.owner = owner
            # self.include_synonyms = include_synonyms
            # self.include_descendants = include_descendants
            # self.include_ancestors = include_ancestors
            # self.report_tags = report_tags
            # self.vocabulary = vocabulary
            # self.sections = sections


            pipeline = PipelineConfig() # TODO
            pipelines.append(pipeline)
    return pipelines


def run_phenotype(model: PhenotypeModel, phenotype_id: str, job_id: int):
    pipelines = get_pipelines_from_phenotype(model)
    if pipelines and len(pipelines) > 0:
        for pipeline in pipelines:
            pipeline_id = insert_pipeline_config(pipeline, util.conn_string)
            insert_phenotype_mapping(phenotype_id, pipeline_id, util.conn_string)

        run_phenotype_job(phenotype_id, str(job_id), model.owner)
