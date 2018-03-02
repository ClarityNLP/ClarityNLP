import requests
import json
import string
import csv

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
