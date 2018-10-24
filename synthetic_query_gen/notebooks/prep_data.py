import numpy as np
import json
import requests
import csv

def get_exclusion_criteria_index(criteria):
    try:
        ex_index = criteria.lower().index("exclusion criteria")
    except ValueError:
        ex_index = -1
    return ex_index


def read_aact():
    # Sample AACT data read from here - https://www.ctti-clinicaltrials.org/aact-database
    file_in = "/Users/charityhilton/Downloads/20181001_pipe-delimited-export/eligibilities.txt"
    with open('data/clinical_study.txt') as f:
        cols = None
        results = list()

        txt = ''
        for i, line in enumerate(f):

            if i == 0:
                cols = line.split('|')
            else:
                if line.startswith('NCT') and len(txt) > 0:
                    res = txt.split('|')
                    criteria = res[26]

                    ex_index = get_exclusion_criteria_index(criteria)

                    if ex_index >= 0:
                        inclusion = criteria[0:ex_index]
                        exclusion = criteria[ex_index:]
                    else:
                        inclusion = criteria
                        exclusion = ''
                    new_row = [res[0], inclusion, exclusion, res[27], res[28], res[29]]
                    if criteria != 'Please contact site for information.':
                        results.append(new_row)
                    txt = line
                else:
                    if len(line.strip()) > 0:
                        txt = txt + line

        print(len(results))
        return results


def load_aact_in_solr():
    file_in = "/Users/charityhilton/Downloads/20181001_pipe-delimited-export/eligibilities.txt"
    solr_url = "http://18.220.133.76:8983/solr/sample"
    url = solr_url + '/update?commit=true'
    headers = {
        'Content-type': 'application/json',
    }

    result_list = list()
    with open(file_in) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='|')
        line = 0
        cols = []
        for row in csv_reader:
            if line == 0:
                cols = row
                print(cols)
            else:
                print(row[1])
                criteria = str(row[8])
                criteria = criteria.replace('~', '\n')
                criteria = criteria.encode("ascii", errors="ignore").decode()
                ex_index = get_exclusion_criteria_index(criteria)

                if ex_index >= 0:
                    inclusion = criteria[0:ex_index]
                    exclusion = criteria[ex_index:]
                else:
                    inclusion = criteria
                    exclusion = ''

                d = {
                        "subject": row[1],
                         "description_attr": "AACT Clinical Trials",
                         "source": "AACT",
                         "report_date": "2018-10-24T00:00:00Z"
                     }
                for i in range(len(cols)):
                    if i != 0 and i != 1 and i != 7 and i != 8:
                        colname = cols[i] + "_attr"
                        d[colname] = str(row[i])

                d2 = d.copy()

                d["report_type"] = "Clinical Trial Inclusion Criteria"
                d["id"] = "ct_inc_" + row[0]
                d["report_id"] = "ct_inc_" + row[0]
                d["report_text"] = inclusion
                result_list.append(d)

                if len(exclusion) > 0:
                    d2["report_type"] = "Clinical Trial Exclusion Criteria"
                    d2["id"] = "ct_exc_" + row[0]
                    d2["report_id"] = "ct_exc_" + row[0]
                    d2["report_text"] = exclusion
                    result_list.append(d2)
                else:
                    print('no exclusion')
            line += 1

            if line % 100 == 0:
                print("parsed {0} lines".format(str(line)))
                # Pushing data to Solr
                data = json.dumps(result_list)
                response2 = requests.post(url, headers=headers, data=data)

                if response2.status_code == 200:
                    print("Uploaded AACT eligibilities batch")
                result_list = list()

    print("parsed {0} lines".format(str(line)))
    # Pushing data to Solr
    data = json.dumps(result_list)
    response2 = requests.post(url, headers=headers, data=data)

    if response2.status_code == 200:
        print("Uploaded AACT eligibilities all")


if __name__ == "__main__":
    # read_aact()
    load_aact_in_solr()
