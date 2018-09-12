import json, csv
import urllib, requests
import pandas as pd

url = 'http://18.220.133.76:5000/'
# url = 'http://localhost:5000/'
nlpql_url = url + 'nlpql'
expander_url = url + 'nlpql_expander'
tester_url = url + 'nlpql_tester'
print('ClarityNLP notebook helpers loaded successfully!')

def run_nlpql(nlpql):
    re = requests.post(nlpql_url, data=nlpql, headers={'content-type':'text/plain'})
    global run_result
    global main_csv
    global intermediate_csv
    global luigi
    
    
    if re.ok:
        run_result = re.json()
        main_csv = run_result['main_results_csv']
        intermediate_csv = run_result['intermediate_results_csv']
        luigi = run_result['luigi_task_monitoring']
        print("Job Successfully Submitted")
        print(json.dumps(run_result, indent=4, sort_keys=True))
        return run_result, main_csv, intermediate_csv, luigi
    else:
        return {}, '', '', ''
    
def run_term_expansion(nlpql):
    re = requests.post(expander_url, data=nlpql, headers={'content-type':'text/plain'})
    if re.ok:
        result = re.text
    else:
        result = 'Invalid NLPQL'
    return result
    