from subprocess import call
import util
import sys
import luigi
# this maps the user friendly name to the pipeline task in luigi_pipeline.py
pipeline_types = {
    "TermFinder": "TermFinderPipeline",
    "ProviderAssertion": "ProviderAssertionPipeline"
}
luigi_log = util.log_dir + '/luigi.log'

def run_pipeline(pipeline_type: str, pipeline_id: str, job_id: int, owner: str):
    func = "PYTHONPATH='.' luigi --workers %s --module luigi_pipeline %s --pipeline %s --job %s --owner %s --scheduler-url http://scheduler:8082" % (
        str(util.luigi_workers), pipeline_types[pipeline_type], pipeline_id, str(job_id), owner)
    try:
        call(func, shell=True)
    except Exception as ex:
        print(ex, file=sys.stderr)
        print("unable to execute %s" % func, file=sys.stderr)
