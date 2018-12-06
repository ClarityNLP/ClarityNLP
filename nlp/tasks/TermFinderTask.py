import json

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
def get_finder(terms, filters, include_synonyms, include_descendants, include_ancestors, vocabulary):
    if filters:
        filters = json.loads(filters)
    if terms:
        terms = json.loads(terms)
    finder_obj = TermFinder(terms, include_synonyms, include_descendants, include_ancestors, vocabulary,
                            filters=filters)
    return finder_obj


@cached(pipeline_cache)
def get_cached_terms(doc_id, term_list, include_synonyms, include_descendants, include_ancestors, vocabulary, filters):
    objs = list()
    doc = get_document_by_id(doc_id)
    section_headers, section_texts = document_sections(doc)
    # all sentences in this document
    doc_text = document_text(doc)

    finder_obj = get_finder(term_list, filters, include_synonyms, include_descendants, include_ancestors, vocabulary)

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


def run_term_finder(name, filters, pipeline_config, temp_file, mongo_client, docs, write_log_data, write_result_data):
    pipeline_config = pipeline_config
    term_matcher = None
    json_filters = None
    json_terms = None
    write_log_data(jobs.IN_PROGRESS, "Finding Terms with " + name)

    for doc in docs:
        if util.use_memory_caching == 'true':
            if not json_filters:
                json_filters = json.dumps(filters)
            if not json_terms:
                json_terms = json.dumps(pipeline_config.terms)
            objs = get_cached_terms(doc[util.solr_report_id_field], json_terms, pipeline_config.
                                    include_synonyms, pipeline_config
                                    .include_descendants, pipeline_config.include_ancestors, pipeline_config
                                    .vocabulary, json_filters)
            for obj in objs:
                write_result_data(temp_file, mongo_client, doc, obj)
        else:
            if not term_matcher:
                term_matcher = TermFinder(pipeline_config.terms, pipeline_config.include_synonyms, pipeline_config
                                          .include_descendants, pipeline_config.include_ancestors, pipeline_config
                                          .vocabulary, filters=filters)
            section_headers, section_texts = document_sections(doc)
            terms_found = term_matcher.get_term_full_text_matches(document_text(doc), section_headers, section_texts)
            for term in terms_found:
                if not isinstance(term.section, str):
                    term.section = term.section.concept
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

                write_result_data(temp_file, mongo_client, doc, obj)


class TermFinderBatchTask(BaseTask):
    task_name = "TermFinder"

    def run_custom_task(self, temp_file, mongo_client):
        filters = dict()
        if self.pipeline_config.sections and len(self.pipeline_config.sections) > 0:
            filters[SECTIONS_FILTER] = self.pipeline_config.sections
        run_term_finder(self.task_name, filters, self.pipeline_config, temp_file, mongo_client, self.docs,
                        self.write_log_data, self.write_result_data)


class ProviderAssertionBatchTask(BaseTask):
    task_name = "ProviderAssertion"

    def run_custom_task(self, temp_file, mongo_client):
        pipeline_config = self.pipeline_config

        pa_filters = provider_assertion_filters
        if pipeline_config.sections and len(pipeline_config.sections) > 0:
            pa_filters[SECTIONS_FILTER] = pipeline_config.sections

        run_term_finder(self.task_name, pa_filters, self.pipeline_config, temp_file, mongo_client, self.docs,
                        self.write_log_data, self.write_result_data)

