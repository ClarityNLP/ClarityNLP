import csv
import math
import os
import sys
import traceback
from datetime import datetime
from claritynlp_logging import log, ERROR, DEBUG


from bson.objectid import ObjectId

import util

pipeline_output_positions = [
    '_id',
    'job_id',
    'pipeline_id',
    'pipeline_type',
    'report_id',
    'subject',
    'report_date',
    'report_type',
    'section',
    'sentence',
    'term',
    'start',
    'end',
    'concept_code'
]
page_size = 100


def display_mapping(x):
    if not x or 'result_display' in x:
        return x

    try:
        val = ''
        if 'value' in x:
            val = x.get('value')
        elif 'term' in x:
            val = x.get('term')
        highlight = val

        sentence = ''
        if 'sentence' in x:
            sentence = x.get('sentence')
        elif 'text' in x:
            sentence = x.get('text')

        start = 0
        end = 0
        if 'start' in x:
            start = x.get('start')
        if 'end' in x:
            end = x.get('end')

        dt = ''
        if 'report_date' in x:
            dt = x.get('report_date')
        elif 'date' in x:
            dt = x.get('date')

        highlight_values = []
        if highlight and len(highlight) > 0:
            highlight_values = [highlight]

        x['result_display'] = {
            "date": dt,
            "result_content": val,
            "highlights": highlight_values,
            "sentence": sentence,
            "start": [start],
            "end": [end]
        }
    except Exception as ex:
        log(ex)
        x['result_display'] = {
            'date': ''
        }
    return x


def job_results(job_type: str, job: str):
    if job_type == 'pipeline':
        return pipeline_results(job)
    elif job_type == 'phenotype' or job_type == 'cohort':
        return phenotype_results(job)
    elif job_type == 'phenotype_intermediate' or job_type == 'features':
        return phenotype_intermediate_results(job)
    elif job_type == 'annotations':
        return phenotype_feedback_results(job)
    else:
        return generic_results(job, job_type)


def phenotype_performance_results(jobs: list):
    client = util.mongo_client()
    db = client[util.mongo_db]
    metrics = dict()

    if len(jobs) < 1:
        return metrics
    try:
        for job in jobs:
            performance = {
                'total_answered': 0,
                'total_correct': 0,
                'total_incorrect': 0,
                'accuracy_score': 0.0,
                'total_comments': 0
            }

            query = {"job_id": int(job.strip())}

            has_comments = 0
            count = 0
            correct = 0
            query_results = db['result_feedback'].find(query)
            # ['comments', 'feature', 'is_correct', 'job_id', 'subject', 'report_id', 'result_id']
            for res in query_results:
                if len(res['comments']) > 0:
                    has_comments += 1
                else:
                    count += 1
                    if res['is_correct'] == 'true' or res['is_correct'] == 'True':
                        correct += 1

            if count > 0:
                performance['accuracy_score'] = float((correct * 1.0) / (count * 1.0))
            else:
                performance['accuracy_score'] = 0.0
            performance['total_incorrect'] = count - correct
            performance['total_correct'] = correct
            performance['total_answered'] = count
            performance['total_comments'] = has_comments

            metrics[job] = performance
    except Exception as e:
        log(e, ERROR)
    finally:
        client.close()

    return metrics


def phenotype_feedback_results(job: str):
    job_type = 'annotations'
    client = util.mongo_client()
    db = client[util.mongo_db]
    today = datetime.today().strftime('%m_%d_%Y_%H%M')
    filename = '/tmp/job_feedback%s_%s_%s.csv' % (job, job_type, today)
    try:
        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=util.delimiter, quotechar=util.quote_character,
                                    quoting=csv.QUOTE_MINIMAL)

            header_written = False
            query = {"job_id": int(job)}

            query_results = db['result_feedback'].find(query)
            columns = sorted(['comments', 'feature', 'is_correct', 'job_id', 'subject', 'report_id', 'result_id'])

            for res in query_results:
                keys = list(res.keys())
                if not header_written:
                    length = len(columns)
                    csv_writer.writerow(columns)
                    header_written = True

                output = [''] * length
                i = 0
                for key in columns:
                    if key in keys:
                        val = res[key]
                        output[i] = val
                    else:
                        output[i] = ''
                    i += 1
                csv_writer.writerow(output)

    except Exception as e:
        log(e)
    finally:
        client.close()

    return filename


