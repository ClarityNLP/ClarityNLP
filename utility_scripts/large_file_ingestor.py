import csv
import sys
import requests
import json

# get file path
file = sys.argv[1]

# get solr url
solr_url = sys.argv[2]
url = solr_url + '/update?commit=true'
headers = {
'Content-type': 'application/json',
}

# to keep track of the number of rows which have been passed
count = 0

# Keeping track of chunk statistics
chunk = 0
chunk_size = 10000
num_chunk_failed = 0

try:
    # read in large csv file
    csvfile = open(file, 'r')
    reader = csv.DictReader(csvfile)
    # Uploading file in chunks to server
    s = []
    for row in reader:

        # Map your csv column names to the appropriate key present.
        # Below example is for MIMIC.
        d = {'subject': row['SUBJECT_ID'],
            'description_attr': row['DESCRIPTION'],
            'source': 'MIMIC',
            'report_type': row['CATEGORY'],
            'report_text': row['TEXT'],
            'cg_id': row['CGID'],
            'report_id': row['ROW_ID'],
            'is_error_attr': row['ISERROR'],
            'id': row['ROW_ID'],
            'store_time_attr': row['STORETIME'],
            'chart_time_attr': row['CHARTTIME'],
            'admission_id': row['HADM_ID'],
            'report_date': row['CHARTDATE']
            }
        s.append(d)

        # Chunking
        count += 1
        if count == chunk_size:
            data = json.dumps(s)
            response = requests.post(url, headers=headers, data=data)
            chunk += 1
            print ("\n\nChunk " + str(chunk) + " " + str(response.status_code))
            if response.status_code != 200:
                num_chunk_failed += 1
            s.clear()
            count = 0

    # Upload any remnant rows
    if len(s) > 0:
        response = requests.post(url, headers=headers, data=data)
        chunk += 1
        print ("\n\nChunk " + str(chunk) + " " + str(response.status_code))
        if response.status_code != 200:
            num_chunk_failed += 1

    # Close file connection
    csvfile.close()

    # Printing statistics
    print ("\n\nFINAL STATISTICS\n")
    print ("\nChunk size = " + str(chunk_size))
    print ("\nNumber of chunks = " + str(chunk))
    print ("\nNumber of failed chunk uploads = " + str(num_chunk_failed))
    print("\n\n")

except Exception as ex:
    print ("\n")
    print (ex)
    print ("\n")
