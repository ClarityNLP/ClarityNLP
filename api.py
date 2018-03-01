import os
from flask import Flask, request, send_file, render_template
from werkzeug import secure_filename
import datetime
from data_access import pipeline_config as p_config
from data_access import jobs
from data_access import job_results
import luigi_pipeline_runner
from flask_autodoc import Autodoc
from nlp import *

TMP_DIR = 'tmp'

app = Flask(__name__)
auto = Autodoc(app)


@app.route('/')
def home():
    return auto.html()

@app.errorhandler(404)
@app.route('/upload', methods = ['POST', 'GET'])
def upload():
    if request.method == 'GET':
        return render_template('solr_upload.html')

    elif request.method == 'POST':
        f = request.files['file']
        fname = f.filename
        if fname.endswith('.csv'):
            f.save(os.path.join(TMP_DIR, secure_filename(f.filename)))
            return render_template('solr_upload.html',result = "File successfully uploaded")
        else:
            return render_template('solr_upload.html',result = "Only CSV files are currently supported")

    return render_template('404.html')


@app.route('/pipeline', methods=['POST'])
@auto.doc()
def pipeline():
    """POST a pipeline job (JSON) to run on the Luigi pipeline."""
    if not request.data:
        return 'POST a JSON pipeline config to execute or an id to GET. Body should be pipeline JSON'
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
@auto.doc()
def pipeline_id():
    """GET a pipeline JSON based on the pipeline_id, PARAMETERS: id=pipeline id"""
    try:
        pid = request.args.get('id')
        return json.dumps(p_config.get_pipeline_config(pid, util.conn_string))
    except Exception as e:
        return "Failed to extract pipeline id parameter" + str(e)


@app.route('/pipeline_types', methods=['GET'])
@auto.doc()
def pipeline_types():
    """GET valid pipeline types"""
    try:
        return repr(list(luigi_pipeline_runner.pipeline_types.keys()))
    except Exception as e:
        return "Failed to get pipeline types" + str(e)


@app.route('/status', methods=['GET'])
@auto.doc()
def get_job_status():
    """GET current job status, PARAMETERS: job=job id"""
    try:
        job = request.args.get('job')
        status = jobs.get_job_status(int(job), util.conn_string)
        return json.dumps(status)
    except Exception as e:
        return "Failed to get job status" + str(e)


@app.route('/job_results', methods=['GET'])
def get_job_results():
    """GET job results as CSV, PARAMETERS: job=job id, type=job type"""
    try:
        job = request.args.get('job')
        job_type = request.args.get('type')
        results = job_results(job_type, job)
        return send_file(results)
    except Exception as e:
        return "Failed to get job results" + str(e)


@app.route('/ngram', methods=['GET'])
@auto.doc()
def get_ngram():
    """GET n-grams for a cohort, PARAMETERS: cohort_id=cohort_id, keyword=keyword, n=ngram length, frequency=cutoff frequency"""
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


@app.route('/value_extraction/<query>', methods=['POST'])
@auto.doc()
def value_extractions(query):
    """POST text to extract measurements (no sentence parsing), POST a text body to parse, query=comma-separated list of terms"""
    if request.method == 'POST' and request.data:
        t = request.data.decode("utf-8")

        results = run_value_extractor({'sentence': t, 'query': query})
        return json.dumps([r.__dict__ for r in results], indent=4)
    return "Please pass in params t (text) and q (comma-separated list of search terms)"


@app.route('/value_extraction_full/<query>', methods=['POST'])
@auto.doc()
def value_extractions_full(query):
    """POST text to extract measurements (with sentence parsing), POST a text body to parse, query=comma-separated list of terms"""
    if request.method == 'POST' and request.data:
        t = request.data.decode("utf-8")

        results = run_value_extractor_full(t, query)
        return json.dumps([r.__dict__ for r in results], indent=4)
    return "Please pass in params t (text) and q (comma-separated list of search terms)"


@app.route('/term_finder/<query>', methods=['POST'])
@auto.doc()
def term_finder(query):
    """GET terms, context, negex, sections from text (no sentence parsing), POST a text body to parse, query=comma-separated list of terms"""
    if request.method == 'POST' and request.data:
        t = request.data.decode("utf-8")
        q_terms = query.split(',')
        finder = TermFinder(q_terms)

        results = finder.get_term_matches(t)
        return json.dumps([r.__dict__ for r in results], indent=4)
    return "Please pass in params t (text) and q (comma-separated list of search terms)"


@app.route('/term_finder_full/<query>', methods=['POST'])
@auto.doc()
def term_finder_full(query):
    """GET terms, context, negex, sections from text (with sentence parsing), POST a text body to parse, query=comma-separated list of terms"""
    if request.method == 'POST' and request.data:
        t = request.data.decode("utf-8")
        q_terms = query.split(',')
        finder = TermFinder(q_terms)

        results = finder.get_term_full_text_matches(t)
        return json.dumps([r.__dict__ for r in results], indent=4)
    return "Please pass "


@app.route('/vocab_expansion', methods=['GET'])
@auto.doc()
def vocabulary_expansion():
    """GET related terms based a user entered term, PARAMETERS: type=1 (synonyms), 2 (ancestors), 3 (descendants), concept=user entered term, vocab=(optional, default is SNOMED)"""
    if request.method == 'GET':

        k = request.args.get('type')
        concept = request.args.get('concept')
        vocab = request.args.get('vocab')
        print(vocab)

        result = {"vocab":[]}

        if k == '1':
            r = get_synonyms(util.conn_string, concept, vocab)
        elif k == '2':
            r = get_ancestors(util.conn_string, concept, vocab)
        elif k == '3':
            r = get_descendants(util.conn_string, concept, vocab)
        else:
            return 'Incorrect request format'

        for i in r:
            result['vocab'].append(i[0])

        return str(result)

    return 'Vocabulary Expansion Failed'


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
