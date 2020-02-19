# A custom task for running CQL queries via ClarityNLP.

import re
import os
import sys
import json
import argparse
import requests
from datetime import datetime
from pymongo import MongoClient

# modify path for local testing
if __name__ == '__main__':
    cur_dir = sys.path[0]
    nlp_dir, tail = os.path.split(cur_dir)
    sys.path.append(nlp_dir)
    sys.path.append(os.path.join(nlp_dir, 'tasks'))
    sys.path.append(os.path.join(nlp_dir, 'data_access'))

# ClarityNLP imports
import util
import data_access
import data_access.time_command as tc
from tasks.task_utilities import BaseTask
import data_access.cql_result_parser as crp
from claritynlp_logging import log, ERROR, DEBUG

    
_VERSION_MAJOR = 0
_VERSION_MINOR = 19

# set to True to enable debug output
_TRACE = True

# names of custom args accessible to CQLExecutionTask

_FHIR_VERSION          = 'fhir_version'            # "DSTU2" or "STU3"
_FHIR_CQL_EVAL_URL     = 'cql_eval_url'            # https://gt-apps.hdap.gatech.edu/cql/evaluate
_FHIR_PATIENT_ID       = 'patient_id'              # 
_FHIR_DATA_SERVICE_URI = 'fhir_data_service_uri'   # https://apps.hdap.gatech.edu/gt-fhir/fhir/
_FHIR_AUTH_TYPE        = 'fhir_auth_type'          # 
_FHIR_AUTH_TOKEN       = 'fhir_auth_token'         # 
_FHIR_TERMINOLOGY_SERVICE_URI      = 'fhir_terminology_service_uri'      # https://cts.nlm.nih.gov/fhir/
_FHIR_TERMINOLOGY_SERVICE_ENDPOINT = 'fhir_terminology_service_endpoint' # Terminology Service Endpoint
_FHIR_TERMINOLOGY_USER_NAME        = 'fhir_terminology_user_name'        # username
_FHIR_TERMINOLOGY_USER_PASSWORD    = 'fhir_terminology_user_password'    # password

_KEY_ERROR = 'error'

# time command custom args
_ARG_TIME_START = 'time_start'
_ARG_TIME_END   = 'time_end'

# value filter custom arg
_ARG_VALUE_FILTER = 'value_filter'

_KEY_RT          = 'resourceType'
_KEY_RES_DISP    = 'result_display'
_KEY_RESULT      = 'result'
_KEY_RESULT_TYPE = 'resultType'

_RT_PATIENT     = 'Patient'
_RT_ENCOUNTER   = 'Encounter'
_RT_OBSERVATION = 'Observation'
_RT_PROCEDURE   = 'Procedure'
_RT_CONDITION   = 'Condition'
_RT_MED_STMT    = 'MedicationStatement'
_RT_MED_ORDER   = 'MedicationOrder'
_RT_MED_ADMIN   = 'MedicationAdministration'

_RESULT_TYPE_DT  = 'datetime'


###############################################################################
def _sort_by_datetime_desc(result_list):
    """
    Sort the namedtuples from cql_result_parser by datetime from most recent
    to least recent.
    """

    patient_list     = []
    datetime_list    = []
    no_datetime_list = []
    for i, obj in enumerate(result_list):
        if _KEY_RT in obj:
            resource_type = obj[_KEY_RT]
            if _RT_PATIENT == resource_type:
                # patient has no date_time field
                patient_list.append(i)
            else:
                dt = getattr(obj, crp.KEY_DATE_TIME, None)
                if dt is not None:
                    datetime_list.append( (dt, i) )
                else:
                    no_datetime_list.append(i)
        elif _KEY_RESULT_TYPE in obj:
            result_type = obj[_KEY_RESULT_TYPE]
            dt = getattr(obj, crp.KEY_DATE_TIME, None)
            if dt is not None:
                datetime_list.append( (dt, i) )
            else:
                no_datetime_list.append(i)
            
    datetime_list = sorted(datetime_list, key=lambda x: x[0], reverse=True)

    earliest = None
    latest   = None
    if len(datetime_list) > 0:
        earliest = datetime_list[-1][0]
        latest   = datetime_list[0][0]

    # build new time-sorted result list
    new_results = []

    # patients go first
    for index in patient_list:
        new_results.append(result_list[index])

    # then any results lacking timestamps
    for index in no_datetime_list:
        new_results.append(result_list[index])

    # then sorted timestamped results
    for obj, index in datetime_list:
        new_results.append(result_list[index])
    
    assert len(new_results) == len(result_list)
    return (new_results, earliest, latest)


