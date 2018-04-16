"""
OHDSI Helpers
"""

import requests
import json
import os


ENDPOINT = 'https://apps.hdap.gatech.edu/ohdsi/WebAPI'

def getConceptSet2(filepath):
    #url = ENDPOINT + '/vocabulary/1PCT/resolveConceptSetExpression'
    url = 'http://api.ohdsi.org/WebAPI/vocabulary/1PCT/resolveConceptSetExpression'
    #url = 'https://apps.hdap.gatech.edu/ohdsi/WebAPI/vocabulary/1PCT/resolveConceptSetExpression'
    headers = {
    'Content-type': 'application/json',
    }

    file = open(filepath,'r')
    data = file.read()
    response = requests.post(url, headers=headers, data=data)

    data = response.text
    url = 'http://api.ohdsi.org/WebAPI/vocabulary/1PCT/lookup/identifiers'
    response = requests.post(url, headers=headers, data=data)

    return response.text


# Getting concept set information
def getConceptSet(conceptset_id):
    # Getting conceptset metainfo
    url = ENDPOINT + '/conceptset/%s' %(conceptset_id)
    meta = requests.get(url).json()

    # Getting conceptset expressions
    url = ENDPOINT + '/conceptset/%s/expression' %(conceptset_id)
    expression = requests.get(url).json()

    # Getting conceptset generationinfo
    url = ENDPOINT + '/conceptset/%s/generationinfo' %(conceptset_id)
    generationinfo = requests.get(url).json()

    # Getting conceptset items
    url = ENDPOINT + '/conceptset/%s/items' %(conceptset_id)
    items = requests.get(url).json()

    conceptset = {"Meta":meta, "Expression":json.dumps(expression), "GenerationInfo":generationinfo, "Items":items}
    return json.dumps(conceptset)



# Getting Cohort information based on Cohort Name
def getCohortByName(cohort_name):
    # Getting all cohort definitions
    url = ENDPOINT + '/cohortdefinition'
    cohort_definitions = requests.get(url).json()

    # Identifying cohort_id with respect to name
    cohort_id = None
    for cohort in cohort_definitions:
        if cohort['name'] == cohort_name:
            cohort_id = cohort['id']
            break

    # Returning results
    if cohort_id is not None:
        return getCohort(cohort_id)
    else:
        return json.dumps({})


# Getting Cohort information based on Cohort ID
def getCohort(cohort_id):

    # Getting the cohort summary
    url = ENDPOINT + '/cohortanalysis/%s/summary' %(cohort_id)
    cohort_details = requests.get(url).json()
    cohort_details['cohortDefinition']['expression'] = json.loads(cohort_details['cohortDefinition']['expression']) #fixing ohdsi JSON structure bug

    # Getting list of patients in the cohort
    url = ENDPOINT + '/cohort/%s' %(cohort_id)
    cohort_patients = requests.get(url).json()

    # Creating and returning results
    cohort = {'Details':cohort_details,'Patients':cohort_patients}
    return json.dumps(cohort)


# For testing purposes
# # TODO: remove once stable
if __name__ == '__main__':
    # m = getCohort(6)
    #m = getCohortByName("text")
    m = getConceptSet2('c2.json')
    print (m)