def pipeline_results(job: str):
    client = util.mongo_client()
    today = datetime.today().strftime('%m_%d_%Y_%H%M')
    filename = '/tmp/job%s_pipeline_%s.csv' % (job, today)

    db = client[util.mongo_db]

    try:
        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=util.delimiter, quotechar=util.quote_character,
                                    quoting=csv.QUOTE_MINIMAL)

            header_written = False
            header_values = pipeline_output_positions
            length = 0
            for res in db.pipeline_results.find({"job_id": int(job)}):
                keys = list(res.keys())
                if not header_written:
                    new_cols = []
                    for k in keys:
                        if k not in header_values:
                            new_cols.append(k)
                    new_cols = sorted(new_cols)
                    header_values.extend(new_cols)

                    length = len(header_values)
                    csv_writer.writerow(header_values)
                    header_written = True

                i = 0
                output = [''] * length
                for key in header_values:
                    if key in keys:
                        val = res[key]
                        output[i] = val
                    i += 1
                csv_writer.writerow(output)
    except Exception as e:
        log(e, ERROR)
    finally:
        client.close()

    return filename


def phenotype_results(job: str):
    return generic_results(job, 'phenotype', True)


def phenotype_intermediate_results(job: str):
    return generic_results(job, 'phenotype', False)


def get_columns(db, job: str, job_type: str, phenotype_final: bool):
    lookup_key = "pipeline_type"
    types = db[job_type + "_results"].distinct(lookup_key, {"job_id": int(job), "phenotype_final": phenotype_final})
    if len(types) == 0:
        lookup_key = "nlpql_feature"
        types = db[job_type + "_results"].distinct(lookup_key,
                                                   {"job_id": int(job), "phenotype_final": phenotype_final})
    cols = list()
    for j in types:
        query = {"job_id": int(job), lookup_key: j, "phenotype_final": phenotype_final}
        results = db[job_type + "_results"].find_one(query)
        keys = list(results.keys())
        cols.extend(keys)
    return list(set(cols))


def generic_results(job: str, job_type: str, phenotype_final: bool = False):
    client = util.mongo_client()
    db = client[util.mongo_db]
    today = datetime.today().strftime('%m_%d_%Y_%H%M')
    filename = '/tmp/job%s_%s_%s.csv' % (job, job_type, today)
    try:
        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=util.delimiter, quotechar=util.quote_character,
                                    quoting=csv.QUOTE_MINIMAL)

            header_written = False
            length = 0
            if job_type == 'phenotype':
                query = {"job_id": int(job), "phenotype_final": phenotype_final}
            else:
                query = {"job_id": int(job)}

            query_results = db[job_type + "_results"].find(query)
            columns = sorted(get_columns(db, job, job_type, phenotype_final))
            for res in query_results:
                keys = list(res.keys())
                if not header_written:
                    length = len(columns)
                    csv_writer.writerow(columns)
                    header_written = True

                output = [''] * length
                i = 0
                for key in columns:
                    if key in keys:
                        val = res[key]
                        output[i] = val
                    else:
                        output[i] = ''
                    i += 1
                csv_writer.writerow(output)

    except Exception as e:
        log(e)
    finally:
        client.close()

    return filename


def lookup_phenotype_result_by_id(id: str):
    client = util.mongo_client()
    db = client[util.mongo_db]
    obj = dict()

    try:
        obj = db.phenotype_results.find_one({'_id': ObjectId(id)})
        obj = display_mapping(obj)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        obj['success'] = False
    finally:
        client.close()

    return obj


def lookup_phenotype_results_by_id(id_list: list):
    client = util.mongo_client()
    db = client[util.mongo_db]
    obj = dict()
    obj['results'] = list()
    obj['indexes'] = dict()

    try:
        # db.phenotype_results.find({"_id": { $in: [ObjectId("5b117352bcf26f020e392a9c"),
        # ObjectId("5b117352bcf26f020e3926e2")]}})
        # TODO TODO TODO
        ids = list(map(lambda x: ObjectId(x), id_list))
        res = db.phenotype_results.find({
            "_id": {
                "$in": ids
            }
        })
        obj['results'] = list(res)
        n = 0
        for o in obj['results']:
            o = display_mapping(o)
            id = str(o['_id'])
            obj['indexes'][id] = n
            n = n + 1

    except Exception as e:
        log(e, ERROR)
        traceback.print_exc(file=sys.stdout)
        obj['success'] = False
    finally:
        client.close()

    return obj