###############################################################################
def _json_to_objs(json_obj):
    """
    Decode the data returned by the CQLEngine and sort it by timestamp from
    most recent to least recent.
    """

    if _TRACE:
        log('CQLExecutionTask: Calling _json_to_objs...')

    KEY_RESULT_TYPE = 'resultType'
        
    results = []

    # assumes we either have a list of objects or a single obj
    obj_type = type(json_obj)
    
    if list == obj_type:
        if _TRACE:
            log('\tfound list of length {0}'.format(len(json_obj)))
        for e in json_obj:
            # skip if no resultType key
            if KEY_RESULT_TYPE not in e:
                continue
            if _TRACE:
                log('\t\tdecoding resource type {0}'.format(e['resultType']))
            result_obj = crp.decode_top_level_obj(e)
            if result_obj is None:
                continue
            if list is not type(result_obj):
                results.append(result_obj)
            else:
                results.extend(result_obj)
    elif dict == obj_type:
        if _TRACE:
            log('\tfound dict of size {0}'.format(len(json_obj)))
        result_obj = crp.decode_top_level_obj(json_obj)
        if result_obj is not None:
            if list is not type(result_obj):
                results.append(result_obj)
            else:
                results.extend(result_obj)

    if _TRACE:
        log('\tThere are {0} results after top-level decode'.
              format(len(results)))
                
    if 0 == len(results):
        return (results, None, None)
                
    # check for presence of the 'error' key in the Patient resource
    # if present, FHIR server returned no useful data
    for obj in results:
        if _KEY_RT in obj:
            resource_type = obj[_KEY_RT]
            if _RT_PATIENT == resource_type:
                if _KEY_ERROR in obj:
                    log('\n*** CQLExecutionTask: ERROR KEY FOUND IN PATIENT RESOURCE ***\n')
                    return (None, None, None)
                
    # sort by datetime from most to least recent
    # element[0] is the patient resource
    results, earliest, latest = _sort_by_datetime_desc(results)

    return (results, earliest, latest)


