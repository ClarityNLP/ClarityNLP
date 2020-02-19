from flask import request,  Blueprint

from apis.api_helpers import init
from data_access import *
from algorithms import *
from claritynlp_logging import log, ERROR, DEBUG


algorithm_app = Blueprint('algorithm_app', __name__)


@algorithm_app.route('/ngram_cohort', methods=['GET'])
def get_ngram():
    """GET n-grams for a cohort, PARAMETERS: cohort_id=cohort_id, keyword=keyword, n=ngram length, frequency=cutoff
    frequency"""
    if request.method == 'GET':
        cohort_id = request.args.get('cohort_id')
        keyword = request.args.get('keyword')
        n = request.args.get('n')
        frequency = request.args.get('frequency')

        log(cohort_id)
        log(keyword)
        log(n)
        log(frequency)

        result = extract_ngrams(cohort_id, keyword, int(n), int(frequency))

        ans = '\n'.join(result)

        return ans
    return 'Unable to extract n-gram'


@algorithm_app.route('/measurement_finder', methods=['POST'])
def measurement_finder():
    """POST to extract measurements, See samples/sample_measurement_finder.json"""
    if request.method == 'POST' and request.data:
        init()
        obj = NLPModel.from_dict(request.get_json())

        results = run_measurement_finder_full(obj.text, obj.terms)
        return json.dumps([r.__dict__ for r in results], indent=4)
    return "Please POST a valid JSON object with terms and text"


@algorithm_app.route('/term_finder', methods=['POST'])
def term_finder():
    """POST to extract terms, context, negex, sections from text, See samples/sample_term_finder.json"""
    if request.method == 'POST' and request.data:
        init()
        obj = NLPModel.from_dict(request.get_json())
        finder = TermFinder(obj.terms)

        results = finder.get_term_full_text_matches(obj.text)
        return json.dumps([r.__dict__ for r in results], indent=4)
    return "Please POST a valid JSON object with terms and text"


@algorithm_app.route('/value_extractor', methods=['POST'])
def value_extractor():
    """POST to extract values such as BP, LVEF, Vital Signs etc. (See samples/sample_value_extractor.json)"""
    if request.method == 'POST' and request.data:
        init()
        obj = NLPModel.from_dict(request.get_json())
        results = run_value_extractor_full(obj.terms, obj.text, obj.min_value, obj.max_value, is_case_sensitive_text=obj
                                           .case_sensitive)

        return json.dumps([r.__dict__ for r in results], indent=4)
    return "Please POST a valid JSON object with terms and text"


@algorithm_app.route('/named_entity_recognition', methods=['POST'])
def named_entity_recognition():
    """POST to extract standard named entities. (See samples/sample_ner.json)"""
    if request.method == 'POST' and request.data:
        init()
        obj = NLPModel.from_dict(request.get_json())
        results = get_standard_entities(obj.text)

        return json.dumps([r.__dict__ for r in results], indent=4)
    return "Please POST a valid JSON object with text"


@algorithm_app.route('/pos_tagger', methods=['POST'])
def pos_tagger():
    """POST to extract Tags. (See samples/sample_pos_tag_text.json)"""
    if request.method == 'POST' and request.data:
        init()
        obj = NLPModel.from_dict(request.get_json())
        tags = get_tags(obj.text)

        return json.dumps([t.__dict__ for t in tags], indent=4)
    return "Please POST a valid JSON object with text"


@algorithm_app.route("/tnm_stage", methods=["POST"])
def tnm_stage():
    """POST to extract TNM cancer stage (See samples/sample_tnm_stage.json)"""
    if request.method == 'POST' and request.data:
        init()
        obj = NLPModel.from_dict(request.get_json())
        res = run_tnm_stager_full(obj.text)

        return json.dumps(res, indent=4)
    return "Please POST a valid JSON object text"
