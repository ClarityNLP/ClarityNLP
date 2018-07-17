from pymongo import MongoClient
from textacy import extract, Doc

import util

try:
    from .task_utilities import BaseTask, BaseCollector, pipeline_mongo_writer, get_config_integer
except Exception as e:
    print(e)
    from task_utilities import BaseTask, BaseCollector, pipeline_mongo_writer, get_config_integer

# Clarity.ngram({
#   termset:[Orthopnea],
#   "n": "3",
#   "filter_nums": true,
#   "filter_stops": true,
#   "filter_punct": true,
#   "min_freq": 2,
#   "lemmas": true,
#   "limit_to_termset": true
#   });


class NGramCollector(BaseCollector):

    def run_custom_task(self, pipeline_id, job, owner, pipeline_type, pipeline_config, client, db):
        print("running ngram collector")
        # db.phenotype_results.aggregate([{ $match: {
        #    nlpql_feature: {$eq: "orthopneaNgram"}, job_id: {$eq: 10117}}},
        # { $group: {_id: "$text",
        #    cnt: { $sum: "$count"}}}])
        print('run custom task collector')
        min_freq = get_config_integer(pipeline_config, 'min_freq', default=1)
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
                    "_id": "$text",
                    "cnt": {
                        "$sum": "$count"
                    }
                }
            }
        ]

        results = list(db.phenotype_results.aggregate(q))

        for r in results:
            if r['cnt'] >= min_freq:
                pipeline_mongo_writer(client, pipeline_id, pipeline_type, job, 0, pipeline_config, None, {
                    'text': r['_id'],
                    'count': r['cnt']
                }, phenotype_final=True)


class NGramTask(BaseTask):
    task_name = "ngram"

    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        print('run custom task')
        n_num = self.get_integer('n', default=2)
        filter_stops = self.get_boolean('filter_stops', default=True)
        filter_punct = self.get_boolean('filter_punct', default=True)
        filter_nums = self.get_boolean('filter_nums', default=False)
        min_freq = self.get_integer('min_freq', default=1)
        lemmas = self.get_boolean('lemmas', default=True)
        limit_to_termset = self.get_boolean('limit_to_termset', default=False)
        termset = self.pipeline_config.terms
        if not termset:
            termset = list()
        lower_termset = [x.lower() for x in termset]

        for doc in self.docs:
            ngrams = list()
            t_doc = Doc(doc[util.solr_text_field])
            res = extract.ngrams(t_doc, n_num, filter_stops=filter_stops, filter_punct=filter_punct,
                                 filter_nums=filter_nums, min_freq=min_freq)
            for r in res:
                if lemmas:
                    text = r.lemma_
                else:
                    text = r.text
                text = text.lower()

                if limit_to_termset:
                    for t in lower_termset:
                        if text == t or t in text:
                            ngrams.append({
                                'text': text,
                                'count': 1
                            })
                else:
                    ngrams.append({
                        'text': text,
                        'count': 1
                    })
            self.write_multiple_result_data(temp_file, mongo_client, doc, ngrams)

    def get_collector_class(self):
        return NGramCollector


if __name__ == "__main__":
    content = "Can we forge against these enemies a grand and global alliance, North and South, East and West, that can assure a more fruitful life for all mankind? Will you join in that historic effort? In the long history of the world, only a few generations have been granted the role of defending freedom in its hour of maximum danger. I do not shrink from this responsibility — I welcome it. I do not believe that any of us would exchange places with any other people or any other generation. The energy, the faith, the devotion which we bring to this endeavor will light our country and all who serve it — and the glow from that fire can truly light the world."
    d = Doc(content)
    results = extract.ngrams(d, 3)
    print(results)