###############################################################################
def _to_result_obj(obj):
    """
    Insert the 'result_display' information and build the object to be written
    to MongoDB.
    """

    # if _TRACE:
    log('Calling _to_result_obj...')
    log('obj: ')
    log(obj)
    log()

    codesys_map = {
        'http://snomed.info/ct':'SNOMED',
        'http://snomed.info/sct':'SNOMED',
        'http://www.nlm.nih.gov/research/umls/rxnorm':'RXNORM',
        'http://loinc.org':'LOINC',
        'http://www.ama-assn.org/go/cpt':'CPT',
        'http://hl7.org/fhir/sid/icd-9-cm':'ICD-9',
        'http://hl7.org/fhir/sid/icd-10':'ICD-10',
        'http://hl7.org/fhir/sid/icd-10-nl':'ICD-10',
        'http://hl7.org/fhir/sid/icd-10-cm':'ICD-10'
    }
        
    KEY_RC = 'result_content'
    KEY_CODE = 'code_coding_0_code'
    KEY_CODESYS = 'code_coding_0_system'

    if _KEY_RT not in obj:
        # primitive type
        assert _KEY_RESULT_TYPE in obj
        result_type = obj[_KEY_RESULT_TYPE].lower()
        result_str = ''
        if _KEY_RESULT in obj:
            result = obj[_KEY_RESULT]

            # convert datetime objects to string
            if datetime is type(result):
                result_str = result.isoformat()
            else:
                result_str = result
            
        result_display_obj = {
            'date': '',
            'result_content':result_str,
            'sentence': '',
            'highlights':[result_str]
        }

        # set the date field for dateType types
        if _RESULT_TYPE_DT == result_type:
            result_display_obj['date'] = result_str

        obj[_KEY_RES_DISP] = result_display_obj
        return obj
    
    # insert the display/formatting info
    assert _KEY_RT in obj
    resource_type = obj[_KEY_RT]

    value_name = ''
    if crp.KEY_VALUE_NAME in obj:
        value_name = obj[crp.KEY_VALUE_NAME]
    date = 'UNKNOWN'
    if crp.KEY_DATE_TIME in obj:
        date = obj[crp.KEY_DATE_TIME]

    result_display_obj = {
        'date':date,
        #'result_content':'{0}: {1}'.format(resource_type, value_name),
        #'result_content':'{0}\n{1}'.format(value_name, codesys),
        'result_content':'{0}'.format(value_name),
        'sentence':'',
        'highlights':[value_name]
    }
        
    if _RT_PATIENT == resource_type:
        if 'birthDate' in obj:
            date = obj['birthDate']
        result_display_obj['date'] = date
        result_display_obj[KEY_RC] = 'Patient: {0}, DOB: {1}'.format(value_name, date)

    elif _RT_CONDITION == resource_type:
        codesys = ''
        if KEY_CODESYS in obj:
            codesys_url = obj[KEY_CODESYS]
            if codesys_url in codesys_map:
                codesys = codesys_map[codesys_url]
            else:
                codesys = codesys_url
        code = ''
        if KEY_CODE in obj:
            code = obj[KEY_CODE]

        result_display_obj[KEY_RC] = '{0}\n{1}: {2}'.format(value_name, codesys, code)
            
    elif _RT_ENCOUNTER == resource_type:
        identifier = ''
        subject_ref = ''
        name = ''
        if 'id' in obj:
            identifier = obj['id']
        if 'subject_reference' in obj:
            subject_ref = obj['subject_reference']
        if 'subject_display' in obj:
            name = obj['subject_display']
        value = 'Encounter {0} for {1}'.format(identifier, subject_ref)
        if len(name) > 0:
            value += '\n{0}'.format(name)
        result_display_obj[KEY_RC] = value
        
    elif _RT_OBSERVATION == resource_type:
        value = ''
        units = ''
        if crp.KEY_VALUE in obj:
            # sometimes a value is not present in an observation
            value = obj[crp.KEY_VALUE]
        #if crp.KEY_UNITS in obj:
        #    units = obj[crp.KEY_UNITS]
        if 'valueQuantity_code' in obj:
            units = obj['valueQuantity_code']
        #result_display_obj[KEY_RC] = '{0}: {1} {2}'.format(value_name, value, units)
        #result_display_obj['highlights']:[value_name, value, units]
        result_display_obj[KEY_RC] = '{0} {1}'.format(value, units)
        result_display_obj['highlights']:[value, units]
        
        # explicitly set report_text field for Observation resources
        obj['report_text'] = '{0}: {1} {2}'.format(value_name, value, units)
        
    elif _RT_MED_STMT == resource_type:
        if 'effectiveDateTime' in obj:
            date = obj['effectiveDateTime']
        elif 'effectivePeriod_start' in obj:
            start = obj['effectivePeriod_start']
            date = '{0}'.format(start)
            #if 'effectivePeriod_end' in obj:
            #    end = obj['effectivePeriod_end']
            #    date += ' to {0}'.format(end)
        result_display_obj['date'] = date
        
    elif _RT_MED_ORDER == resource_type:       
        if 'dateWritten' in obj:
            date = obj['dateWritten']
        if 'dateEnded' in obj:
            end = obj['dateEnded']
            date += ' to {0}'.format(end)
        result_display_obj['date'] = date
        
    elif _RT_MED_ADMIN == resource_type:
        if 'effectiveDateTime' in obj:
            date = obj['effectiveDateTime']
        elif 'effectivePeriod_start' in obj:
            start = obj['effectivePeriod_start']
            date = '{0}'.format(start)
            if 'effectivePeriod_end' in obj:
                end = obj['effectivePeriod_end']
                date += ' to {0}'.format(end)
        result_display_obj['date'] = date

    obj[_KEY_RES_DISP] = result_display_obj

    return obj


###############################################################################
def _get_custom_arg(str_key, str_variable_name, job_id, custom_arg_dict):
    """
    Extract a value at the given key from the given dict, or return None
    if not found. Attempt to read from environmental variables, if known.
    """

    value = None
    if str_key in custom_arg_dict:
        value = custom_arg_dict[str_key]

    if value is None:
        if str_key in util.properties:
            value = util.properties[str_key]

    # treat empty strings as None
    if str == type(value) and 0 == len(value):
        value = None
            
    # echo in job status and in log file
    msg = 'CQLExecutionTask: {0} == {1}'.format(str_variable_name, value)
    data_access.update_job_status(job_id,
                                  util.conn_string,
                                  data_access.IN_PROGRESS,
                                  msg)
    # write msg to log file
    log(msg)
    
    return value


