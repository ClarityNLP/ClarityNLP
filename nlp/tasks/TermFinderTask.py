from algorithms import *
from data_access import jobs
from .task_utilities import pipeline_mongo_writer, BaseTask
import util

provider_assertion_filters = {
    'negex': ["Affirmed"],
    "temporality": ["Recent", "Historical"],
    "experiencer": ["Patient"]
}
SECTIONS_FILTER = "sections"


class TermFinderBatchTask(BaseTask):
    task_name = "TermFinder"

    def run_custom_task(self, temp_file, mongo_client):
        pipeline_config = self.pipeline_config
        term_matcher = TermFinder(pipeline_config.terms, pipeline_config.include_synonyms, pipeline_config
                                  .include_descendants, pipeline_config.include_ancestors, pipeline_config
                                  .vocabulary)
        filters = dict()
        if pipeline_config.sections and len(pipeline_config.sections) > 0:
            filters[SECTIONS_FILTER] = pipeline_config.sections

        self.write_log_data(jobs.IN_PROGRESS, "Finding Terms with TermFinder")

        for doc in self.docs:
            terms_found = term_matcher.get_term_full_text_matches(self.get_document_text(doc), filters)
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
                self.write_result_data(temp_file, mongo_client, doc, obj)

            del terms_found


class ProviderAssertionBatchTask(BaseTask):
    task_name = "ProviderAssertion"

    def run_custom_task(self, temp_file, mongo_client):

        pipeline_config = self.pipeline_config
        term_matcher = TermFinder(pipeline_config.terms, pipeline_config.include_synonyms, pipeline_config
                                  .include_descendants, pipeline_config.include_ancestors, pipeline_config
                                  .vocabulary)

        pa_filters = provider_assertion_filters
        if pipeline_config.sections and len(pipeline_config.sections) > 0:
            pa_filters[SECTIONS_FILTER] = pipeline_config.sections

        self.write_log_data(jobs.IN_PROGRESS, "Finding Terms with ProviderAssertion")
        for doc in self.docs:
            terms_found = term_matcher.get_term_full_text_matches(self.get_document_text(doc), pa_filters)
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

                self.write_result_data(temp_file, mongo_client, doc, obj)

            del terms_found

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
