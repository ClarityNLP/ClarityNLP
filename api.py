from flask import Flask, redirect, url_for, request
import util
import json
import datetime
from data_access import pipeline_config as p_config
from data_access import jobs
import luigi_pipeline
from nlp import extract_ngrams

app = Flask(__name__)


@app.route('/')
def hello_world():
    return "Hello NLP"


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
                                                 owner=p_cfg.owner, status='STARTED', date_ended=None, phenotype_id=-1,
                                                 pipeline_id=p_id, date_started=datetime.datetime.now(),
                                                 job_type='PIPELINE'), util.conn_string)

        luigi_pipeline.run_pipeline(p_cfg.config_type, str(p_id), job_id, p_cfg.owner)

        return '{ "pipeline_id": "%s", "job_id": "%s" }' % (str(p_id), str(job_id))

    except Exception as e:
        return 'Failed to load and insert pipeline. ' + str(e), 400


@app.route('/pipeline_id', methods=['POST', 'GET'])
def pipeline_id():
    if request.method == 'POST':
        if not request.data:
            return 'POST a pipeline id'
        try:
            pid = request.data
            p = p_config.get_pipeline_config(pid, util.conn_string)
            print(p)
            job = jobs.create_new_job(jobs.NlpJob(job_id=-1,
                                                  name=p.name,
                                                  description=p.description,
                                                  owner=p.owner,
                                                  status='STARTED',
                                                  date_ended=None,
                                                  date_started=datetime.datetime.now(),
                                                  job_type='PIPELINE'), util.conn_string)
            # TODO kick off

            return '{ "job_id", %s }' % job
        except Exception as e:
            return 'Failed to load pipeline id ' + str(e), 400
    try:
        pid = request.args.get('id')
        return json.dumps(p_config.get_pipeline_config(pid, util.conn_string))
    except Exception as e:
        return "Failed to extract pipeline id parameter" + str(e)

# ngram API
@app.route('/ngram', methods=['GET'])
def get_ngram():
    if request.method == 'GET':
        if not request.data:
            return 'Provide cohort_id'

        # TODO: Parse data and make request
        # TODO: Error checking to see if all of these entries are passed
        cohort_id = requst.args['cohort_id']
        keyword = requst.args['keyword']
        n = requst.args['n']
        frequency = request.args['frequency']

        print (cohort_id)
        print (keyword)
        print (n)
        print (frequency)

        #result = extract_ngrams(cohort_id, keyword, n, frequency)

        # TODO: Format the output

    return -1


# TODO POST a phenotype job for running
# TODO GET a phenotype job status


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
