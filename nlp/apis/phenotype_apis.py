import datetime

from flask import request, Blueprint
from luigi_tools import phenotype_helper, luigi_runner
from data_access import *
from algorithms import *
from nlpql import *
from .docs import auto
from apis.api_helpers import init
from tasks import register_tasks, registered_pipelines, registered_collectors

register_tasks()
print(registered_pipelines)
print(registered_collectors)


phenotype_app = Blueprint('phenotype_app', __name__)


def post_phenotype(p_cfg: PhenotypeModel, raw_nlpql: str=''):
    validated = phenotype_helper.validate_phenotype(p_cfg)
    if not validated['success']:
        return validated

    init()
    if len(raw_nlpql) > 0:
        p_cfg.nlpql = raw_nlpql
    p_id = insert_phenotype_model(p_cfg, util.conn_string)
    if p_id == -1:
        return {"success": False,
                "error": "Failed to insert phenotype"}


    job_id = jobs.create_new_job(jobs.NlpJob(job_id=-1, name=p_cfg.description, description=p_cfg.description,
                                             owner=p_cfg.owner, status=jobs.STARTED, date_ended=None,
                                             phenotype_id=p_id, pipeline_id=-1,
                                             date_started=datetime.datetime.now(),
                                             job_type='PHENOTYPE'), util.conn_string)

    pipeline_ids = luigi_runner.run_phenotype(p_cfg, p_id, job_id)
    pipeline_urls = ["%s/pipeline_id/%s" % (util.main_url, str(pid)) for pid in pipeline_ids]

    output = dict()
    output["job_id"] = str(job_id)
    output["phenotype_id"] = str(p_id)
    output['phenotype_config'] = "%s/phenotype_id/%s" % (util.main_url, str(p_id))
    output['pipeline_ids'] = pipeline_ids
    output['pipeline_configs'] = pipeline_urls
    output["status_endpoint"] = "%s/status/%s" % (util.main_url, str(job_id))
    output["results_viewer"] = "%s?job=%s" % (util.results_viewer_url, str(job_id))
    output["luigi_task_monitoring"] = "%s/static/visualiser/index.html#search__search=job=%s" % (
        util.luigi_url, str(job_id))
    output["intermediate_results_csv"] = "%s/job_results/%s/%s" % (util.main_url, str(job_id),
                                                                        'phenotype_intermediate')
    output["main_results_csv"] = "%s/job_results/%s/%s" % (util.main_url, str(job_id), 'phenotype')

    return output


@phenotype_app.route('/phenotype', methods=['POST'])
@auto.doc(groups=['public', 'private', 'phenotypes'])
def phenotype():
    """POST a phenotype job (JSON) to run"""
    if not request.data:
        return 'POST a JSON phenotype config to execute or an id to GET. Body should be phenotype JSON'
    try:
        p_cfg = PhenotypeModel.from_dict(request.get_json())
        return json.dumps(post_phenotype(p_cfg), indent=4)
    except Exception as ex:
        print(ex)
        return 'Failed to load and insert phenotype. ' + str(ex), 400


@phenotype_app.route("/nlpql", methods=["POST"])
@auto.doc(groups=['public', 'private', 'phenotypes'])
def nlpql():
    """POST to run NLPQL phenotype"""
    if request.method == 'POST' and request.data:
        raw_nlpql = request.data.decode("utf-8")
        nlpql_results = run_nlpql_parser(raw_nlpql)
        if nlpql_results['has_errors'] or nlpql_results['has_warnings']:
            return json.dumps(nlpql_results)
        else:
            p_cfg = nlpql_results['phenotype']
            phenotype_info = post_phenotype(p_cfg, raw_nlpql)
            return json.dumps(phenotype_info, indent=4)

    return "Please POST text containing NLPQL."


