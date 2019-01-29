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


def load_criteria_in_solr():
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
                criteria_str = str(row[8])
                criteria_split = criteria_str.split('~')
                criteria = ''
                n = 0
                for i in criteria_split:
                    stripped = i.strip()
                    if len(stripped) > 0:
                        if n == 0:
                            criteria = stripped
                        elif not (stripped[0].islower() or stripped[0].isnumeric() or stripped[0] == ')' or stripped[0] == '(')  and n > 0:
                            criteria += '\n '
                            criteria += stripped
                        else:
                            criteria += ' '
                            criteria += stripped
                    n += 1

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
                         "report_date": "2018-10-25T00:00:00Z"
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


def load_descriptions_in_solr():
    file_in = "/Users/charityhilton/Downloads/20181001_pipe-delimited-export/detailed_descriptions.txt"
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
                txt_str = str(row[2])
                txt_split = txt_str.split('~')
                txt = ''
                n = 0
                for i in txt_split:
                    stripped = i.strip()
                    if len(stripped) > 0:
                        if n == 0:
                            txt = stripped
                        elif not (stripped[0].islower() or stripped[0].isnumeric() or stripped[0] == ')' or stripped[0] == '(') and n > 0:
                            txt += '\n '
                            txt += stripped
                        else:
                            txt += ' '
                            txt += stripped

                    n += 1
                d = {"subject": row[1],
                     "description_attr": "AACT Clinical Trials",
                     "source": "AACT",
                     "report_type": "Clinical Trial Description",
                     "report_text": txt,
                     "report_id": row[0],
                     "id": row[0],
                     "report_date":  "2018-10-25T00:00:00Z"
                     }
                result_list.append(d)
            line += 1

            if line % 100 == 0:
                print("parsed {0} lines".format(str(line)))
                # Pushing data to Solr
                data = json.dumps(result_list)
                response2 = requests.post(url, headers=headers, data=data)

                if response2.status_code == 200:
                    print("Uploaded AACT description batch")
                result_list = list()

    print("parsed {0} lines".format(str(line)))
    # Pushing data to Solr
    data = json.dumps(result_list)
    response2 = requests.post(url, headers=headers, data=data)

    if response2.status_code == 200:
        print("Uploaded AACT description all")


def load_interventions_in_solr():
    file_in = "/Users/charityhilton/Downloads/20181001_pipe-delimited-export/interventions.txt"
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
                txt_str = str(row[4])
                txt_split = txt_str.split('~')
                txt = ''
                n = 0
                for i in txt_split:
                    stripped = i.strip()
                    if len(stripped) > 0:
                        if n == 0:
                            txt = stripped
                        elif not (stripped[0].islower() or stripped[0].isnumeric() or stripped[0] == ')' or stripped[0] == '(') and n > 0:
                            txt += '\n '
                            txt += stripped
                        else:
                            txt += ' '
                            txt += stripped
                    n += 1
                # id|nct_id|intervention_type|name|description
                d = {"subject": row[1],
                     "description_attr": "AACT Clinical Trials",
                     "source": "AACT",
                     "report_type": "Clinical Trial Interventions",
                     "report_text": txt,
                     "report_id": row[0],
                     "id": row[0],
                     "type_attr": str(row[2]),
                     "name_attr": str(row[3]),
                     "report_date":  "2018-10-25T00:00:00Z"
                     }
                result_list.append(d)
            line += 1

            if line % 100 == 0:
                print("parsed {0} lines".format(str(line)))
                # Pushing data to Solr
                data = json.dumps(result_list)
                response2 = requests.post(url, headers=headers, data=data)

                if response2.status_code == 200:
                    print("Uploaded AACT intervention batch")
                result_list = list()

    print("parsed {0} lines".format(str(line)))
    # Pushing data to Solr
    data = json.dumps(result_list)
    response2 = requests.post(url, headers=headers, data=data)

    if response2.status_code == 200:
        print("Uploaded AACT intevention all")


def write_all_inclusion_ids():
    # Sample AACT data read from here - https://www.ctti-clinicaltrials.org/aact-database
    file_in = "/Users/charityhilton/Downloads/20181001_pipe-delimited-export/eligibilities.txt"
    with open(file_in) as f:
        csv_reader = csv.reader(f, delimiter='|')
        line = 0
        cols = []
        ids = open("data/nct_ids.txt","w+")
        for row in csv_reader:
            if line > 0:
                id = row[1]

                criteria_str = str(row[8])
                criteria_split = criteria_str.split('~')
                criteria = ''
                n = 0
                for i in criteria_split:
                    stripped = i.strip()
                    if len(stripped) > 0:
                        if n == 0:
                            criteria = stripped
                        elif not (stripped[0].islower() or stripped[0].isnumeric() or stripped[0] == ')' or stripped[0] == '(')  and n > 0:
                            criteria += '\n '
                            criteria += stripped
                        else:
                            criteria += ' '
                            criteria += stripped
                    n += 1

                criteria = criteria.encode("ascii", errors="ignore").decode()
                ex_index = get_exclusion_criteria_index(criteria)

                if ex_index >= 0:
                    inclusion = criteria[0:ex_index]
                else:
                    inclusion = criteria
                if len(inclusion) > 0:
                    ids.write(id)
                    ids.write('\n')
            line += 1
        ids.close()


if __name__ == "__main__":
    # read_aact()
    # load_criteria_in_solr()
    # load_descriptions_in_solr()
    # load_interventions_in_solr()
    write_all_inclusion_ids()
    print('done')
