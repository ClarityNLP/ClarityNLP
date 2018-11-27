import configparser
import json
import sys
import traceback
from os import path

import psycopg2
from psycopg2.extras import NamedTupleCursor
import requests

url = 'http://18.220.133.76:5000/'
# url = 'http://localhost:5000/'
nlpql_url = url + 'nlpql'
expander_url = url + 'nlpql_expander'
tester_url = url + 'nlpql_tester'

SCRIPT_DIR = path.dirname(__file__)
config = configparser.RawConfigParser()
config_path = path.join(SCRIPT_DIR, 'project.cfg')
config.read(config_path)

print('ClarityNLP notebook helpers loaded successfully!')


def load_file(filepath):
    infile = open(filepath, "r")
    if infile:
        data = infile.read().replace('\n', '')
    infile.close()
    return data


def get_cohort_patients(cohort_id):
    # http://18.220.133.76:5000/ohdsi_get_cohort?cohort_id=356
    re = requests.get(url + 'ohdsi_get_cohort?cohort_id=' + str(cohort_id))
    if re.ok:
        return re.json()
    else:
        return {'error', 'Unable to fetch cohort'}
    

def run_nlpql_tester(nlpql):
    re = requests.post(tester_url, data=nlpql, headers={'content-type': 'text/plain'})
    if re.ok:
        result = json.dumps(re.json(), indent=4)
    else:
        result = 'Invalid NLPQL'
    return result


def run_nlpql(nlpql):
    re = requests.post(nlpql_url, data=nlpql, headers={'content-type': 'text/plain'})
    global run_result
    global main_csv
    global intermediate_csv
    global luigi

    if re.ok:
        run_result = re.json()
        main_csv = run_result['main_results_csv']
        intermediate_csv = run_result['intermediate_results_csv']
        luigi = run_result['luigi_task_monitoring']
        print("Job Successfully Submitted")
        print(json.dumps(run_result, indent=4, sort_keys=True))
        return run_result, main_csv, intermediate_csv, luigi
    else:
        return {}, '', '', ''


def run_term_expansion(nlpql):
    re = requests.post(expander_url, data=nlpql, headers={'content-type': 'text/plain'})
    if re.ok:
        result = re.text
    else:
        result = 'Invalid NLPQL'
    return result


def read_property(config_tuple):
    property_name = ''
    try:
        property_name = config.get(config_tuple[0], config_tuple[1])
    except Exception as ex:
        print('Check that %s property is set in project.cfg' % str(config_tuple))
    return property_name


def query_patients(patient_list: list):
    conn_string = "host='%s' dbname='%s' user='%s' password='%s' port=%s" % (
        read_property(('pg', 'host')),
        read_property(('pg', 'dbname')),
        read_property(('pg', 'user')),
        read_property(('pg', 'password')),
        str(read_property(('pg', 'port'))))

    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor(cursor_factory=NamedTupleCursor)
    items = list()

    try:
        subject_string = ', '.join([str(x) for x in patient_list])
        cursor.execute("""
            select person_id as subject, gender_source_value as gender, race_source_value as race from
            mimic_v5.person p
            where person_id IN (
            """ + subject_string + ")")
        items = cursor.fetchall()

    except Exception as ex:
        traceback.print_exc(file=sys.stdout)
    finally:
        conn.close()

    return items
