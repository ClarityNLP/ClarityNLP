import luigi
import csv
from data_access import solr_data
from data_access import pipeline_config as config
from nlp import *
from data_access import jobs
import util


section_tagger_init()


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

        docs = solr_data.query(self.solr_query, rows=util.row_count, start=self.start, solr_url=util.solr_url)
        pipeline_config = config.get_pipeline_config(self.pipeline, util.conn_string)
        term_matcher = terms.SimpleTermFinder(pipeline_config.terms, pipeline_config.include_synonyms, pipeline_config
                                              .include_descendants, pipeline_config.include_ancestors)
        c_text = Context()

        with self.output().open('w') as outfile:
            csv_writer = csv.writer(outfile, delimiter=util.delimiter,
                                    quotechar=util.quote_character, quoting=csv.QUOTE_MINIMAL)
            for doc in docs:
                if doc["report_text"] and len(doc["report_text"]) > 0:
                    section_headers, section_texts = [UNKNOWN], [doc["report_text"]]
                    try:
                        section_headers, section_texts = sec_tag_process(doc["report_text"])
                    except Exception as e:
                        print(e)

                    subject = doc["subject"]
                    report_type = doc["report_type"]
                    report_id = doc["report_id"]
                    report_date = doc["report_date"]
                    for idx in range(0, len(section_headers)):
                        txt = section_texts[idx]
                        sentences = self.segment.parse_sentences(txt)
                        section_code = ".".join([str(i) for i in section_headers[idx].treecode_list])

                        for sentence in sentences:
                            for m in term_matcher.get_matches(sentence):
                                context_matches = c_text.run_context(m.group(0), sentence)
                                csv_writer.writerow([report_id, subject, report_date, report_type,
                                                     section_headers[idx].concept, section_code,
                                                     sentence, m.group(), m.start(), m.end(), pipeline_config.concept_code,
                                                     context_matches.negex.value, context_matches.temporality.value,
                                                     context_matches.experiencier.value])

    def output(self):
        return luigi.LocalTarget("%s/pipeline_job%s_term_finder_batch%s.csv" % (util.tmp_dir, str(self.job),
                                                                                str(self.start)))