###############################################################################
def _get_datetime_window(custom_args, data_earliest, data_latest):
    """
    Extract and parse the datetime_start and datetime_end custom
    arguments. These specify the start/end datetime filters for the CQL
    results.
    """

    datetime_start = None
    datetime_end = None    
    
    if _ARG_TIME_START in custom_args:
        time_start = custom_args[_ARG_TIME_START]
        datetime_start = tc.parse_time_command(time_start,
                                               data_earliest,
                                               data_latest)
        
    if _ARG_TIME_END in custom_args:
        time_end = custom_args[_ARG_TIME_END]
        datetime_end = tc.parse_time_command(time_end,
                                             data_earliest,
                                             data_latest)

    if _TRACE:
        log('\n*** datetime_start: {0}'.format(datetime_start))
        log('***   datetime_end: {0}'.format(datetime_end))
        
    return (datetime_start, datetime_end)


###############################################################################
def _apply_datetime_filter(samples, t0, t1):
    """
    Remove any samples outside of the specified start and end times.
    The 'samples' parameter is a list of namedtuples from the CQL result
    parser module.
    """

    if _TRACE:
        log('CQLExecutionTask: calling _apply_datetime_filter...')
        log('\tt0: {0}, t1: {0}'.format(t0, t1))
        log('\tlength of samples list: {0}'.format(len(samples)))

    if 0 == len(samples):
        return []
    
    results = []
    for s in samples:

        # Timestamps from the relevant FHIR resources have been mapped to
        # the 'date_time' field by the cql_result_parser.
        t = getattr(s, crp.KEY_DATE_TIME, None)
        if t is None:
            # no timestamp in this sample
            results.append(s)
            continue
        if t0 is not None and t < t0:
            continue
        if t1 is not None and t > t1:
            continue

        results.append(s)

    return results


###############################################################################
def _apply_value_filter(str_value_filter, result_list):
    """
    Apply the value filter to the result list and return any survivors.
    """

    str_op = str_value_filter.lower()
    
    filter_value = None
    filter_result = None
    
    if str_op.startswith('min'):
        # find minimum value of all results with a 'value' field
        for r in result_list:
            if crp.KEY_VALUE in r:
                val = r[crp.KEY_VALUE]
                if filter_value is None or val < filter_value:
                    filter_value = val
                    filter_result = r
    elif str_op.startswith('max'):
        # find max value of all results with a 'value' field
        for r in result_list:
            if crp.KEY_VALUE in r:
                val = r[crp.KEY_VALUE]
                if filter_value is None or val > filter_value:
                    filter_value = val
                    filter_result = r

    if filter_result is None:
        # no filterable values were found, so return original list
        return result_list
    else:
        return [filter_result]
                

