# setup sample solr core and documents

import os
import sys
import json
import argparse
import datetime
import requests
import subprocess

_VERSION_MAJOR = 0
_VERSION_MINOR = 1
_MODULE_NAME   = 'configure_solr.py'


# setup tokenized field type
DATA1 = [
    {
        "add-field-type" : {
            "name":"searchText",
            "class":"solr.TextField",
            "positionIncrementGap":"100",
            "analyzer" : {
                "charFilters":[
                    {
                        "class":"solr.PatternReplaceCharFilterFactory",
                        "replacement":"$1$1",
                        "pattern":"([a-zA-Z])\\\\1+"
                    }
                ],
                "tokenizer":{
                    "class":"solr.WhitespaceTokenizerFactory"
                },
                "filters":[
                    {
                        "class":"solr.WordDelimiterFilterFactory",
                        "preserveOriginal":"0"
                    },
                    {
                        "class": "solr.LowerCaseFilterFactory"
                    }
                ]
            }
        }
    }
]

# standard fields
DATA2 = [
    {
        "add-field":{
            "name":"report_date",
            "type":"pdate",
            "indexed":"true",
            "stored":"true",
            "default":"NOW"
        }
    },
    {
        "add-field":{
            "name":"report_id",
            "type":"string",
            "indexed":"true",
            "stored":"true"
        }
    },
    {
        "add-field":{
            "name":"report_text",
            "type":"searchText",
            "indexed":"true",
            "stored":"true",
            "termPositions":"true",
            "termVectors":"true",
            "docValues":"false",
            "required":"true"
        }
    },
    {
        "add-field":{
            "name":"source",
            "type":"string",
            "indexed":"true",
            "stored":"true"
        }
    },
    {
        "add-field":{
            "name":"subject",
            "type":"string",
            "indexed":"true",
            "stored":"true"
        }
    },
    {
        "add-field":{
            "name":"report_type",
            "type":"string",
            "indexed":"true",
            "stored":"true"
        }
    },
    {
        "add-field":{
            "name":"signatureField",
            "type":"string",
            "stored":"true",
            "indexed":"true",
            "multiValued":"false"
        }
    }
]

# dynamic fields
DATA3 = [
    {
        "add-dynamic-field":{
            "name":"*_section",
            "type":"searchText",
            "indexed":"true",
            "stored":"false"
        }
    },
    {
        "add-dynamic-field":{
            "name":"*_id",
            "type":"plong",
            "indexed":"true",
            "stored":"true"
        }
    },
    {
        "add-dynamic-field":{
            "name":"*_ids",
            "type":"plongs",
            "multiValued":"true",
            "indexed":"true",
            "stored":"true"
        }
    },
    {
        "add-dynamic-field":{
            "name":"*_system",
            "type":"string",
            "indexed":"true",
            "stored":"true"
        }
    },
    {
        "add-dynamic-field":{
            "name":"*_attr",
            "type":"string",
            "indexed":"true",
            "stored":"true"
        }
    },
    {
        "add-dynamic-field":{
            "name":"*_attrs",
            "type":"strings",
            "multiValued":"true",
            "indexed":"true",
            "stored":"true"
        }
    }
]


###############################################################################
def _run_command(command):
    """
    Launch a subprocess to run the command; return the returncode and stderr.
    """

    cp = subprocess.run(command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True)
    
    return (cp.returncode, cp.stderr.lower())


###############################################################################
def _create_solr_core(core_name):
    """
    Create a new solr core with the given name. First delete the core if it
    exists, then recreate from scratch. This core is assumed to be for test
    purposes only.
    """

    command = ['solr', 'delete', '-c', core_name, '-deleteConfig', 'true']
    returncode, err_msg = _run_command(command)
    if 0 != returncode:
        # error if msg is something other than that the core doesn't exist
        if -1 == err_msg.find('cannot unload non-existent core'):
            print(err_msg)
            return False
    
    command = ['solr', 'create_core', '-c', core_name]
    returncode, err_msg = _run_command(command)
    if 0 != returncode:
        print(err_msg)
        return False
        
    return True


###############################################################################
def _ingest_file(core_name, filepath):
    """
    Use the Solr post tool to ingest the given sample file.
    """

    command = ['post', '-c', core_name, filepath]
    returncode, err_msg = _run_command(command)
    if 0 != returncode:
        print(err_msg)
        return False

    return True
    

###############################################################################
def _http_post(solr_url, headers, json_data, params=None):
    """
    Send an HTTP POST to the solr_url with the json_data and optional params.
    Return the complete response object.
    """

    try:
        if params is not None:
            r = requests.post(solr_url,
                              headers=headers,
                              params=params,
                              data=json_data)
        else:
            r = requests.post(solr_url,
                              headers=headers,
                              data=json_data)
    except requests.exceptions.HTTPError as e:
        print('\n*** HTTP error: "{0}" ***\n'.format(e))
    except requests.exceptions.ConnectionError as e:
        print('\n*** ConnectionError: "{0}" ***\n'.format(e))
    except requests.exceptions.Timeout as e:
        print('\n*** Timeout: "{0}" ***\n'.format(e))
    except requests.exceptions.RequestException as e:
        print('\n*** RequestException: "{0}" ***\n'.format(e))

    return r
    

