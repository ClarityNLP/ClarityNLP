import requests
import json
import string
import csv
import configparser
import psycopg2
import psycopg2.extras

def upload_file(solr_url, filepath):

    if filepath.endswith(".csv"):
        url = solr_url + '/update/csv'
        headers = {
        'Content-type': 'application/csv',
        }
    elif filepath.endswith(".json"):
        url = solr_url + '/update/json'
        headers = {
        'Content-type': 'application/json',
        }
    else:
        return "Could not upload. Unsupported file type. Currently only CSV and JSON files are supported."

    data = open(filepath, 'rb').read()
    response = requests.post(url, headers=headers, data=data)
    print (response.status_code)
    print (response.reason)

    if response.status_code == 200:
        responseMsg = "Successfully uploaded file to Solr."
    elif response.status_code == 400:
        responseMsg = "Could not upload. Check file."
    else:
        responseMsg = "Could not upload. Contact Admin."

    return responseMsg

def upload_from_db(conn_string, solr_url):
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    report_list = []
    url = solr_url + '/update/json'
    headers = {
    'Content-type': 'application/json',
    }

    cursor.execute("""SELECT * FROM mimic_v5.note""")
    result = cursor.fetchall()
    for i in result:
        concept_id = int(i[4])
        cursor.execute("""SELECT concept_name FROM mimic_v5.concept WHERE concept_id = %s""",(concept_id,))
        concept_name = cursor.fetchall()[0][0]
        d = {"subject":i[1],
            "description_attr":"Report",
            "source":"MIMIC Notes",
            "report_type":"test report",
            "report_text":i[5],
            "cg_id": "",
            "report_id": i[1],
            "is_error_attr": "",
            "id": i[1],
            "store_time_attr": "",
            "chart_time_attr": "",
            "admission_id": 123456,
            "report_date": str(i[11])
            }
        report_list.append(d)

    data = str(report_list)
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        responseMsg = "Successfully migrated data to Solr."
    else:
        responseMsg = "Could not upload. Contact Admin."

    return responseMsg

def aact_db_upload(solr_url):
    conn_string = "host='%s' dbname='%s' user='%s' password='%s' port=%s" % ('aact-db.ctti-clinicaltrials.org',
                                                                             'aact',
                                                                             'aact',
                                                                             'aact',
                                                                             '5432')

    # Connecting to the AACT DB
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    # SOLR upload headers
    #url = solr_url_2 + '/update/json'
    url = solr_url + '/update?commit=true'
    headers = {
    'Content-type': 'application/json',
    }

    # Extracting information
    cursor.execute("""SELECT * FROM detailed_descriptions INNER JOIN studies ON studies.nct_id = detailed_descriptions.nct_id WHERE studies.first_received_date > '2018-01-01' LIMIT 1000""")
    result = cursor.fetchall()

    result_list = []
    for i in result:
        d = {"subject":i[1],
            "description_attr":"AACT Clinical Trials",
            "source":"AACT Clinical Trials",
            "report_type":"Clinical Trial Description",
            "report_text":i[2],
            "cg_id": "",
            "report_id": i[0],
            "is_error_attr": "",
            "id": i[0],
            "store_time_attr": "",
            "chart_time_attr": "",
            "admission_id": "",
            "report_date": str(i[5])
            }

        result_list.append(d)

    # Pushing data to Solr
    data = json.dumps(result_list)
    response = requests.post(url, headers=headers, data=data)

    # Result verification
    if response.status_code == 200:
        response_msg = "Successfully migrated data to Solr."
    else:
        response_msg = "Could not upload. Contact Admin."

    return response_msg
