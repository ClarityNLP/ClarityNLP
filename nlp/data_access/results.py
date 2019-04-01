import csv
import os
import math 
import sys
import traceback
from datetime import datetime
import pandas as pd
import dask.dataframe as dd
from collections import OrderedDict
from bson.objectid import ObjectId
from pymongo import MongoClient
import data_access
import math 

import psycopg2

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
    elif job_type == 'phenotype' or job_type == 'cohort':
        return phenotype_results(job)
    elif job_type == 'phenotype_intermediate' or job_type == 'features':
        return phenotype_intermediate_results(job)
    elif job_type == 'annotations':
        return phenotype_feedback_results(job)
    else:
        return generic_results(job, job_type)



def phenotype_feedback_results(job: str):
    job_type = 'annotations'
    client = MongoClient(util.mongo_host, util.mongo_port)
    db = client[util.mongo_db]
    today = datetime.today().strftime('%m_%d_%Y_%H%M')
    filename = '/tmp/job_feedback%s_%s_%s.csv' % (job, job_type, today)
    try:
        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=util.delimiter, quotechar=util.quote_character,
                                    quoting=csv.QUOTE_MINIMAL)

            header_written = False
            query = {"job_id": int(job)}

            results = db['result_feedback'].find(query)
            columns = sorted(['comments', 'feature', 'is_correct', 'job_id', 'subject', 'report_id', 'result_id'])

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
    today = datetime.today().strftime('%m_%d_%Y_%H%M%s')
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


def lookup_phenotype_results_by_id(id_list: list):
    client = MongoClient(util.mongo_host, util.mongo_port)
    db = client[util.mongo_db]
    obj = dict()
    obj['results'] = list()
    obj['indexes'] = dict()

    try:
        # db.phenotype_results.find({"_id": { $in: [ObjectId("5b117352bcf26f020e392a9c"), ObjectId("5b117352bcf26f020e3926e2")]}})
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
            id = str(o['_id'])
            obj['indexes'][id] = n
            n = n + 1

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
        results = sorted(results, key=lambda r: r['count'], reverse=True)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    finally:
        client.close()

    return results

def phenotype_stats(job_id: str, phenotype_final: bool):
    results = phenotype_subjects(job_id, phenotype_final)
    stats = {
        "subjects": 0,
        "results": 0
    }
    if len(results) > 0:
        subjects = len(results)
        documents = 0
        for r in results:
            documents += int(r['count'])
        stats["subjects"] = subjects
        stats["results"] = documents
    return stats

def phenotype_subject_results(job_id: str, phenotype_final: bool, subject: str):
    client = MongoClient(util.mongo_host, util.mongo_port)
    db = client[util.mongo_db]
    results = []
    try:
        query = {"job_id": int(job_id), "phenotype_final": phenotype_final, "subject": subject}

        temp = list(db["phenotype_results"].find(query))
        for r in temp:
            obj = r.copy()
            for k in r.keys():
                val = r[k]
                if (isinstance(val, int) or isinstance(val, float)) and math.isnan(val):
                    del obj[k]
            results.append(obj)

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    finally:
        client.close()

    return results


def phenotype_feature_results(job_id: str, feature: str, subject: str):
    client = MongoClient(util.mongo_host, util.mongo_port)
    db = client[util.mongo_db]
    results = []
    try:
        query = {"job_id": int(job_id), "nlpql_feature": feature, "subject": subject}

        results = list(db["phenotype_results"].find(query))
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    finally:
        client.close()

    return results


def phenotype_results_by_context(context: str, query_filters: dict):
    client = MongoClient(util.mongo_host, util.mongo_port)
    db = client[util.mongo_db]
    results = []
    try:
        if context.lower() == 'patient' or context.lower() == 'subject':
            project = 'subject'
        else:
            project = 'report_id'
        results = list(db["phenotype_results"].find(query_filters, {project: 1}))

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    finally:
        client.close()

    return results

def generate_feature_matrix(context: str, query_filters:dict, job_type: str, job_id: str, phenotype_id: int):

    def assign_feature_label(row, column, feature):
        return int(row[column] == feature)
    
    interim_df_file = job_results("phenotype_intermediate", job_id)
    final_df_file = job_results("phenotype", job_id)

    interim_df = dd.read_csv(interim_df_file, header=0)
    interim_features = interim_df.loc[:, "nlpql_feature"].unique()

    final_df = dd.read_csv(final_df_file, header=0)
    final_features = final_df.loc[:, "nlpql_feature"].unique()

    out = interim_df.loc[:, ["_id", "nlpql_feature"]].merge(final_df.loc[:, ["_id", "nlpql_feature"]], how= "outer" , on=["_id"]).compute()

    for feature in interim_features.compute():
        out[feature] = out.apply(assign_feature_label, column="nlpql_feature_x", feature=feature, axis=1)

    for feature in final_features.compute():
        out[feature] = out.apply(assign_feature_label, column="nlpql_feature_y", feature=feature, axis=1)

    # get json out of postgres to recover the metadata associated with the non-matches (eg, the 0s)
    cols_to_keep = OrderedDict()

    cols_to_keep[0] = "_id"

    for i, feature in enumerate(interim_features.compute()):
        cols_to_keep[i+1] = feature

    for i, feature in enumerate(final_features.compute()):
        cols_to_keep[len(cols_to_keep.keys())+1] = feature

    results_mat = out.loc[:, cols_to_keep.values()]

    # TODO: get all the filters applied to the dataset, and then do the set math to give these people/notes all 0s
    # TODO: also, check whether we need a "context" function / filter for these results (will be relevant for when we query solr and for what we join on (e.g., patient id or note id)

    #out.columns= [x for x in set(interim_features).intersection(set(final_features))]

    # todo: check the query type first? to make sure it's a phenotype
    nlpql_config = data_access.query_phenotype(phenotype_id, util.conn_string)

    return results_mat

def remove_tmp_file(filename):
    if filename:
        os.remove(filename)


if __name__ == "__main__":
    # job_results("pipeline", "97")	
    #results = phenotype_performance_results("2152")
    #print(results)
    feature_matrix = generate_feature_matrix("", {}, "phenotype", "2156", 2004)



















