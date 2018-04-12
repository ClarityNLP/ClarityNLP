"""
OHDSI Helpers
"""

import requests
import json


ENDPOINT = 'https://apps.hdap.gatech.edu/ohdsi/WebAPI'

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
    getCohort(6)