# from cachetools import cached
#
# from algorithms import *
# from .task_utilities import BaseTask, pipeline_cache, init_cache, document_text, get_document_by_id, document_sections
#
# provider_assertion_filters = {
#     'negex': ["Affirmed"],
#     "temporality": ["Recent", "Historical"],
#     "experiencer": ["Patient"]
# }
# SECTIONS_FILTER = "sections"
#
#
# def lookup_key(pipeline_config, task_name):
#     term_key = "|".join(sorted(pipeline_config.terms))
#     return "%s~%s~%r~%r~%r~%s" % (task_name, term_key, pipeline_config.include_ancestors, pipeline_config.
#                                   include_descendants, pipeline_config.include_synonyms, pipeline_config.vocabulary)
#
#
# def _get_finder(key):
#     vals = key.split('~')
#     term_vals = vals[1].split('|')
#     include_ancestors = vals[2] == "True"
#     include_descendants = vals[3] == "True"
#     include_synonyms = vals[4] == "True"
#     vocab = vals[5]
#     finder_obj = TermFinder(term_vals, include_synonyms, include_descendants, include_ancestors, vocab)
#     return finder_obj
#
#
# @cached(init_cache)
# def get_finder(key):
#     return _get_finder(key)
#
#
# def _get_term_matches(document_id, sections, is_provider_assertion, finder_obj):
#     if is_provider_assertion:
#         filters = provider_assertion_filters
#     else:
#         filters = dict()
#     if sections:
#         filters[SECTIONS_FILTER] = json.loads(sections)
#
#     objs = list()
#     doc = get_document_by_id(document_id)
#     doc_text = document_text(doc, clean=True)
#     section_headers, section_texts = document_sections(doc)
#     terms_found = finder_obj.get_term_full_text_matches(doc_text, filters, section_headers, section_texts)
#     for term in terms_found:
#         obj = {
#             "sentence": term.sentence,
#             "section": term.section,
#             "term": term.term,
#             "start": term.start,
#             "end": term.end,
#             "negation": term.negex,
#             "temporality": term.temporality,
#             "experiencer": term.experiencer
#         }
#         objs.append(obj)
#     return objs
#
#
# @cached(pipeline_cache)
# def get_term_matches(key, document_id, sections, is_provider_assertion):
#     finder_obj = get_finder(key)
#     return _get_term_matches(document_id, sections, is_provider_assertion, finder_obj)
#
#
# class TermFinderBatchTask(BaseTask):
#     task_name = "TermFinder"
#
#     def pull_from_cache(self):
#         return True
#
#     def get_lookup_key(self):
#         if not self.lookup_key or self.lookup_key == '':
#             key = lookup_key(self.pipeline_config, self.task_name)
#             self.lookup_key = key
#         return self.lookup_key
#
#     def run_custom_task(self, temp_file, mongo_client):
#         pipeline_config = self.pipeline_config
#         if pipeline_config.sections and len(pipeline_config.sections) > 0:
#             sections = json.dumps(pipeline_config.sections)
#         else:
#             sections = None
#
#         key = self.get_lookup_key()
#         if not util.use_memory_caching:
#             finder_obj = _get_finder(key)
#         else:
#             finder_obj = None
#         for doc in self.docs:
#             if util.use_memory_caching:
#                 objs = get_term_matches(key, doc[util.solr_report_id_field], sections, False)
#             else:
#                 objs = _get_term_matches(doc[util.solr_report_id_field], sections, False, finder_obj)
#
#             for obj in objs:
#                 self.write_result_data(temp_file, mongo_client, doc, obj)
#
#             del objs
#
#
# class ProviderAssertionBatchTask(BaseTask):
#     task_name = "ProviderAssertion"
#
#     def pull_from_cache(self):
#         return True
#
#     def get_lookup_key(self):
#         if not self.lookup_key or self.lookup_key == '':
#             key = lookup_key(self.pipeline_config, self.task_name)
#             self.lookup_key = key
#         return self.lookup_key
#
#     def run_custom_task(self, temp_file, mongo_client):
#
#         pipeline_config = self.pipeline_config
#         if pipeline_config.sections and len(pipeline_config.sections) > 0:
#             sections = json.dumps(pipeline_config.sections)
#         else:
#             sections = None
#
#         key = self.get_lookup_key()
#         if not util.use_memory_caching:
#             finder_obj = _get_finder(key)
#         else:
#             finder_obj = None
#         for doc in self.docs:
#             if util.use_memory_caching:
#                 objs = get_term_matches(key, doc[util.solr_report_id_field], sections, False)
#             else:
#                 objs = _get_term_matches(doc[util.solr_report_id_field], sections, False, finder_obj)
#
#             for obj in objs:
#                 self.write_result_data(temp_file, mongo_client, doc, obj)
#
#             del objs