@phenotype_app.route('/pipeline', methods=['POST'])
@auto.doc(groups=['public', 'private', 'phenotypes'])
def pipeline():
    """POST a pipeline job (JSON) to run on the Luigi pipeline."""
    if not request.data:
        return 'POST a JSON pipeline config to execute or an id to GET. Body should be pipeline JSON'
    try:
        init()
        p_cfg = PipelineConfig.from_dict(request.get_json())
        p_id = insert_pipeline_config(p_cfg, util.conn_string)
        if p_id == -1:
            return '{ "success", false }'
        job_id = jobs.create_new_job(jobs.NlpJob(job_id=-1, name=p_cfg.name, description=p_cfg.description,
                                                 owner=p_cfg.owner, status=jobs.STARTED, date_ended=None,
                                                 phenotype_id=-1, pipeline_id=p_id,
                                                 date_started=datetime.datetime.now(),
                                                 job_type='PIPELINE'), util.conn_string)

        luigi_runner.run_pipeline(p_cfg.config_type, str(p_id), job_id, p_cfg.owner)

        output = dict()
        output["pipeline_id"] = str(p_id)
        output["job_id"] = str(job_id)
        output["luigi_task_monitoring"] = "%s/static/visualiser/index.html#search__search=job=%s" % (
            util.luigi_url, str(job_id))
        output["status_endpoint"] = "%s/status/%s" % (util.main_url, str(job_id))
        output["results_endpoint"] = "%s/job_results/%s/%s" % (util.main_url, str(job_id), 'pipeline')

        return json.dumps(output, indent=4)

    except Exception as e:
        return 'Failed to load and insert pipeline. ' + str(e), 400


@phenotype_app.route('/pipeline_id/<int:pipeline_id>', methods=['GET'])
@auto.doc(groups=['public', 'private', 'phenotypes'])
def pipeline_id(pipeline_id: int):
    """GET a pipeline JSON based on the pipeline_id"""
    try:
        p = get_pipeline_config(pipeline_id, util.conn_string)
        return p.to_json()
    except Exception as ex:
        traceback.print_exc(file=sys.stderr)
        return "Failed to eval pipeline" + str(ex)


@phenotype_app.route('/phenotype_id/<int:phenotype_id>', methods=['GET'])
@auto.doc(groups=['public', 'private', 'phenotypes'])
def phenotype_id(phenotype_id: int):
    """GET a pipeline JSON based on the phenotype_id"""
    try:
        p = query_phenotype(phenotype_id, util.conn_string)
        return p.to_json()
    except Exception as ex:
        traceback.print_exc(file=sys.stderr)
        return "Failed to eval phenotype" + str(ex)


@phenotype_app.route("/nlpql_tester", methods=["POST"])
@auto.doc(groups=['public', 'private', 'phenotypes'])
def nlpql_tester():
    """POST to test NLPQL parsing"""
    if request.method == 'POST' and request.data:
        nlpql_results = run_nlpql_parser(request.data.decode("utf-8"))
        if nlpql_results['has_errors'] or nlpql_results['has_warnings']:
            return json.dumps(nlpql_results)
        else:
            return nlpql_results['phenotype'].to_json()

    return "Please POST text containing NLPQL."


@phenotype_app.route("/nlpql_expander", methods=["POST"])
@auto.doc(groups=['public', 'private', 'phenotypes'])
def nlpql_expander():
    """POST to expand NLPQL termset macros"""
    if request.method == 'POST' and request.data:
        nlpql_results = expand_nlpql_macros(request.data.decode("utf-8"))
        # if nlpql_results['has_errors'] or nlpql_results['has_warnings']:
        #     return json.dumps(nlpql_results)
        # else:
        #     return nlpql_results['phenotype']
        return nlpql_results

    return "Please POST text containing NLPQL."


@phenotype_app.route('/phenotype_jobs/<string:status_string>', methods=['GET'])
@auto.doc(groups=['public', 'private', 'phenotypes'])
def phenotype_jobs(status_string: str):
    """GET a phenotype jobs JSON based on the job status"""
    try:
        p = query_phenotype_jobs(status_string, util.conn_string)
        return json.dumps(p, indent=4, sort_keys=True, default=str)
    except Exception as ex:
        traceback.print_exc(file=sys.stderr)
        return "Failed: " + str(ex)


