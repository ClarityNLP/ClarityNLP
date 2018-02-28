import luigi
import csv
from data_access import solr_data
from data_access import pipeline_config as config
from nlp import *
from data_access import jobs
import util


class TermFinderBatchTask(luigi.Task):
    pipeline = luigi.IntParameter()
    job = luigi.IntParameter()
    start = luigi.IntParameter()
    batch = luigi.IntParameter()
    solr_query = luigi.Parameter()
    segment = segmentation.Segmentation()

    def run(self):
        jobs.update_job_status(str(self.job), util.conn_string, jobs.IN_PROGRESS, "Running TermFinder Batch %s" %
                               self.batch)

        pipeline_config = config.get_pipeline_config(self.pipeline, util.conn_string)
        docs = solr_data.query(self.solr_query, rows=util.row_count, start=self.start, solr_url=util.solr_url,
                               tags=pipeline_config.report_tags, mapper_inst=util.report_mapper_inst,
                               mapper_url=util.report_mapper_url, mapper_key=util.report_mapper_key)
        term_matcher = TermFinder(pipeline_config.terms, pipeline_config.include_synonyms, pipeline_config
                                  .include_descendants, pipeline_config.include_ancestors)

        with self.output().open('w') as outfile:
            csv_writer = csv.writer(outfile, delimiter=util.delimiter,
                                    quotechar=util.quote_character, quoting=csv.QUOTE_MINIMAL)
            # self.sentence = sentence
            # self.term = term
            # self.negex = negex
            # self.temporality = temporality
            # self.experiencer = experiencer
            # self.section = section
            # self.start = start
            # self.end = end
            for doc in docs:
                terms_found = term_matcher.get_term_full_text_matches(doc["report_text"])
                for term in terms_found:
                    csv_writer.writerow([doc["report_id"], doc["subject"], doc["report_date"], doc["report_type"],
                                         term.section, "",
                                         term.sentence, term.term, term.start, term.end, pipeline_config.concept_code,
                                         term.negex, term.temporality,
                                         term.experiencer])

    def output(self):
        return luigi.LocalTarget("%s/pipeline_job%s_term_finder_batch%s.csv" % (util.tmp_dir, str(self.job),
                                                                                str(self.start)))
