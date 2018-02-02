import glob
import util
import csv
import os
from datetime import datetime
try:
    from .pipeline_config import pipeline_output_positions
except Exception as e:
    print(e)
    from pipeline_config import pipeline_output_positions


def job_results(prefix: str, job: str):
    today = datetime.today().strftime('%m_%d_%Y_%H%M')
    filename = '/tmp/job%s_%s.csv' % (str(job), today)

    result_dir = "%s/%s_job%s_*.csv" % (util.tmp_dir, prefix, job)
    files = glob.glob(result_dir)

    with open(filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=util.delimiter, quotechar=util.quote_character,
                               quoting=csv.QUOTE_MINIMAL)

        csv_writer.writerow(pipeline_output_positions)
        for matched_file in files:
            with open(matched_file, newline='') as readfile:
                csv_reader = csv.reader(readfile, delimiter=util.delimiter, quotechar=util.quote_character,
                               quoting=csv.QUOTE_MINIMAL)
                for row in csv_reader:
                    csv_writer.writerow(row)
    return filename


def remove_tmp_file(filename):
    if filename:
        os.remove(filename)
