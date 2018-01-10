from flask import Flask, redirect, url_for, request
import util
import json
from data_access import pipeline_config as p_config
from data_access import jobs

app = Flask(__name__)


@app.route('/pipeline', methods=['POST'])
def pipeline():
    if not request.data:
        return 'POST a JSON pipeline config to execute or an id to GET'
    try:
        pipeline_config = p_config.PipelineConfig.from_dict(request.get_json())
    except Exception as e:
        return 'Failed to load JSON. ' + str(e), 400


@app.route('/pipeline_id', methods=['POST', 'GET'])
def pipeline_id():
    try:
        pipeline_id = request.args.get('id')
        return json.dumps(p_config.get_pipeline_config(pipeline_id, util.conn_string))
    except Exception as e:
        return "Failed to extract pipeline id parameter" + str(e)


# TODO POST a job by pipeline_id
# TODO POST a phenotype job for running
# TODO GET a phenotype job status

if __name__ == '__main__':
    app.run(debug=True)
