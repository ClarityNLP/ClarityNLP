from cachetools import cached

from algorithms import *
from data_access import jobs
from .task_utilities import BaseTask, pipeline_cache, init_cache, get_document_by_id, document_text, document_sections

provider_assertion_filters = {
    'negex': ["Affirmed"],
    "temporality": ["Recent", "Historical"],
    "experiencer": ["Patient"]
}
SECTIONS_FILTER = "sections"


@cached(init_cache)
def get_finder(key):
    _, _, term_list, synonyms, descendants, ancestors, vocab, _, filters = get_values_from_key(key)
    finder_obj = TermFinder(term_list, synonyms, descendants, ancestors, vocab,
                            filters=filters)

    return finder_obj


def get_term_matches(key):
    _, doc_id, term_list, synonyms, descendants, ancestors, vocab, _, filters = get_values_from_key(key)

    objs = list()
    doc = get_document_by_id(doc_id)
    section_headers, section_texts = document_sections(doc)
    # all sentences in this document
    doc_text = document_text(doc)

    keys = key.split('|')
    keys[1] = ''
    finder_obj = get_finder('|'.join(keys))

    terms_found = finder_obj.get_term_full_text_matches(doc_text, section_headers, section_texts)
    for term in terms_found:
        obj = {
            "sentence": term.sentence,
            "section": term.section,
            "term": term.term,
            "start": term.start,
            "end": term.end,
            "negation": term.negex,
            "temporality": term.temporality,
            "experiencer": term.experiencer
        }
        objs.append(obj)

    return objs


def setup_key(name, doc_id, term_list, synonyms, descendants,
              ancestors, vocab, filters, has_special_filters):
    if isinstance(term_list, list):
        term_list = json.dumps(term_list)
    if isinstance(filters, dict):
        filters = json.dumps(filters)
    thing = '%s|%s|%s|%r|%r|%r|%s|%r' % (name, doc_id, term_list, synonyms, descendants,
                                         ancestors, vocab, has_special_filters)
    if has_special_filters:
        thing += ("|%s" + filters)
    else:
        thing += '|'
    return thing


def get_values_from_key(key):
    keys = key.split('|')
    type_name = keys[0]
    doc_id = keys[1]
    term_list = json.loads(keys[2])
    synonyms = keys[3] == "True"
    descendants = keys[4] == "True"
    ancestors = keys[5] == "True"
    vocab = keys[6]
    has_special_filters = keys[7] == "True"
    if len(keys[8]) > 0:
        filters = json.loads(keys[8])
    else:
        if type_name == "ProviderAssertion":
            filters = provider_assertion_filters
        else:
            filters = dict()
    return type_name, doc_id, term_list, synonyms, descendants, ancestors, vocab, has_special_filters, filters


@cached(pipeline_cache)
def _get_cached_terms(key):
    util.add_cache_compute_count()
    return get_term_matches(key)


def get_cached_terms(name, doc_id, term_list, synonyms, descendants, ancestors, vocab,
                     filters, has_special_filters):
    thing = setup_key(name, doc_id, term_list, synonyms, descendants, ancestors, vocab,
                      filters, has_special_filters)
    if util.use_redis_caching == "true":
        # TODO use better key method, some recoverable hash
        hashed_str = name + ':' + thing
        res = util.get_from_redis_cache(hashed_str)
        util.add_cache_query_count()
        if res:
            objs = json.loads(res)
        else:
            util.add_cache_compute_count()
            objs = get_term_matches(thing)
            util.write_to_redis_cache(hashed_str, json.dumps(objs))
    else:
        util.add_cache_query_count()
        objs = _get_cached_terms(thing)
        if not objs or len(objs) == 0:
            objs = get_term_matches(thing)
    return objs


def run_term_finder(name, filters, pipeline_config, temp_file, mongo_client, docs, write_log_data, write_result_data,
                    has_special_filters):
    pipeline_config = pipeline_config
    term_matcher = None
    write_log_data(jobs.IN_PROGRESS, "Finding Terms with " + name)

    for doc in docs:
        objs = get_cached_terms(name, doc[util.solr_report_id_field], pipeline_config.terms, pipeline_config.
                                include_synonyms, pipeline_config
                                .include_descendants, pipeline_config.include_ancestors, pipeline_config
                                .vocabulary, filters, has_special_filters)
        if objs and len(objs) > 0:
            for obj in objs:
                write_result_data(temp_file, mongo_client, doc, obj)
        else:
            if not term_matcher:
                term_matcher = TermFinder(pipeline_config.terms, pipeline_config.include_synonyms, pipeline_config
                                          .include_descendants, pipeline_config.include_ancestors, pipeline_config
                                          .vocabulary, filters=filters, excluded_terms=pipeline_config.excluded_terms)
            section_headers, section_texts = document_sections(doc)
            terms_found = term_matcher.get_term_full_text_matches(document_text(doc), section_headers, section_texts)
            for term in terms_found:
                if not isinstance(term.section, str):
                    term.section = term.section.concept
                obj = {
                    "sentence": term.sentence,
                    "section": term.section,
                    "term": term.term,
                    "text": term.term,
                    "start": term.start,
                    "end": term.end,
                    "negation": term.negex,
                    "temporality": term.temporality,
                    "experiencer": term.experiencer,
                    "value": (term.negex == "Affirmed"),
                    "result_display": {
                        "date": doc[util.solr_report_date_field],
                        "result_content": term.sentence,
                        "sentence": term.sentence,
                        "highlights": [term.term],
                        "start": [term.start],
                        "end": [term.end],
                    }
                }

                write_result_data(temp_file, mongo_client, doc, obj)


class TermFinderBatchTask(BaseTask):
    task_name = "TermFinder"

    def run_custom_task(self, temp_file, mongo_client):
        filters = dict()
        special_filters = False
        if self.pipeline_config.sections and len(self.pipeline_config.sections) > 0:
            filters[SECTIONS_FILTER] = self.pipeline_config.sections
            special_filters = True
        run_term_finder(self.task_name, filters, self.pipeline_config, temp_file, mongo_client, self.docs,
                        self.write_log_data, self.write_result_data, special_filters)


class ProviderAssertionBatchTask(BaseTask):
    task_name = "ProviderAssertion"

    def run_custom_task(self, temp_file, mongo_client):
        pipeline_config = self.pipeline_config

        special_filters = False
        pa_filters = provider_assertion_filters
        if pipeline_config.sections and len(pipeline_config.sections) > 0:
            pa_filters[SECTIONS_FILTER] = pipeline_config.sections
            special_filters = True

        run_term_finder(self.task_name, pa_filters, self.pipeline_config, temp_file, mongo_client, self.docs,
                        self.write_log_data, self.write_result_data, special_filters)
