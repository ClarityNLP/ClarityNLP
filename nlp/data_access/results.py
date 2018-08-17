import csv
import os
import sys
import traceback
from datetime import datetime

from pymongo import MongoClient
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


def job_results(job_type: str, job: str):
    if job_type == 'pipeline':
        return pipeline_results(job)
    elif job_type == 'phenotype':
        return phenotype_results(job)
    elif job_type == 'phenotype_intermediate':
        return phenotype_intermediate_results(job)
    else:
        return generic_results(job, job_type)


def pipeline_results(job: str):
    client = MongoClient(util.mongo_host, util.mongo_port)
    today = datetime.today().strftime('%m_%d_%Y_%H%M')
    filename = '/tmp/job%s_pipeline_%s.csv' % (job, today)
    length = len(pipeline_output_positions)

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
        print(e)
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
    client = MongoClient(util.mongo_host, util.mongo_port)
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

            results = db[job_type + "_results"].find(query)
            columns = sorted(get_columns(db, job, job_type, phenotype_final))
            for res in results:
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
        print(e)
    finally:
        client.close()

    return filename


def lookup_phenotype_result_by_id(id: str):
    client = MongoClient(util.mongo_host, util.mongo_port)
    db = client[util.mongo_db]
    obj = dict()

    try:
        obj = db.phenotype_results.find_one({'_id': ObjectId(id)})
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        obj['success'] = False
    finally:
        client.close()

    return obj


def paged_phenotype_results(job_id: str, phenotype_final: bool, last_id: str = ''):
    client = MongoClient(util.mongo_host, util.mongo_port)
    db = client[util.mongo_db]
    obj = dict()

    try:
        columns = sorted(get_columns(db, job_id, 'phenotype', phenotype_final))
        if last_id == '' and last_id != '-1':
            results = list(db.phenotype_results.find({"job_id": int(job_id), "phenotype_final": phenotype_final}).limit(
                page_size))
            obj['count'] = int(
                db.phenotype_results.find({"job_id": int(job_id), "phenotype_final": phenotype_final}).count())
        else:
            results = list(db.phenotype_results.find({"_id": {"$gt": ObjectId(last_id)}, "job_id": int(job_id),
                 "phenotype_final": phenotype_final}).limit(page_size))

        results_length = len(results)
        no_more = False
        if results_length < page_size:
            no_more = True
        if results_length > 0:
            new_last_id = results[-1]['_id']
        else:
            new_last_id = ''

        obj['results'] = results
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
    client = MongoClient(util.mongo_host, util.mongo_port)
    db = client[util.mongo_db]
    results = []
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
        results = list(db.phenotype_results.aggregate(q))
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    finally:
        client.close()

    return results


def phenotype_subject_results(job_id: str, phenotype_final: bool, subject: str):
    client = MongoClient(util.mongo_host, util.mongo_port)
    db = client[util.mongo_db]
    results = []
    try:
        query = {"job_id": int(job_id), "phenotype_final": phenotype_final, "subject": subject}

        results = list(db["phenotype_results"].find(query))
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    finally:
        client.close()

    return results


def phenotype_feature_results(job_id: str, feature: str):
    client = MongoClient(util.mongo_host, util.mongo_port)
    db = client[util.mongo_db]
    results = []
    try:
        query = {"job_id": int(job_id), "nlpql_feature": feature}

        results = list(db["phenotype_results"].find(query))
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    finally:
        client.close()

    return results


def remove_tmp_file(filename):
    if filename:
        os.remove(filename)


if __name__ == "__main__":
    job_results("pipeline", "97")
