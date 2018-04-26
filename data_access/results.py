import util
import csv
import os
from pymongo import MongoClient
from datetime import datetime

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


def job_results(job_type: str, job: str):
    if job_type == 'pipeline':
        return pipeline_results(job)
    elif job_type == 'phenotype':
        return phenotype_results(job)
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
    return generic_results(job, 'phenotype')


def generic_results(job: str, job_type: str):
    client = MongoClient(util.mongo_host, util.mongo_port)
    db = client[util.mongo_db]
    today = datetime.today().strftime('%m_%d_%Y_%H%M')
    filename = '/tmp/job%s_%s_%s.csv' % (job, job_type, today)
    try:
        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=util.delimiter, quotechar=util.quote_character,
                                    quoting=csv.QUOTE_MINIMAL)

            header_written = False
            header_values = []
            length = 0
            if job_type == 'phenotype':
                query = {"job_id": int(job), "final": True}
            else:
                query = {"job_id": int(job)}

            results = db[job_type + "_results"].find(query)
            for res in results:
                keys = list(res.keys())
                if not header_written:
                    length = len(keys)
                    header_values = sorted(keys)
                    csv_writer.writerow(header_values)
                    header_written = True

                output = [''] * length
                i = 0
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


def remove_tmp_file(filename):
    if filename:
        os.remove(filename)


if __name__ == "__main__":
    job_results("pipeline", "97")
