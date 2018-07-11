import datetime

from flask import request, Blueprint
from luigi_tools import phenotype_helper, luigi_runner
from data_access import *
from algorithms import *
from nlpql import *
from .docs import auto
from apis.api_helpers import init
from tasks import register_tasks, registered_pipelines

register_tasks()
print(registered_pipelines)


phenotype_app = Blueprint('phenotype_app', __name__)


def post_phenotype(p_cfg: PhenotypeModel):
    validated = phenotype_helper.validate_phenotype(p_cfg)
    if not validated['success']:
        return validated

    init()
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
    output["luigi_task_monitoring"] = "%s/static/visualiser/index.html#search__search=job=%s" % (
        util.luigi_url, str(job_id))
    output["intermediate_results_endpoint"] = "%s/job_results/%s/%s" % (util.main_url, str(job_id),
                                                                        'phenotype_intermediate')
    output["main_results_endpoint"] = "%s/job_results/%s/%s" % (util.main_url, str(job_id), 'phenotype')

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
        nlpql_results = run_nlpql_parser(request.data.decode("utf-8"))
        if nlpql_results['has_errors'] or nlpql_results['has_warnings']:
            return json.dumps(nlpql_results)
        else:
            p_cfg = nlpql_results['phenotype']
            return json.dumps(post_phenotype(p_cfg), indent=4)

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
