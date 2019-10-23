from flask import request, Blueprint

from algorithms import *
from data_access import *
from ohdsi import *
from claritynlp_logging import log, ERROR, DEBUG


ohdsi_app = Blueprint('ohdsi_app', __name__)


@ohdsi_app.route('/ohdsi_create_cohort', methods=['GET'])
def ohdsi_create_cohort():
    """Creating Cohorts"""
    if request.method == 'GET':
        filepath = 'ohdsi/data/' + request.args.get('file')
        msg = createCohort(filepath)
        return msg

    return "Could not retrieve Cohort"


@ohdsi_app.route('/ohdsi_get_conceptset', methods=['GET'])
def ohdsi_get_conceptset():
    """Get concept set details."""
    if request.method == 'GET':
        filepath = 'ohdsi/data/' + request.args.get('file')
        conceptset = getConceptSet(filepath)
        return conceptset

    return "Could not retrieve Concept Set"


@ohdsi_app.route('/ohdsi_get_cohort', methods=['GET'])
def ohdsi_get_cohort():
    """Get cohort details from OHDSI."""
    if request.method == 'GET':
        cohort_id = request.args.get('cohort_id')
        cohort = json.dumps(getCohort(cohort_id))
        return cohort

    return "Could not retrieve Cohort"


@ohdsi_app.route('/ohdsi_cohort_status', methods=['GET'])
def ohdsi_cohort_status():
    """Get status of OHDSI cohort creation"""
    if request.method == 'GET':
        cohort_id = request.args.get('cohort_id')
        status = getCohortStatus(cohort_id)
        return status

    return "Could not retrieve cohort status"


@ohdsi_app.route('/ohdsi_get_cohort_by_name', methods=['GET'])
def ohdsi_get_cohort_by_name():
    """Get cohort details from OHDSI by giving Cohort name."""
    if request.method == 'GET':
        cohort_name = request.args.get('cohort_name')
        cohort = json.dumps(getCohortByName(cohort_name))
        return cohort

    return "Could not retrieve Cohort"


@ohdsi_app.route('/vocab_expansion', methods=['GET'])
def vocabulary_expansion():
    """GET related terms based a user entered term, PARAMETERS: type=1 (synonyms), 2 (ancestors), 3 (descendants), concept=user entered term, vocab=(optional, default is SNOMED)"""
    if request.method == 'GET':

        k = request.args.get('type')
        concept = request.args.get('concept')
        vocab = request.args.get('vocab')
        log(vocab)

        result = {"vocab": []}

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