###############################################################################
def _create_validation_files(solr_base_url):
    """
    Create and ingest test for ClarityNLP validation.
    """

    # special docs for validation purposes
    VALIDATION_FILES = ['data_validation0.txt']

    solr_url = '{0}/update'.format(solr_base_url)
    headers = {'Content-type':'application/json'}
    params = {'wt':'json', 'commit':'true'}
    
    for i in range(len(VALIDATION_FILES)):
        f = VALIDATION_FILES[i]
        # load file contents into a string
        with open(f, 'r') as infile:
            text = infile.read()

        # construct a JSON document with fields required by ClarityNLP
        
        # current datetime will be used as the timestamp
        now = datetime.datetime.utcnow().isoformat()

        report_type = 'CLARITYNLP_VALIDATION_{0}'.format(i)
        
        clarity_doc = {}
        clarity_doc['report_type'] = report_type
        clarity_doc['id'] = '{0}_{1}'.format(report_type, i)
        clarity_doc['report_id'] = clarity_doc['id']
        clarity_doc['source'] = report_type
        clarity_doc['report_date'] = now + 'Z'
        clarity_doc['subject'] = "-1"
        clarity_doc['report_text'] = text

        # solr requires an 'add' field with a 'doc' key equal to clarity_doc
        data = {'add': {'doc':clarity_doc} }

        # convert to json
        json_data = json.dumps(data, indent=4)

        # HTTP POST the JSON document to the test core
        r = _http_post(solr_url, headers, json_data, params)
        if 200 != r.status_code:
            print(r.text)
            return False

    return True
            

###############################################################################
def _configure_solr_schema(solr_base_url, obj_list):
    """
    Send data to solr via HTTP POST, check the response, and return True
    if successful or False otherwise.
    """

    solr_url = '{0}/schema'.format(solr_base_url)
    headers = {'Content-type':'application/json'}

    for payload in obj_list:
        json_data = json.dumps(payload)
        r = _http_post(solr_url, headers, json_data)
        
        if 200 != r.status_code:
            print(r.text)
            return False

    return True


###############################################################################
def _get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':

    # name of the ClarityNLP solr test core
    CORE_NAME = 'claritynlp_test'
    
    parser = argparse.ArgumentParser(
        description='Configure the ClarityNLP test core')
    parser.add_argument('-v', '--version', help='show version and exit',
                        action='store_true')
    parser.add_argument('-n', '--hostname',
                        help='hostname for solr instance, default == localhost')
    parser.add_argument('-p', '--port',
                        help='port number for solr instance, default == 8983')

    args = parser.parse_args()

    if 'version' in args and args.version:
        print(_get_version())
        sys.exit(0)

    hostname = 'localhost'
    if 'hostname' in args and args.hostname is not None:
        hostname = args.hostname

    port = 8983
    if 'port' in args and args.port is not None:
        port = int(args.port)

    solr_base_url = 'http://{0}:{1}/solr/{2}'.format(hostname, port, CORE_NAME)

    print('Configuring solr...')

    ok = _create_solr_core(CORE_NAME)
    if not ok:
        sys.exit(-1)
    print('\tcreated solr core "{0}"'.format(CORE_NAME))
    
    # setup custom field type
    ok = _configure_solr_schema(solr_base_url, DATA1)
    if not ok:
        print('\tcreation of "searchText" field type failed')
        sys.exit(-1)
    print('\tcreated the "searchText" field type')

    # add standard fields
    ok = _configure_solr_schema(solr_base_url, DATA2)
    if not ok:
        print('\tstandard field setup failed')
        sys.exit(-1)
    print('\tcreated standard fields')
        
    # add dynamic fields
    ok = _configure_solr_schema(solr_base_url, DATA3)
    if not ok:
        print('\tdynamic field setup failed')
        sys.exit(-1)
    print('\tcreated dynamic fields')

    # ingest test documents into Solr

    # construct path to ClarityNLP/utilities/nlp-solr, where the docs are
    cwd = os.getcwd()
    head, tail = os.path.split(cwd)
    assert head.lower().endswith('claritynlp')
    nlp_solr_dir = os.path.join(head, 'utilities', 'nlp-solr')

    print('Loading sample documents...')
    files = ['sample.csv', 'sample2.csv', 'sample3.csv', 'sample4.csv']
    for f in files:
        filepath = os.path.join(nlp_solr_dir, f)
        ok = _ingest_file(CORE_NAME, filepath)
        if not ok:
            print('\tload FAILED for file {0}'.format(filepath))
        else:
            print('\tloaded file {0}'.format(filepath))

    # create and ingest the validation files
    print('Loading validation files...')
    if not _create_validation_files(solr_base_url):
        print('\n\t*** Ingest failure for validation files ***')
    else:
        # run validation checks
        pass
            
    print('Finished!')
    