###############################################################################
class CQLExecutionTask(BaseTask):
    
    task_name = "CQLExecutionTask"

    # VERY IMPORTANT to prevent parallel execution of this task, to avoid
    # sending lots of identical HTTP POSTs to the CQL Engine
    parallel_task = False
        
    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        
        job_id = str(self.job)

        # get the FHIR Version
        fhir_version = _get_custom_arg(_FHIR_VERSION,
                                       'fhir_version',
                                       job_id,
                                       self.pipeline_config.custom_arguments)
        if fhir_version is None:
            log('\n*** CQLExecutionTask: using fhir_version == STU3 ***')
            fhir_version = "STU3"

        fhir_version = fhir_version.lower()
        if not fhir_version.endswith('stu2') and not fhir_version.endswith('stu3'):
            log('\n*** CQLExecutionTask: fhir_version "{0}" is invalid ***'.
                  format(fhir_version))
            return

        # URL of the FHIR server's CQL evaluation endpoint
        cql_eval_url = _get_custom_arg(_FHIR_CQL_EVAL_URL,
                                       'cql_eval_url',
                                       job_id,
                                       self.pipeline_config.custom_arguments)
        if cql_eval_url is None:
            log('\n*** CQLExecutionTask: no cql_eval_url was found ***\n')
            return

        patient_id = _get_custom_arg(_FHIR_PATIENT_ID,
                                     'patient_id',
                                     job_id,
                                     self.pipeline_config.custom_arguments)
        if patient_id is None:
            log('\n*** CQLExecutionTask: no patient_id was found ***\n')
            return

        # patient_id must be a string
        patient_id = str(patient_id)

        # CQL code string verbatim from CQL file
        cql_code = self.pipeline_config.cql
        log('\n*** CQL CODE: ***\n')
        log(cql_code)
        log()
        if cql_code is None or 0 == len(cql_code):
            log('\n*** CQLExecutionTask: no CQL code was found ***\n')
            return

        # fhir_terminology_service_endpoint = _get_custom_arg(_FHIR_TERMINOLOGY_SERVICE_ENDPOINT,
        #                                                     'fhir_terminology_service_endpoint',
        #                                                     job_id,
        #                                                     self.pipeline_config.custom_arguments)

        # if fhir_terminology_service_endpoint is None:
        #     return

        fhir_data_service_uri = _get_custom_arg(_FHIR_DATA_SERVICE_URI,
                                                'fhir_data_service_uri',
                                                job_id,
                                                self.pipeline_config.custom_arguments)

        if fhir_data_service_uri is None:
            log('\n*** CQLExecutionTask: fhir_data_service is None ***')
            return

        # ensure '/' termination
        if not fhir_data_service_uri.endswith('/'):
                fhir_data_service_uri += '/'

        # initialize payload
        payload = {
            # the requests lib will properly escape the raw string
            "fhirVersion":fhir_version,
            "code":cql_code,
            #"fhirServiceUri":fhir_terminology_service_endpoint,
            "dataServiceUri":fhir_data_service_uri,
            "patientId":patient_id,
        }

        fhir_auth_type = _get_custom_arg(_FHIR_AUTH_TYPE,
                                         'fhir_auth_type',
                                         job_id,
                                         self.pipeline_config.custom_arguments)

        fhir_auth_token = _get_custom_arg(_FHIR_AUTH_TOKEN,
                                          'fhir_auth_token',
                                          job_id,
                                          self.pipeline_config.custom_arguments)

        # setup the request header; add authentication if credentials provided
        headers = {
            'Content-Type':'application/json; charset=utf-8',
            'Accept':'application/json; charset=utf-8'
        }

        if fhir_auth_type is not None and fhir_auth_token is not None:
            if len(fhir_auth_type) > 0 and len(fhir_auth_token) > 0:
                headers['Authorization'] = '{0} {1}'.format(fhir_auth_type, fhir_auth_token)

        # # params for UMLS OID code lookup
        # fhir_terminology_service_uri = _get_custom_arg(_FHIR_TERMINOLOGY_SERVICE_URI,
        #                                                'fhir_terminology_service_uri',
        #                                                job_id,
        #                                                self.pipeline_config.custom_arguments)
        # # ensure '/' termination
        # if fhir_terminology_service_uri is not None:
        #     if not fhir_terminology_service_uri.endswith('/'):
        #         fhir_terminology_service_uri += '/'

        # fhir_terminology_user_name = _get_custom_arg(_FHIR_TERMINOLOGY_USER_NAME,
        #                                              'fhir_terminology_user_name',
        #                                              job_id,
        #                                              self.pipeline_config.custom_arguments)

        # fhir_terminology_user_password = _get_custom_arg(_FHIR_TERMINOLOGY_USER_PASSWORD,
        #                                                  'fhir_terminology_user_password',
        #                                                  job_id,
        #                                                  self.pipeline_config.custom_arguments)

        # # setup terminology server capability
        # if fhir_terminology_service_uri is not None and \
        #    fhir_terminology_user_name is not None and fhir_terminology_user_name != 'username' and \
        #    fhir_terminology_user_password is not None and fhir_terminology_user_password != 'password':
        #     payload['terminologyServiceUri'] = fhir_terminology_service_uri
        #     payload['terminologyUser'] = fhir_terminology_user_name
        #     payload['terminologyPass'] = fhir_terminology_user_password

        # perform the request here, catch lots of different exceptions

        log('\n*** CQLExecutionTask: Request ***')
        log('Headers: ')
        for k,v in headers.items():
            log('\t{0} => {1}'.format(k,v))
        log('Payload: ')
        for k,v in payload.items():
            log('\t{0} => {1}'.format(k,v))
        log()

        has_error = False
        r = None
        try:
            r = requests.post(cql_eval_url,
                              headers=headers,
                              data=json.dumps(payload, indent=4))

        except requests.exceptions.HTTPError as e:
            log('\n*** CQLExecutionTask HTTP error: "{0}" ***\n'.format(e))
            has_error = True
        except requests.exceptions.ConnectionError as e:
            log('\n*** CQLExecutionTask ConnectionError: "{0}" ***\n'.format(e))
            has_error = True
        except requests.exceptions.Timeout as e:
            log('\n*** CQLExecutionTask Timeout: "{0}" ***\n'.format(e))
            has_error = True
        except requests.exceptions.RequestException as e:
            log('\n*** CQLEXecutionTask RequestException: "{0}" ***\n'.format(e))
            has_error = True

        if has_error:
            log('HTTP error, terminating CQLExecutionTask...')
            if r:
                log('RESPONSE CONTENT')
                log(r.content)
                log('RESPONSE HEADERS')
                log(r.headers)
            return

        log('Response status code: {0}'.format(r.status_code))

        results = None
        if 200 == r.status_code:
            if _TRACE:
                log('\n*** CQL JSON RESULTS ***\n')
                log(r.json())
                log()

            # data_earliest == earliest datetime in the data
            # data_latest   == latest datetime in the data
            results, data_earliest, data_latest = _json_to_objs(r.json())
            log('\tCQLExecutionTask: found {0} results'.format(len(results)))
        else:
            log('\n*** CQLExecutionTask: HTTP status code {0} ***\n'.format(r.status_code))
            return

        if results is None or (0 == len(results)):
            return

        # parse datetime_start, datetime_end time commands, if any, and
        # filter data to specified time window
        datetime_start, datetime_end = _get_datetime_window(
            self.pipeline_config.custom_arguments,
            data_earliest,
            data_latest
        )

        # remove results outside of the desired time window
        results = _apply_datetime_filter(results, datetime_start, datetime_end)
        log('\n*** CQLExecutionTask: {0} results after time filtering. ***'.
              format(len(results)))

        # get the value filter custom arg, if any
        str_value_filter = _get_custom_arg(_ARG_VALUE_FILTER,
                                           'value_filter',
                                           job_id,
                                           self.pipeline_config.custom_arguments)

        if str_value_filter is not None:
            results = _apply_value_filter(str_value_filter, results)
        
        for obj in results:

            if obj is None:
                continue

            # construct result object and write to MongoDB
            mongo_obj = _to_result_obj(obj)
            self.write_result_data(temp_file, mongo_client, None, mongo_obj)


