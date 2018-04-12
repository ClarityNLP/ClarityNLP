"""
OHDSI Helpers
"""

import requests
import json


ENDPOINT = 'https://apps.hdap.gatech.edu/ohdsi/WebAPI'

def getCohortByName(cohort_name):
    # Getting all cohort definitions
    url = ENDPOINT + '/cohortdefinition'
    cohort_definitions = requests.get(url).json()

    cohort_id = None

    for cohort in cohort_definitions:
        if cohort['name'] == cohort_name:
            cohort_id = cohort['id']
            break

    if cohort_id is not None:
        return getCohort(cohort_id)
    else:
        return json.dumps({})


def getCohort(cohort_id):

    # Getting the cohort summary
    url = ENDPOINT + '/cohortanalysis/%s/summary' %(cohort_id)
    cohort_details = requests.get(url).json()

    # Getting list of patients in the cohort
    url = ENDPOINT + '/cohort/%s' %(cohort_id)
    cohort_patients = requests.get(url).json()

    cohort = {'Details':cohort_details,'Patients':cohort_patients}

    return json.dumps(cohort)


    # print (data['cohortDefinition'])
    #
    # for key, val in cohort.items():
    #     print (key)



if __name__ == '__main__':
    #getCohort(6)
    m = getCohortByName("text")
    print (m)
