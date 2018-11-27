import json

from cachetools import cached

from algorithms import *
from data_access import jobs
from .task_utilities import BaseTask, pipeline_cache, init_cache, document_text, get_document_by_id

provider_assertion_filters = {
    'negex': ["Affirmed"],
    "temporality": ["Recent", "Historical"],
    "experiencer": ["Patient"]
}
SECTIONS_FILTER = "sections"


def lookup_key(pipeline_config, task_name):
    term_key = "|".join(sorted(pipeline_config.terms))
    return "%s~%s~%r~%r~%r~%s" % (task_name, term_key, pipeline_config.include_ancestors, pipeline_config.
                                  include_descendants, pipeline_config.include_synonyms, pipeline_config.vocabulary)


@cached(init_cache)
def get_finder(key):
    vals = key.split('~')
    term_vals = vals[1].split('|')
    include_ancestors = bool(vals[2])
    include_descendants = bool(vals[3])
    include_synonyms = bool(vals[4])
    vocab = vals[5]
    finder_obj = TermFinder(term_vals, include_synonyms, include_descendants, include_ancestors, vocab)
    return finder_obj


@cached(pipeline_cache)
def get_term_matches(key, document_id, sections, is_provider_assertion):
    finder_obj = get_finder(key)

    if is_provider_assertion:
        filters = provider_assertion_filters
    else:
        filters = dict()
    if sections:
        filters[SECTIONS_FILTER] = json.loads(sections)

    objs = list()
    doc = get_document_by_id(document_id)
    doc_text = document_text(doc, clean=True)
    terms_found = finder_obj.get_term_full_text_matches(doc_text, filters)
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


class TermFinderBatchTask(BaseTask):
    task_name = "TermFinder"

    def pull_from_cache(self):
        return True

    def get_lookup_key(self):
        return lookup_key(self.pipeline_config, self.task_name)

    def run_custom_task(self, temp_file, mongo_client):
        pipeline_config = self.pipeline_config
        if pipeline_config.sections and len(pipeline_config.sections) > 0:
            sections = json.dumps(pipeline_config.sections)
        else:
            sections = None

        self.write_log_data(jobs.IN_PROGRESS, "Finding Terms with TermFinder")

        for doc in self.docs:
            objs = get_term_matches(self.get_lookup_key(), doc[util.solr_report_id_field], sections, False)

            for obj in objs:
                self.write_result_data(temp_file, mongo_client, doc, obj)

            del objs


class ProviderAssertionBatchTask(BaseTask):
    task_name = "ProviderAssertion"

    def pull_from_cache(self):
        return True

    def get_lookup_key(self):
        return lookup_key(self.pipeline_config, self.task_name)

    def run_custom_task(self, temp_file, mongo_client):

        pipeline_config = self.pipeline_config
        if pipeline_config.sections and len(pipeline_config.sections) > 0:
            sections = json.dumps(pipeline_config.sections)
        else:
            sections = None

        self.write_log_data(jobs.IN_PROGRESS, "Finding Terms with ProviderAssertion")

        for doc in self.docs:
            objs = get_term_matches(self.get_lookup_key(), doc[util.solr_report_id_field], sections, True)

            for obj in objs:
                self.write_result_data(temp_file, mongo_client, doc, obj)

            del objs