def paged_phenotype_results(job_id: str, phenotype_final: bool, last_id: str = ''):
    client = util.mongo_client()
    db = client[util.mongo_db]
    obj = dict()

    try:
        columns = sorted(get_columns(db, job_id, 'phenotype', phenotype_final))
        if last_id == '' and last_id != '-1':
            res = list(db.phenotype_results.find({"job_id": int(job_id), "phenotype_final": phenotype_final}).limit(
                page_size))
            obj['count'] = int(
                db.phenotype_results.find({"job_id": int(job_id), "phenotype_final": phenotype_final}).count())
        else:
            res = list(db.phenotype_results.find({"_id": {"$gt": ObjectId(last_id)}, "job_id": int(job_id),
                                                  "phenotype_final": phenotype_final}).limit(page_size))

        results_length = len(res)
        no_more = False
        if results_length < page_size:
            no_more = True
        if results_length > 0:
            new_last_id = res[-1]['_id']
        else:
            new_last_id = ''

        obj['results'] = list(map(display_mapping, res))
        obj['no_more'] = no_more
        obj['new_last_id'] = new_last_id
        obj['columns'] = columns
        obj['result_count'] = results_length
        obj['success'] = True

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        obj['success'] = False
    finally:
        client.close()

    return obj


def phenotype_subjects(job_id: str, phenotype_final: bool):
    client = util.mongo_client()
    db = client[util.mongo_db]
    res = []
    # db.phenotype_results.aggregate([  {"$match":{"job_id":{"$eq":10201}, "phenotype_final":{"$eq":true}}},
    #  {"$group" : {_id:"$subject", count:{$sum:1}}} ])
    try:
        q = [
            {
                "$match": {
                    "phenotype_final": {
                        "$eq": phenotype_final
                    },
                    "job_id": {
                        "$eq": int(job_id)
                    }
                }},
            {
                "$group": {
                    "_id": "$subject",
                    "count": {
                        "$sum": 1
                    }
                }
            }
        ]
        res = list(db.phenotype_results.aggregate(q))
        res = sorted(res, key=lambda r: r['count'], reverse=True)
    except Exception as e:
        log(e, ERROR)
    finally:
        client.close()

    return res


def phenotype_stats(job_id: str, phenotype_final: bool):
    res = phenotype_subjects(job_id, phenotype_final)
    stats = {
        "subjects": 0,
        "results": 0
    }
    if len(res) > 0:
        subjects = len(res)
        documents = 0
        for r in res:
            documents += int(r['count'])
        stats["subjects"] = subjects
        stats["results"] = documents
    return stats


def phenotype_subject_results(job_id: str, phenotype_final: bool, subject: str):
    client = util.mongo_client()
    db = client[util.mongo_db]
    res = []
    try:
        query = {"job_id": int(job_id), "phenotype_final": phenotype_final, "subject": subject}

        temp = list(db["phenotype_results"].find(query))
        for r in temp:
            obj = r.copy()
            for k in r.keys():
                val = r[k]
                if (isinstance(val, int) or isinstance(val, float)) and math.isnan(val):
                    del obj[k]
            res.append(obj)

    except Exception as e:
        log(e, ERROR)
    finally:
        client.close()

    return res


def phenotype_feature_results(job_id: str, feature: str, subject: str):
    client = util.mongo_client()
    db = client[util.mongo_db]
    res = []
    try:
        query = {"job_id": int(job_id), "nlpql_feature": feature, "subject": subject}

        res = list(db["phenotype_results"].find(query))
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    finally:
        client.close()

    return res


def phenotype_results_by_context(context: str, query_filters: dict):
    client = util.mongo_client()
    db = client[util.mongo_db]
    res = []
    try:
        if context.lower() == 'patient' or context.lower() == 'subject':
            project = 'subject'
        else:
            project = 'report_id'
        res = list(db["phenotype_results"].find(query_filters, {project: 1}))

    except Exception as e:
        log(e, ERROR)
        traceback.print_exc(file=sys.stdout)
    finally:
        client.close()

    return res


def remove_tmp_file(filename):
    if filename:
        os.remove(filename)


if __name__ == "__main__":
    # job_results("pipeline", "97")
    results = phenotype_performance_results(["2152"])
    log(results)
