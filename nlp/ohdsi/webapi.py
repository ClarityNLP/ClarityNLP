"""
OHDSI Helpers
"""
import requests
import json
import util


ENDPOINT = util.ohdsi_url
if len(ENDPOINT) == 0:
    ENDPOINT = 'http://api.ohdsi.org/WebAPI'


def getConceptSet(filepath):
    url = ENDPOINT + '/vocabulary/OHDSI-CDMV5/resolveConceptSetExpression'
    #url = 'http://api.ohdsi.org/WebAPI/vocabulary/1PCT/resolveConceptSetExpression'
    headers = {
    'Content-type': 'application/json',
    }

    file = open(filepath,'r')
    data = file.read()
    response = requests.post(url, headers=headers, data=data)
    data = response.text

    url = ENDPOINT + '/vocabulary/OHDSI-CDMV5/lookup/identifiers'
    response = requests.post(url, headers=headers, data=data)

    return response.text

"""
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
"""


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
        return {}


# Getting Cohort information based on Cohort ID
def getCohort(cohort_id):
    # Getting the cohort summary
    url = ENDPOINT + '/cohortanalysis/%s/summary' % cohort_id
    cohort_details = requests.get(url).json()
    cohort_details['cohortDefinition']['expression'] = json.loads(cohort_details['cohortDefinition']['expression']) #fixing ohdsi JSON structure bug

    # Getting list of patients in the cohort
    url = ENDPOINT + '/cohort/%s' %(cohort_id)
    cohort_patients = requests.get(url).json()

    # Creating and returning results
    cohort = {'Details':cohort_details,'Patients':cohort_patients}
    return cohort

def createCohort(filepath):
    url = ENDPOINT + '/cohortdefinition/'
    headers = {
    'Content-type': 'application/json',
    }
    file = open(filepath,'r')
    data = file.read() # Don't parse to JSON. Weird OHDSI standard
    #data = json.loads(file.read())

    # Getting ID for new cohort
    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        return "Cohort could not be created. Reason: check JSON file"
    cohort_id = response.json()['id']

    # Triggering cohort creation job
    url = ENDPOINT + '/cohortdefinition/%s/generate/OHDSI-CDMV5' % cohort_id
    response = requests.get(url)

    # Checking if cohort creation job has been triggered
    if response.status_code == 200:
        return "Cohort creation job has been triggered."
    else:
        return "Cohort could not be created."


def getCohortStatus(cohort_id):
    # Getting cohort details
    url = ENDPOINT + '/cohortdefinition/%s/info' %(cohort_id)
    status = requests.get(url)
    return status.text
