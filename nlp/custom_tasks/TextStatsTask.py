from tasks.task_utilities import BaseTask, BaseCollector, pipeline_mongo_writer, get_config_string
from pymongo import MongoClient
import textacy
from textacy.text_stats import TextStats
from claritynlp_logging import log, ERROR, DEBUG



class TextStatsCollector(BaseCollector):

    collector_name = "TextStats"

    def run_custom_task(self, pipeline_id, job, owner, pipeline_type, pipeline_config, client, db):
        group_key = get_config_string(pipeline_config, "group_by", default='report_type')
        log('run custom task collector')
        q = [
            {
                "$match": {
                    "nlpql_feature": {
                        "$eq": pipeline_config.name
                    },
                    "job_id": {
                        "$eq": job
                    }
                }},
            {
                "$group": {
                    "_id": ("$" + group_key),
                    "avg_word_cnt": {
                        "$avg": "$words"
                    },
                    "avg_grade_level": {
                        "$avg": "$grade_level"
                    },
                    "avg_sentences": {
                        "$avg": "$sentences"
                    },
                    "avg_long_words": {
                        "$avg": "$long_words"
                    },
                    "avg_polysyllable_words": {
                        "$avg": "$polysyllable_words"
                    }
                }
            }
        ]

        results = list(db.phenotype_results.aggregate(q))

        group_by = "text_stats_group_by_field_" + group_key
        for r in results:
            pipeline_mongo_writer(client, pipeline_id, pipeline_type, job, 0, pipeline_config, None, {
                group_by: r['_id'],
                'average_word_count': r['avg_word_cnt'],
                'average_grade_level': r['avg_grade_level'],
                'average_sentences': r['avg_sentences'],
                'average_long_words': r['avg_long_words'],
                'average_polysyllable_words': r['avg_polysyllable_words']
            }, phenotype_final=True)


class TextStatsTask(BaseTask):
    task_name = "TextStats"

    # NLPQL

    # define sampleTask:
    # Clarity.TextStats({
    #   documentset: [ProviderNotes]
    # });

    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        for doc in self.docs:
            txt = self.get_document_text(doc)
            textacy_doc = textacy.make_spacy_doc(txt, lang='en')
            ts = TextStats(textacy_doc)

            obj = {
                "sentences": ts.n_sents,
                "words": ts.n_words,
                "characters": ts.n_chars,
                "unique_words": ts.n_unique_words,
                "grade_level": ts.flesch_kincaid_grade_level,
                "long_words": ts.n_long_words,
                "monosyllable_words": ts.n_monosyllable_words,
                "polysyllable_words": ts.n_polysyllable_words
            }
            self.write_result_data(temp_file, mongo_client, doc, obj)
