from algorithms import *
from data_access import jobs
from .task_utilities import pipeline_mongo_writer, BaseTask

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
            terms_found = term_matcher.get_term_full_text_matches(doc["report_text"], filters)
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
            terms_found = term_matcher.get_term_full_text_matches(doc["report_text"], pa_filters)
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

