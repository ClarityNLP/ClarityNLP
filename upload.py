import requests
import json
import string
import csv

def upload_file(solr_url, filename):
    # filepath = "../tmp/" + filename
    # csvfile = open(filename, 'r')
    # content = csvfile.readlines()
    # req = urllib.request(solr_url)
    # req.add_header('Content-Type', 'application/csv')
    # print (urllib.urlopen(req, string.join(entry)))

    url = solr_url + '/update/csv'
    print (url)

    headers = {
    'Content-type': 'text/plain; charset=utf-8',
    }

    data = open(filename, 'rb').read()
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
