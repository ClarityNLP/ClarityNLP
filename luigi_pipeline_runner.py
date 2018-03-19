from subprocess import call
import util
import sys

# this maps the user friendly name to the pipeline task in luigi_pipeline.py
pipeline_types = {
    "TermFinder": "TermFinderPipeline",
    "ProviderAssertion": "ProviderAssertionPipeline",
    "ValueExtractor": "ValueExtractorPipeline"
}
luigi_log = util.log_dir + '/luigi.log'


def run_pipeline(pipeline_type: str, pipeline_id: str, job_id: int, owner: str):
    scheduler = util.luigi_scheduler
    print("running job %s on pipeline %s; logging here %s" % (str(job_id), str(pipeline_id), luigi_log))
    func = "PYTHONPATH='.' luigi --workers %s --module luigi_pipeline %s --pipeline %s --job %s --owner %s --scheduler-url %s > %s 2>&1 &" % (
        str(util.luigi_workers), pipeline_types[pipeline_type], pipeline_id, str(job_id), owner, scheduler, luigi_log)
    try:
        call(func, shell=True)
    except Exception as ex:
        print(ex, file=sys.stderr)
        print("unable to execute %s" % func, file=sys.stderr)
