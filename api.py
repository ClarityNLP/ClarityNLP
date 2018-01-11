from flask import Flask, redirect, url_for, request
import util
import json
import datetime
from data_access import pipeline_config as p_config
from data_access import jobs


app = Flask(__name__)


@app.route('/pipeline', methods=['POST'])
def pipeline():
    if not request.data:
        return 'POST a JSON pipeline config to execute or an id to GET'
    try:
        p_cfg = p_config.PipelineConfig.from_dict(request.get_json())
        # TODO write to pipeline table
        # TODO create job

    except Exception as e:
        return 'Failed to load JSON. ' + str(e), 400


@app.route('/pipeline_id', methods=['POST', 'GET'])
def pipeline_id():
    if request.method == 'POST':
        if not request.data:
            return 'POST a pipeline id'
        try:
            pid = request.data
            p = p_config.get_pipeline_config(pid, util.conn_string)
            print(p)
            job = jobs.create_new_job(jobs.NlpJob(id=-1,
                                                  name=p.name,
                                                  description=p.description,
                                                  owner=p.owner,
                                                  status='STARTED',
                                                  date_ended=None,
                                                  date_started=datetime.datetime.now(),
                                                  type='PIPELINE'), util.conn_string)
            # TODO kick off

            return '{ "job_id", %s }' % job
        except Exception as e:
            return 'Failed to load pipeline id ' + str(e), 400
    try:
        pid = request.args.get('id')
        return json.dumps(p_config.get_pipeline_config(pid, util.conn_string))
    except Exception as e:
        return "Failed to extract pipeline id parameter" + str(e)


# TODO POST a phenotype job for running
# TODO GET a phenotype job status

if __name__ == '__main__':
    app.run(debug=True)