###############################################################################
if __name__ == '__main__':

    # for command-line testing only
    
    parser = argparse.ArgumentParser(
        description='test CQL Engine result decoding locally')

    parser.add_argument('-f', '--filepath',
                        help='path to JSON file containing CQL Engine results')

    parser.add_argument('--debug',
                        action='store_true',
                        help='print debugging information')

    args = parser.parse_args()

    filpath = None
    if 'filepath' in args and args.filepath:
        filepath = args.filepath
        if not os.path.isfile(filepath):
            print('Unknown file specified: "{0}"'.format(filepath))
            sys.exit(-1)

    if 'debug' in args and args.debug:
        crp.enable_debug()
        
    with open(filepath, 'rt') as infile:
        json_string = infile.read()
        json_data = json.loads(json_string)

        results, data_earliest, data_latest = _json_to_objs(json_data)
        print('\tfound {0} results'.format(len(results)))
        if results is not None:


            # str_value_filter = 'MIN()'
            # if str_value_filter is not None:
            #     results = _apply_value_filter(str_value_filter, results)
            #     print('filtered to {0} results'.format(len(results)))

            
            for counter, obj in enumerate(results):
                
                if obj is None:
                    continue

                mongo_obj = _to_result_obj(obj)

                # print to stdout
                print('RESULT {0}'.format(counter))
                for k,v in mongo_obj.items():
                    if dict == type(v):
                        print('\t{0}'.format(k))
                        for k2,v2 in v.items():
                            print('\t\t{0} => {1}'.format(k2, v2))
                    else:
                        print('\t{0} => {1}'.format(k,v))