@phenotype_app.route('/phenotype_job_by_id/<string:id>', methods=['GET'])
@auto.doc(groups=['public', 'private', 'phenotypes'])
def phenotype_job_by_id(id: str):
    """GET a phenotype jobs JSON by id"""
    try:
        p = query_phenotype_job_by_id(id, util.conn_string)
        return json.dumps(p, indent=4, sort_keys=True, default=str)
    except Exception as ex:
        traceback.print_exc(file=sys.stderr)
        return "Failed: " + str(ex)


@phenotype_app.route('/phenotype_paged_results/<int:job_id>/<string:phenotype_final_str>', methods=['GET'])
@auto.doc(groups=['public', 'private', 'phenotypes'])
def get_paged_phenotype_results(job_id: int, phenotype_final_str: str):
    """GET paged phenotype results"""
    try:
        phenotype_final = False
        phenotype_final_str = str(phenotype_final_str).strip().lower()
        if phenotype_final_str == 't' or phenotype_final_str == 'true' or phenotype_final_str == 'yes':
            phenotype_final = True
        last_id = request.args.get('last_id', '')
        res = paged_phenotype_results(str(job_id), phenotype_final, last_id)

        return json.dumps(res, indent=4, default=str)
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return "Failed: " + str(e)


@phenotype_app.route('/phenotype_subjects/<int:job_id>/<string:phenotype_final_str>', methods=['GET'])
@auto.doc(groups=['public', 'private', 'phenotypes'])
def get_phenotype_subjects(job_id: int, phenotype_final_str: str):
    """GET phenotype_subjects"""
    try:
        phenotype_final = False
        phenotype_final_str = str(phenotype_final_str).strip().lower()
        if phenotype_final_str == 't' or phenotype_final_str == 'true' or phenotype_final_str == 'yes':
            phenotype_final = True
        res = phenotype_subjects(str(job_id), phenotype_final)

        return json.dumps(res, indent=4, default=str)
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return "Failed: " + str(e)


@phenotype_app.route('/phenotype_subject_results/<int:job_id>/<string:phenotype_final_str>/<string:subject>', methods=['GET'])
@auto.doc(groups=['public', 'private', 'phenotypes'])
def get_phenotype_subject_results(job_id: int, phenotype_final_str, subject: str):
    """GET phenotype results for a given subject"""
    try:
        phenotype_final = False
        phenotype_final_str = str(phenotype_final_str).strip().lower()
        if phenotype_final_str == 't' or phenotype_final_str == 'true' or phenotype_final_str == 'yes':
            phenotype_final = True
        res = phenotype_subject_results(str(job_id), phenotype_final, subject)

        return json.dumps(res, indent=4, default=str)
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return "Failed: " + str(e)


@phenotype_app.route('/phenotype_result_by_id/<string:id>', methods=['GET'])
@auto.doc(groups=['public', 'private', 'phenotypes'])
def get_phenotype_result_by_id(id: str):
    """GET phenotype result for a given mongo identifier"""
    try:
        res = lookup_phenotype_result_by_id(id)

        return json.dumps(res, indent=4, default=str)
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return "Failed: " + str(e)


@phenotype_app.route('/phenotype_structure/<int:id>', methods=['GET'])
@auto.doc(groups=['public', 'private', 'phenotypes'])
def get_phenotype_structure(id: int):
    """GET phenotype structure parsed out"""
    try:
        res = phenotype_structure(id, util.conn_string)

        return json.dumps(res, indent=4, default=str)
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return "Failed: " + str(e)


@phenotype_app.route('/phenotype_feature_results/<int:job_id>/<string:feature>', methods=['GET'])
@auto.doc(groups=['public', 'private', 'phenotypes'])
def get_phenotype_feature_results(job_id: int, feature: str):
    """GET phenotype results for a given feature"""
    try:
        res = phenotype_feature_results(str(job_id), feature)

        return json.dumps(res, indent=4, default=str)
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return "Failed: " + str(e)


@phenotype_app.route('/phenotype_results_by_id/<string:ids>', methods=['GET'])
@auto.doc(groups=['public', 'private', 'phenotypes'])
def get_phenotype_results_by_id(ids: str):
    """GET phenotype results for a comma-separated list of ids"""
    try:
        id_list = ids.split(',')
        res = lookup_phenotype_results_by_id(id_list)

        return json.dumps(res, indent=4, default=str)
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return "Failed: " + str(e)
