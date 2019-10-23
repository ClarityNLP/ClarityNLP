import simplejson
from flask import send_file, Blueprint, Response, request
from os import listdir
from os.path import isfile, join
from claritynlp_logging import log, ERROR, DEBUG


from data_access import *
from algorithms import *
from results import *
import tasks
import subprocess
import json

utility_app = Blueprint('utility_app', __name__)


@utility_app.route('/')
def home():
    return "Welcome to ClarityNLP!"


@utility_app.route('/kill_job/<int:job_id>', methods=['GET'])
def kill_job(job_id: int):
    log('killing job now ' + str(job_id))
    cmd = "ps -ef | grep luigi | grep -v luigid | grep \"job %d\" | awk '{print $2}'" % job_id
    pid = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, shell=True)
    output, err = pid.communicate()
    update_job_status(str(job_id), util.conn_string,
                      "KILLED", "Killed by user command")

    if len(output) > 0 and len(err) == 0:
        pid = output.decode("utf-8").strip()
        kill_cmd = "kill -9 %s" % pid
        subprocess.call(kill_cmd, shell=True)

        return "Killed job %d, pid %s!" % (job_id, pid)
    else:
        if len(output) == 0:
            return "Unable to kill job. No matching Luigi job!"
        else:
            return "Unable to kill job. %s" % err.decode("utf-8")


@utility_app.route('/delete_job/<int:job_id>', methods=['GET'])
def delete_job_by_id(job_id: int):
    log('deleting job now ' + str(job_id))
    flag = delete_job(str(job_id), util.conn_string)
    if flag == 1:
        return "Successfully deleted Job!"
    else:
        return "Unable to delete Job!"


@utility_app.route('/job_results/<int:job_id>/<string:job_type>', methods=['GET'])
def get_job_results(job_id: int, job_type: str):
    """GET job results as CSV"""
    try:
        job_output = job_results(job_type, str(job_id))
        return send_file(job_output)
    except Exception as ex:
        return "Failed to get job results" + str(ex)


@utility_app.route('/sections', methods=['GET'])
def get_section_source():
    """GET source file for sections and synonyms"""
    try:
        file_path = get_sec_tag_source_tags()
        return send_file(file_path)
    except Exception as ex:
        log(ex)
        return "Failed to retrieve sections source file"


@utility_app.route("/report_type_mappings", methods=["GET"])
def report_type_mappings():
    """GET dictionary of report type mappings"""
    mappings = get_report_type_mappings(
        util.report_mapper_url, util.report_mapper_inst, util.report_mapper_key)
    return simplejson.dumps(mappings, sort_keys=True, indent=4 * ' ')


@utility_app.route('/pipeline_types', methods=['GET'])
def pipeline_types():
    """GET valid pipeline types"""
    try:
        return repr(list(tasks.registered_pipelines.keys()))
    except Exception as ex:
        return "Failed to get pipeline types" + str(ex)


@utility_app.route('/status/<int:job_id>', methods=['GET'])
def get_job_status(job_id: int):
    """GET current job status"""
    try:
        status = jobs.get_job_status(job_id, util.conn_string)
        return json.dumps(status, indent=4)
    except Exception as e:
        return "Failed to get job status" + str(e)


@utility_app.route('/stats/<string:job_ids>', methods=['GET'])
def get_job_stats(job_ids: str):
    """GET current job stats"""
    try:
        perf = jobs.get_job_performance(job_ids.split(','), util.conn_string)
        return json.dumps(perf, indent=4)
    except Exception as e:
        return "Failed to get job stats" + str(e)


@utility_app.route('/performance/<string:job_ids>', methods=['GET'])
def get_job_performance(job_ids: str):
    """GET current job performance"""
    try:
        perf = phenotype_performance_results(job_ids.split(','))
        return json.dumps(perf, indent=4)
    except Exception as e:
        return "Failed to get job stats" + str(e)


@utility_app.route('/document/<string:report_id>', methods=['GET'])
def get_document_by_id(report_id: str):
    """GET Solr document by id"""
    try:
        doc = query_doc_by_id(report_id, util.solr_url)
        return json.dumps(doc, indent=4)
    except Exception as ex:
        return "Failed to get document by id" + str(ex)


sample_path = '../nlpql/'


@utility_app.route('/nlpql_samples', methods=['GET'])
def get_nlpql_samples():
    """GET NLPQL samples"""
    try:
        nlpql_files = list()
        for root, subdirs, files in os.walk(sample_path):

            for subdir in subdirs:
                for s_root, s_subdirs, s_files in os.walk(sample_path + subdir):
                    for file in s_files:
                        nlpql_files.append(subdir + '/' + file)

            break

        return json.dumps(nlpql_files, indent=4)
    except Exception as e:
        return "Failed to get nlpql samples" + str(e)


@utility_app.route('/nlpql_text/<string:subdir>/<string:name>', methods=['GET'])
def get_nlpql_text(subdir: str, name: str):
    """GET NLPQL sample by name"""
    try:
        sample_file = sample_path + subdir + '/' + name
        with open(sample_file, 'r') as f:
            return f.read()
    except Exception as e:
        return "Failed to get nlpql text" + str(e)


@utility_app.route('/write_nlpql_feedback', methods=['GET', 'POST'])
def write_nlpql_feedback():
    """Write NLPQL feedback"""
    if request.method == 'POST':
        data = request.get_json()
        response = writeResultFeedback(data)
        return response
    else:
        return Response('Only POST requests are supported', status=400, mimetype='application/json')


@utility_app.route('/library', methods=['GET'])
def library():
    """Get all NLPQL in NLPQL Library"""
    if request.method == 'GET':
        library = get_library(util.conn_string)
        response = json.dumps(library, indent=4, sort_keys=True, default=str)
        return response
    else:
        return Response('Only GET requests are supported', status=400, mimetype='application/json')
