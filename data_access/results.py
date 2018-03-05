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
    'concept_code',
    'negation',
    'temporality',
    'experiencer'
]


def job_results(job_type: str, job: str):
    client = MongoClient(util.mongo_host, util.mongo_port)
    today = datetime.today().strftime('%m_%d_%Y_%H%M')
    filename = '/tmp/job%s_%s_%s.csv' % (job, job_type, today)
    length = len(pipeline_output_positions)

    db = client[util.mongo_db]

    with open(filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=util.delimiter, quotechar=util.quote_character,
                               quoting=csv.QUOTE_MINIMAL)

        csv_writer.writerow(pipeline_output_positions)
        for res in db.pipeline_results.find({"job_id": int(job)}):
            keys = list(res.keys())
            output = [''] * length
            i = 0
            for key in pipeline_output_positions:
                if key in keys:
                    val = res[key]
                    output[i] = val
                i += 1
            csv_writer.writerow(output)

    return filename


def remove_tmp_file(filename):
    if filename:
        os.remove(filename)


if __name__ == "__main__":
    job_results("pipeline", "97")
