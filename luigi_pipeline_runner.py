from subprocess import call
import util

# this maps the user friendly name to the pipeline task in luigi_pipeline.py
pipeline_types = {
    "TermFinder": "TermFinderPipeline",
    "ProviderAssertion": "ProviderAssertionPipeline"
}
luigi_log = util.log_dir + '/luigi.log'


def run_pipeline(pipeline_type: str, pipeline_id: str, job_id: int, owner: str):
    # after many efforts to use threading + the luigi API, can't seem to get it to work
    # this solution seems to work ok for now, may want to revisit later
    func = "PYTHONPATH='.' %s --workers %s --module luigi_pipeline %s --pipeline %s --job %s --owner %s > %s 2>&1 &" % (
        util.luigi_home, str(util.luigi_workers), pipeline_types[pipeline_type], pipeline_id, str(job_id), owner,
        luigi_log)
    try:
        call(func, shell=True)
    except Exception as ex:
        print(ex)
        print("unable to execute %s" % func)
