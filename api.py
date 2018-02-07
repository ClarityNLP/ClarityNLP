from flask import Flask, request, send_file
import util
import json
import datetime
from data_access import pipeline_config as p_config
from data_access import jobs
from data_access import job_results
import luigi_pipeline_runner
from nlp import extract_ngrams
from nlp import get_synonyms, get_ancestors, get_descendants


app = Flask(__name__)


@app.route('/')
def hello_world():
    return "Welcome to NLP!"


@app.route('/pipeline', methods=['POST'])
def pipeline():
    if not request.data:
        return 'POST a JSON pipeline config to execute or an id to GET'
    try:
        p_cfg = p_config.PipelineConfig.from_dict(request.get_json())
        p_id = p_config.insert_pipeline_config(p_cfg, util.conn_string)
        if p_id == -1:
            return '{ "success", false }'
        job_id = jobs.create_new_job(jobs.NlpJob(job_id=-1, name=p_cfg.name, description=p_cfg.description,
                                                 owner=p_cfg.owner, status=jobs.STARTED, date_ended=None,
                                                 phenotype_id=-1, pipeline_id=p_id, date_started=datetime.datetime.now(),
                                                 job_type='PIPELINE'), util.conn_string)

        luigi_pipeline_runner.run_pipeline(p_cfg.config_type, str(p_id), job_id, p_cfg.owner)

        return '{ "pipeline_id": "%s", "job_id": "%s", "status_endpoint": "%s/status?job=%s", ' \
               '"results_endpoint": "%s/job_results?job=%s&type=%s", "luigi_task_monitoring":' \
               '"%s/static/visualiser/index.html#search__search=job=%s"}' % \
               (str(p_id), str(job_id), util.main_url, str(job_id), util.main_url, str(job_id), 'pipeline',
                util.luigi_url, str(job_id))

    except Exception as e:
        return 'Failed to load and insert pipeline. ' + str(e), 400


@app.route('/pipeline_id', methods=['GET'])
def pipeline_id():
    try:
        pid = request.args.get('id')
        return json.dumps(p_config.get_pipeline_config(pid, util.conn_string))
    except Exception as e:
        return "Failed to extract pipeline id parameter" + str(e)


@app.route('/pipeline_types', methods=['GET'])
def pipeline_types():
    try:
        return repr(list(luigi_pipeline_runner.pipeline_types.keys()))
    except Exception as e:
        return "Failed to get pipeline types" + str(e)


@app.route('/status', methods=['GET'])
def get_job_status():
    try:
        job = request.args.get('job')
        status = jobs.get_job_status(int(job), util.conn_string)
        return json.dumps(status)
    except Exception as e:
        return "Failed to get job status" + str(e)


@app.route('/job_results', methods=['GET'])
def get_job_results():
    try:
        job = request.args.get('job')
        job_type = request.args.get('type')
        results = job_results(job_type, job)
        return send_file(results)
    except Exception as e:
        return "Failed to get job results" + str(e)


@app.route('/ngram', methods=['GET'])
def get_ngram():
    if request.method == 'GET':
        cohort_id = request.args.get('cohort_id')
        keyword = request.args.get('keyword')
        n = request.args.get('n')
        frequency = request.args.get('frequency')

        print(cohort_id)
        print(keyword)
        print(n)
        print(frequency)

        result = extract_ngrams(cohort_id, keyword, int(n), int(frequency))

        ans = '\n'.join(result)

        return ans
    return 'Unable to extract n-gram'


@app.route('/vocab_expansion', methods=['GET'])
def vocabulary_expansion():
    if request.method == 'GET':
        """
        type:
            1 - synonyms
            2 - ancestors
            3 - descendants
        concept:
            user entered term
        """
        k = request.args.get('type')
        concept = request.args.get('concept')

        result = {"vocab":[]}

        if k == '1':
            r = get_synonyms(util.conn_string, concept)
        elif k == '2':
            r = get_ancestors(util.conn_string, concept)
        elif k == '3':
            r = get_descendants(util.conn_string, concept)
        else:
            return 'Incorrect request format'

        for i in r:
            result['vocab'].append(i[0])

        return str(result)

    return 'Vocabulary Expansion Failed'


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
