import luigi
import csv
from data_access import solr_data
from data_access import pipeline_config as config
from nlp import segmentation
from nlp import terms
import util

row_count = 10
delimiter = '|'
quote_character = '"'
positions = {
    'report_id': 0,
    'subject': 1,
    'report_date': 2,
    'report_type': 3,
    'sentence': 4,
    'term': 5,
    'term_start': 6,
    'term_end': 7
}

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
                sentences = segmentation.parse_sentences(doc["report_text"])
                subject = doc["subject"]
                report_type = doc["report_type"]
                report_id = doc["report_id"]
                report_date = doc["report_date"]
                for sentence in sentences:
                    for m in term_matcher.get_matches(sentence):
                        csv_writer.writerow([report_id, subject, report_date, report_type, sentence, m.group(),
                                              m.start(), m.end()])

    def output(self):
        return luigi.LocalTarget("%s/pipeline_job%s_term_finder_batch%s.txt" % (util.tmp_dir, str(self.job), str
        (self.start)))


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
        matches = [TermFinderBatchTask(pipeline=self.pipeline, job=self.job, start=n, solr_query=solr_query) for n
                     in ranges]

        return matches

    def run(self):
        for t in self.input():
            print(t)


def run_ner_pipeline(pipeline_id: str, job_id: int, owner: str):
    luigi.run(['NERPipeline', '--pipeline', pipeline_id, '--job', str(job_id), '--owner', owner, '--local-scheduler'])


if __name__ == "__main__":
    luigi.run(['NERPipeline', '--pipeline', '1', '--job', '1234', '--owner', 'user', '--local-scheduler'])
