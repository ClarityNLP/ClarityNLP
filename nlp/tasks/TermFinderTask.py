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

        filters = dict()
        if pipeline_config.sections and len(pipeline_config.sections) > 0:
            filters[SECTIONS_FILTER] = pipeline_config.sections

        self.write_log_data(jobs.IN_PROGRESS, "Finding Terms with TermFinder")
        term_matcher = TermFinder(pipeline_config.terms, pipeline_config.include_synonyms, pipeline_config
                                  .include_descendants, pipeline_config.include_ancestors, pipeline_config
                                  .vocabulary, filters=filters)

        for doc in self.docs:
            section_headers, section_texts = self.get_document_sections(doc)
            terms_found = term_matcher.get_term_full_text_matches(self.get_document_text(doc), section_headers,
                                                                  section_texts)
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
        pa_filters = provider_assertion_filters
        if pipeline_config.sections and len(pipeline_config.sections) > 0:
            pa_filters[SECTIONS_FILTER] = pipeline_config.sections

        term_matcher = TermFinder(pipeline_config.terms, pipeline_config.include_synonyms, pipeline_config
                                  .include_descendants, pipeline_config.include_ancestors, pipeline_config
                                  .vocabulary, filters=pa_filters)

        self.write_log_data(jobs.IN_PROGRESS, "Finding Terms with ProviderAssertion")

        for doc in self.docs:
            section_headers, section_texts = self.get_document_sections(doc)
            terms_found = term_matcher.get_term_full_text_matches(self.get_document_text(doc), section_headers,
                                                                  section_texts)
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

