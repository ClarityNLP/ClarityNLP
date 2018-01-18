import luigi
import csv
from data_access import solr_data
from data_access import pipeline_config as config
from nlp import segmentation
from nlp import terms
from nlp import section_tagger
import util

section_tagger.section_tagger_init()

row_count = 10
delimiter = '|'
quote_character = '"'

# TODO get scheduler type and additional config


class TermFinderBatchTask(luigi.Task):
    pipeline = luigi.IntParameter()
    job = luigi.IntParameter()
    start = luigi.IntParameter()
    solr_query = luigi.Parameter()

    def run(self):
        docs = solr_data.query(self.solr_query, rows=row_count, start=self.start, solr_url=util.solr_url)
        pipeline_config = config.get_pipeline_config(self.pipeline, util.conn_string)
        term_matcher = terms.SimpleTermFinder(pipeline_config.terms)

        with self.output().open('w') as outfile:
            csv_writer = csv.writer(outfile, delimiter=delimiter,
                                    quotechar=quote_character, quoting=csv.QUOTE_MINIMAL)
            for doc in docs:
                section_headers, section_texts = section_tagger.process_report(doc["report_text"])
                subject = doc["subject"]
                report_type = doc["report_type"]
                report_id = doc["report_id"]
                report_date = doc["report_date"]
                for idx in range(0, len(section_headers)):
                    sentences = segmentation.parse_sentences(section_texts[idx])
                    section_code = ".".join([str(i) for i in section_headers[idx].treecode_list])

                    for sentence in sentences:
                        for m in term_matcher.get_matches(sentence):
                            csv_writer.writerow([report_id, subject, report_date, report_type,
                                                 section_headers[idx].concept, section_code,
                                                 sentence, m.group(), m.start(), m.end(), pipeline_config.concept_code])

    def output(self):
        return luigi.LocalTarget("%s/pipeline_job%s_term_finder_batch%s.txt" % (util.tmp_dir, str(self.job),
                                                                                str(self.start)))


class NERPipeline(luigi.Task):
    pipeline = luigi.IntParameter()
    job = luigi.IntParameter()
    owner = luigi.Parameter()

    def requires(self):
        pipeline_config = config.get_pipeline_config(self.pipeline, util.conn_string)
        solr_query = config.get_query(pipeline_config)
        total_docs = solr_data.query_doc_size(solr_query, solr_url=util.solr_url)
        doc_limit = config.get_limit(total_docs, pipeline_config)
        ranges = range(0, (doc_limit + row_count), row_count)
        matches = [TermFinderBatchTask(pipeline=self.pipeline, job=self.job, start=n, solr_query=solr_query) for n in
                   ranges]

        return matches

    def run(self):
        for t in self.input():
            print(t)


def run_ner_pipeline(pipeline_id: str, job_id: str, owner: str):
    luigi.run(['NERPipeline', '--pipeline', pipeline_id, '--job', str(job_id), '--owner', owner, '--local-scheduler'])


pipeline_types = {
    "NER": run_ner_pipeline
}


def run_pipeline(pipeline_type: str, pipeline_id: str, job_id: int, owner: str):
    pipeline_types[pipeline_type](pipeline_id, job_id, owner)


if __name__ == "__main__":
    luigi.run(['NERPipeline', '--pipeline', '1', '--job', '1234', '--owner', 'user'])
