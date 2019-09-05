# A custom task for running CQL queries via ClarityNLP.

import re
import os
import sys
import json
import argparse
import requests
import multiprocessing
from datetime import datetime
from pymongo import MongoClient

# modify path for local testing
if __name__ == '__main__':
    cur_dir = sys.path[0]
    nlp_dir, tail = os.path.split(cur_dir)
    sys.path.append(nlp_dir)
    sys.path.append(os.path.join(nlp_dir, 'tasks'))
    sys.path.append(os.path.join(nlp_dir, 'data_acess'))

# ClarityNLP imports
import util
import data_access
import data_access.time_command as tc
from tasks.task_utilities import BaseTask
import data_access.cql_result_parser as crp
    
_VERSION_MAJOR = 0
_VERSION_MINOR = 9

# names of custom args accessible to CQLExecutionTask

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

# number of unique task indices among all Luigi clones of this task
_MAX_TASK_INDEX = 1024

# Array for coordinating clones of this task, all initialized to -1.
_shared_array = multiprocessing.Array('i', [-1]*_MAX_TASK_INDEX)

# time command custom args
_ARG_TIME_START = 'time_start'
_ARG_TIME_END   = 'time_end'


###############################################################################
def _atomic_check(task_index):
    """
    Given the task index (a user-defined param of the task), check the shared
    array element at that index. If it is -1, this is the first time that value
    for the task_index has been seen. In this case, write the task index into
    the shared array and return the task index to the caller. Otherwise 
    return -1.
    """

    global _shared_array

    assert task_index >= 0
    assert task_index < _MAX_TASK_INDEX

    return_val = -1
    with _shared_array.get_lock():
        elt_val = _shared_array[task_index]
        if -1 == elt_val:
            # first time to see this value of the task index
            _shared_array[task_index] = task_index
            return_val = task_index

    return return_val


###############################################################################
def _sort_by_datetime_desc(result_list):
    """
    Sort the namedtuples from cql_result_parser by datetime from most recent
    to least recent.
    """

    patient_list = []
    procedure_list = []
    condition_list = []
    observation_list = []
    medication_request_list = []
    medication_statement_list = []

    # build list of (datetime_obj, index) from each type of namedtuple
    for i in range(len(result_list)):
        obj = result_list[i]
        if obj is None:
            print('\n\n******* CQLExecutionTask: OBJ IS NONE ******\n\n')
        
        if isinstance(obj, crp.ObservationResource):
            dt = getattr(obj, 'date_time', None)
            assert dt is not None
            observation_list.append( (dt, i) )
        elif isinstance(obj, crp.ConditionResource):
            dt = getattr(obj, 'date_time', None)
            assert dt is not None
            condition_list.append( (dt, i) )
        elif isinstance(obj, crp.ProcedureResource):
            dt = getattr(obj, 'date_time', None)
            assert dt is not None
            procedure_list.append( (dt, i) )
        elif isinstance(obj, crp.MedicationStatementResource):
            dt = getattr(obj, 'date_time', None)
            assert dt is not None
            medication_statement_list.append( (dt, i) )
        elif isinstance(obj, crp.MedicationRequestResource):
            dt = getattr(obj, 'date_time', None)
            assert dt is not None
            medication_request_list.append( (dt, i) )
        elif isinstance(obj, crp.PatientResource):
            # patient has no date_time
            patient_list.append( (obj, i) )
        else:
            print('\n*** CQLExecutionTask _sort_by_datetime_desc: ***')
            print('  *** unknown namedtuple: {0} ***\n'.format(obj))
            return result_list

    assert 1 == len(patient_list)
        
    # sort each by datetime in descending order of date
    # only a single list, if any, should have nonzero length, since the FHIR
    # data is either {patient, observation+}, {patient, condition+}, or
    # {patient, procedure+}
    nonzero_count = 0
    the_list = None
    if len(observation_list) > 0:
        nonzero_count += 1
        observation_list = sorted(observation_list, key=lambda x: x[0], reverse=True)
        the_list = observation_list
    if len(condition_list) > 0:
        nonzero_count += 1
        condition_list = sorted(condition_list, key=lambda x: x[0], reverse=True)
        the_list = condition_list
    if len(procedure_list) > 0:
        nonzero_count += 1
        procedure_list = sorted(procedure_list, key=lambda x: x[0], reverse=True)
        the_list = procedure_list
    if len(medication_statement_list) > 0:
        nonzero_count += 1
        medication_statement_list = sorted(medication_statement_list,
                                           key=lambda x: x[0],
                                           reverse=True)
        the_list = medication_statement_list
    if len(medication_request_list) > 0:
        nonzero_count += 1
        medication_request_list = sorted(medication_request_list,
                                         key=lambda x: x[0],
                                         reverse=True)
        the_list = medication_request_list
        
    if nonzero_count > 1:
        print('\n *** CQLExecutionTask: found multiple FHIR resources ***\n')
        assert nonzero_count <= 1
    else:
        # extract earliest and latest datetimes
        earliest = the_list[-1][0]
        latest = the_list[0][0]
        
    # read out each element in order to assemble sorted list
    # put patient data in front
    new_results = []
    for obj, index in patient_list:
        new_results.append(result_list[index])
    for dt,index in procedure_list:
        new_results.append(result_list[index])
    for dt, index in condition_list:
        new_results.append(result_list[index])
    for dt, index in observation_list:
        new_results.append(result_list[index])
    for dt, index in medication_statement_list:
        new_results.append(result_list[index])
    for dt, index in medication_request_list:
        new_results.append(result_list[index])

    assert len(new_results) == len(result_list)
    return (new_results, earliest, latest)
    

###############################################################################
def _json_to_objs(json_obj):
    """
    Convert the JSON returned by the FHIR server to namedtuples.
    """

    results = []

    # assumes we either have a list of objects or a single obj
    obj_type = type(json_obj)
    if list == obj_type:
        for e in json_obj:
            result_obj = crp.decode_top_level_obj(e)
            if result_obj is None:
                continue
            if list is not type(result_obj):
                results.append(result_obj)
            else:
                results.extend(result_obj)
    elif dict == obj_type:
        result_obj = crp.decode_top_level_obj(json_obj)
        if result_obj is not None:
            if list is not type(result_obj):
                results.append(result_obj)
            else:
                results.extend(result_obj)

    if 0 == len(results):
        return (None, None, None)
                
    # check for presence of the 'error' key in the patient resource
    # if present, FHIR server returned no useful data
    for r in results:
        if isinstance(r, crp.PatientResource):
            if _KEY_ERROR in r:
                print('\n*** CQLExecutionTask: ERROR KEY FOUND IN PATIENT RESOURCE ***\n')
                return (None, None, None)
                
    # sort by datetime from most to least recent
    # element[0] is the patient resource
    results, earliest, latest = _sort_by_datetime_desc(results)

    return (results, earliest, latest)


###############################################################################
def _extract_coding_systems_list(obj, mongo_obj, prefix):
    """
    Extract the list of (code, system, display) tuples.
    """
    
    coding_systems_list = getattr(obj, 'coding_systems_list', None)
    if coding_systems_list is None:
        return
    
    counter = 1
    for coding_obj in coding_systems_list:
        mongo_obj['{0}_codesys_code_{1}'.format(prefix, counter)] = coding_obj.code
        mongo_obj['{0}_codesys_system_{1}'.format(prefix, counter)] = coding_obj.system
        mongo_obj['{0}_codesys_display_{1}'.format(prefix, counter)] = coding_obj.display
        if 1 == counter:
            # set the 'source' field to match coding_obj.display
            mongo_obj['source'] = coding_obj.display
        counter += 1


###############################################################################
def _extract_patient_resource(obj, mongo_obj):
    """
    Extract data from the FHIR patient resource and load into mongo dict.
    """

    assert isinstance(obj, crp.PatientResource)

    if _KEY_ERROR in obj:
        # no data returned
        return

    # patient id is in the 'subject' field
    patient_id = getattr(obj, 'subject', None)
    mongo_obj['patient_subject'] = patient_id

    # get the list of (first_name, last_name) tuples and create numbered fields
    name_list = getattr(obj, 'name_list', None)
    if name_list is not None:
        counter = 1
        for first, last in name_list:
            key_fname = 'patient_fname_{0}'.format(counter)
            key_lname = 'patient_lname_{0}'.format(counter)
            mongo_obj[key_fname] = first
            mongo_obj[key_lname] = last
            counter += 1

    gender = getattr(obj, 'gender', None)
    mongo_obj['patient_gender'] = gender

    dob = getattr(obj, 'date_of_birth', None)
    dob_str = None
    if dob is not None:
        dob_str = dob.isoformat()
    mongo_obj['patient_date_of_birth'] = dob_str


###############################################################################
def _extract_procedure_resource(obj, mongo_obj):
    """
    Extract data from the FHIR procedure resource and load into mongo dict.
    """

    assert isinstance(obj, crp.ProcedureResource)

    if _KEY_ERROR in obj:
        # no data returned
        return

    id_value = getattr(obj, 'id_value', None)
    mongo_obj['procedure_id_value'] = id_value

    status = getattr(obj, 'status', None)
    mongo_obj['procedure_status'] = status

    _extract_coding_systems_list(obj, mongo_obj, 'procedure')

    subject_ref = getattr(obj, 'subject_reference', None)
    mongo_obj['procedure_subject_ref'] = subject_ref

    subject_display = getattr(obj, 'subject_display', None)
    mongo_obj['procedure_subject_display'] = subject_display

    context_ref = getattr(obj, 'context_reference', None)
    mongo_obj['procedure_context_ref'] = context_ref

    dt = getattr(obj, 'date_time', None)
    dt_string = None
    if dt is not None:
        dt_string = dt.isoformat()
    mongo_obj['datetime'] = dt_string

    # add display/formatting info
    procedure_name = mongo_obj['procedure_codesys_display_1']
    result_display_obj = {
        'date': mongo_obj['datetime'],
        'result_content':'Procedure: {0}'.format(procedure_name),
        'sentence':'',
        'highlights': [procedure_name]
    }
    mongo_obj['result_display'] = result_display_obj


###############################################################################
def _extract_condition_resource(obj, mongo_obj):
    """
    Extract dta from the FHIR condition resource and load into mongo dict.
    """

    assert isinstance(obj, crp.ConditionResource)

    if _KEY_ERROR in obj:
        # no data returned
        return

    id_value = getattr(obj, 'id_value', None)
    mongo_obj['condition_id_value'] = id_value

    category_list = getattr(obj, 'category_list', None)
    if category_list is not None:
        counter = 1
        for elt in category_list:
            if isinstance(elt, crp.CodingObj):
                mongo_obj['condition_category_code_{0}'.format(counter)] = elt.code
                mongo_obj['condition_category_system_{0}'.format(counter)] = elt.system
                mongo_obj['condition_category_display_{0}'.format(counter)] = elt.display
                counter += 1

    _extract_coding_systems_list(obj, mongo_obj, 'condition')
        
    subject_ref = getattr(obj, 'subject_reference', None)
    mongo_obj['condition_subject_ref'] = subject_ref

    subject_display = getattr(obj, 'subject_display', None)
    mongo_obj['condition_subject_display'] = subject_display

    context_ref = getattr(obj, 'context_reference', None)
    mongo_obj['condition_context_ref'] = context_ref

    date_time = getattr(obj, 'date_time', None)
    dt_string = None
    if date_time is not None:
        dt_string = date_time.isoformat()
    mongo_obj['datetime'] = dt_string
    
    end_date_time = getattr(obj, 'end_date_time', None)
    dt_string = None
    if end_date_time is not None:
        dt_string = end_date_time.isoformat()
    mongo_obj['end_datetime'] = dt_string

    # add display/formatting info
    condition_name = mongo_obj['condition_codesys_display_1']
    result_display_obj = {
        'date': mongo_obj['datetime'],
        'result_content':'Condition: {0}, onset: {1}, abatement: {2}'.format(
            condition_name, mongo_obj['datetime'], mongo_obj['end_datetime']),
        'sentence':'',
        'highlights':[condition_name]
    }
    mongo_obj['result_display'] = result_display_obj
    

###############################################################################
def _extract_observation_resource(obj, mongo_obj):
    """
    Extract data from the FHIR observation resource and load into mongo dict.
    """

    assert isinstance(obj, crp.ObservationResource)

    if _KEY_ERROR in obj:
        # no data returned
        return

    subject_ref = getattr(obj, 'subject_reference', None)

    # The subject_ref has the form Patient/9940, where the number after the
    # fwd slash is the patient ID. Extract this ID and store in the 'subject'
    # field.
    if subject_ref is not None:
        assert '/' in subject_ref
        text, num = subject_ref.split('/')
        mongo_obj['subject'] = num
    mongo_obj['obs_subject_ref'] = subject_ref

    subject_display = getattr(obj, 'subject_display', None)
    mongo_obj['obs_subject_display'] = subject_display

    context_ref = getattr(obj, 'context_reference', None)
    mongo_obj['obs_context_ref'] = context_ref

    date_time = getattr(obj, 'date_time', None)
    dt_string = None
    if date_time is not None:
        dt_string = date_time.isoformat()
    mongo_obj['datetime'] = dt_string
    
    value = getattr(obj, 'value', None)
    if value is not None:
        # store this in the 'value' field also
        mongo_obj['value'] = value
    mongo_obj['obs_value'] = value

    unit = getattr(obj, 'unit', None)
    mongo_obj['obs_unit'] = unit

    unit_system = getattr(obj, 'unit_system', None)
    mongo_obj['obs_unit_system'] = unit_system

    unit_code = getattr(obj, 'unit_code', None)
    mongo_obj['obs_unit_code'] = unit_code

    _extract_coding_systems_list(obj, mongo_obj, 'obs')

    # add display/formatting info
    value_name = mongo_obj['obs_codesys_display_1']
    units = mongo_obj['obs_unit_code']
    result_display_obj = {
        'date': mongo_obj['datetime'],
        'result_content':'{0}: {1} {2}'.format(value_name, value, units),
        'sentence':'',
        'highlights':[value_name, value, units]
    }
    mongo_obj['result_display'] = result_display_obj
    

###############################################################################
def _extract_medication_statement_resource(obj, mongo_obj):
    """
    Extract data from the FHIR MedicationStatement resource and load into
    mongo dict.
    """

    assert isinstance(obj, crp.MedicationStatementResource)

    if _KEY_ERROR in obj:
        # no data returned
        return

    id_value = getattr(obj, 'id_value', None)
    mongo_obj['med_stmt_id_value'] = id_value
    
    context_ref = getattr(obj, 'context_reference', None)
    mongo_obj['med_stmt_context_ref'] = context_ref
    
    _extract_coding_systems_list(obj, mongo_obj, 'med_stmt')
    
    subject_ref = getattr(obj, 'subject_reference', None)

    # The subject_ref has the form Patient/9940, where the number after the
    # fwd slash is the patient ID. Extract this ID and store in the 'subject'
    # field.
    if subject_ref is not None:
        assert '/' in subject_ref
        text, num = subject_ref.split('/')
        mongo_obj['subject'] = num
    mongo_obj['med_stmt_subject_ref'] = subject_ref

    subject_display = getattr(obj, 'subject_display', None)
    mongo_obj['med_stmt_subject_display'] = subject_display

    taken = getattr(obj, 'taken', None)
    mongo_obj['med_stmt_taken'] = taken

    # list of DoseQuantity objects
    dosage_list = getattr(obj, 'dosage_list', None)
    if dosage_list is not None:
        counter = 1
        for dq_obj in dosage_list:
            key = 'med_stmt_dosage_value_{0}'.format(counter)
            mongo_obj[key] = dq_obj.value
            key = 'med_stmt_dosage_unit_{0}'.format(counter)
            mongo_obj[key] = dq_obj.unit
            key = 'med_stmt_dosage_system_{0}'.format(counter)
            mongo_obj[key] = dq_obj.system
            key = 'med_stmt_dosage_code_{0}'.format(counter)
            mongo_obj[key] = dq_obj.code
            counter += 1

    date_time = getattr(obj, 'date_time', None)
    dt_string = None
    if date_time is not None:
        dt_string = date_time.isoformat()
    mongo_obj['datetime'] = dt_string
    
    end_date_time = getattr(obj, 'end_date_time', None)
    dt_string = None
    if end_date_time is not None:
        dt_string = end_date_time.isoformat()
    mongo_obj['end_datetime'] = dt_string
    
    # add display/formatting info
    value_name = mongo_obj['med_stmt_codesys_display_1']
    value = mongo_obj['med_stmt_dosage_value_1']
    if value is None:
        value = ''
    units = mongo_obj['med_stmt_dosage_unit_1']
    if units is None:
        units = ''
    result_display_obj = {
        'date': mongo_obj['datetime'],
        'result_content':'{0}: {1} {2}'.format(value_name, value, units),
        'sentence':'',
        'highlights':[value_name, value, units]
    }
    mongo_obj['result_display'] = result_display_obj


###############################################################################
def _extract_medication_request_resource(obj, mongo_obj):
    """
    Extract data from the FHIR MedicationRequest resource and load into
    mongo dict.
    """

    assert isinstance(obj, crp.MedicationRequestResource)

    if _KEY_ERROR in obj:
        # no data returned
        return

    id_value = getattr(obj, 'id_value', None)
    mongo_obj['med_req_id_value'] = id_value
    
    _extract_coding_systems_list(obj, mongo_obj, 'med_req')
    
    subject_ref = getattr(obj, 'subject_reference', None)

    # The subject_ref has the form Patient/9940, where the number after the
    # fwd slash is the patient ID. Extract this ID and store in the 'subject'
    # field.
    if subject_ref is not None:
        assert '/' in subject_ref
        text, num = subject_ref.split('/')
        mongo_obj['subject'] = num
    mongo_obj['med_req_subject_ref'] = subject_ref

    subject_display = getattr(obj, 'subject_display', None)
    mongo_obj['med_req_subject_display'] = subject_display

    date_time = getattr(obj, 'date_time', None)
    dt_string = None
    if date_time is not None:
        dt_string = date_time.isoformat()
    mongo_obj['datetime'] = dt_string
    
    # add display/formatting info
    value_name = mongo_obj['med_req_codesys_display_1']
    value = ''
    units = ''
    result_display_obj = {
        'date': mongo_obj['datetime'],
        'result_content':'{0}: {1} {2}'.format(value_name, value, units),
        'sentence':'',
        'highlights':[value_name, value, units]
    }
    mongo_obj['result_display'] = result_display_obj
    
    
###############################################################################
def _get_custom_arg(str_key, str_variable_name, job_id, custom_arg_dict):
    """
    Extract a value at the given key from the given dict, or return None
    if not found. Attempt to read from environmental variables, if known.
    """

    value = None
    if str_key in custom_arg_dict:
        value = custom_arg_dict[str_key]

    if not value:
        if str_key in util.properties:
            value = util.properties[str_key]

    # echo in job status and in log file
    msg = 'CQLExecutionTask: {0} == {1}'.format(str_variable_name, value)
    data_access.update_job_status(job_id,
                                  util.conn_string,
                                  data_access.IN_PROGRESS,
                                  msg)
    # write msg to log file
    print(msg)
    
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

    print('\n*** DATETIME START: {0}'.format(datetime_start))
    print('***   DATETIME END: {0}'.format(datetime_end))
        
    return (datetime_start, datetime_end)


###############################################################################
def _apply_datetime_filter(samples, t0, t1):
    """
    Remove any samples outside of the specified start and end times.
    The 'samples' parameter is a list of namedtuples from the CQL result
    parser module.
    """

    if 0 == len(samples):
        return []
    
    results = []
    for s in samples:

        # Timestamps from the relevant FHIR resources have been mapped to
        # the 'date_time' field by the cql_result_parser.
        t = getattr(s, 'date_time', None)
        if t is None:
            continue

        if t0 is not None and t <= t0:
            continue
        if t1 is not None and t >= t1:
            continue

        results.append(s)

    return results


###############################################################################
class CQLExecutionTask(BaseTask):
    
    task_name = "CQLExecutionTask"
        
    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        
        # get the task_index custom arg for this task
        task_index = self.pipeline_config.custom_arguments['task_index']

        # Do an atomic check on the index and proceed only if a match. There
        # will be a match only for one instance of all task clones that share
        # this particular value of the task_index.
        check_val = _atomic_check(task_index)
        if check_val == task_index:

            job_id = str(self.job)
            
            # URL of the FHIR server's CQL evaluation endpoint
            cql_eval_url = _get_custom_arg(_FHIR_CQL_EVAL_URL,
                                           'cql_eval_url',
                                           job_id,
                                           self.pipeline_config.custom_arguments)
            if cql_eval_url is None:
                return
            
            patient_id = _get_custom_arg(_FHIR_PATIENT_ID,
                                         'patient_id',
                                         job_id,
                                         self.pipeline_config.custom_arguments)
            if patient_id is None:
                return

            # patient_id must be a string
            patient_id = str(patient_id)
            
            # CQL code string verbatim from CQL file
            cql_code = self.pipeline_config.cql
            print('\n*** CQL CODE: ***\n')
            print(cql_code)
            print()
            if cql_code is None or 0 == len(cql_code):
                print('\n*** CQLExecutionTask: no CQL code was found ***\n')
                return
            
            fhir_terminology_service_endpoint = _get_custom_arg(_FHIR_TERMINOLOGY_SERVICE_ENDPOINT,
                                                                'fhir_terminology_service_endpoint',
                                                                job_id,
                                                                self.pipeline_config.custom_arguments)
             
            fhir_data_service_uri = _get_custom_arg(_FHIR_DATA_SERVICE_URI,
                                                    'fhir_data_service_uri',
                                                    job_id,
                                                    self.pipeline_config.custom_arguments)
            if fhir_terminology_service_endpoint is None:
                return
            
            if fhir_data_service_uri is None:
                return

            # ensure '/' termination
            if not fhir_data_service_uri.endswith('/'):
                    fhir_data_service_uri += '/'

            # initialize payload
            payload = {
                # the requests lib will properly escape the raw string
                "code":cql_code,
                "fhirServiceUri":fhir_terminology_service_endpoint,
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

            headers = {
                'Content-Type':'application/json',
                'Authorization':'{0} {1}'.format(fhir_auth_type, fhir_auth_token)
            }
            
            # params for UMLS OID code lookup
            fhir_terminology_service_uri = _get_custom_arg(_FHIR_TERMINOLOGY_SERVICE_URI,
                                                           'fhir_terminology_service_uri',
                                                           job_id,
                                                           self.pipeline_config.custom_arguments)
            # ensure '/' termination
            if fhir_terminology_service_uri is not None:
                if not fhir_terminology_service_uri.endswith('/'):
                    fhir_terminology_service_uri += '/'

            fhir_terminology_user_name = _get_custom_arg(_FHIR_TERMINOLOGY_USER_NAME,
                                                         'fhir_terminology_user_name',
                                                         job_id,
                                                         self.pipeline_config.custom_arguments)
            
            fhir_terminology_user_password = _get_custom_arg(_FHIR_TERMINOLOGY_USER_PASSWORD,
                                                             'fhir_terminology_user_password',
                                                             job_id,
                                                             self.pipeline_config.custom_arguments)
            
            # setup terminology server capability
            if fhir_terminology_service_uri is not None and \
               fhir_terminology_user_name is not None and fhir_terminology_user_name != 'username' and \
               fhir_terminology_user_password is not None and fhir_terminology_user_password != 'password':
                payload['terminologyServiceUri'] = fhir_terminology_service_uri
                payload['terminologyUser'] = fhir_terminology_user_name
                payload['terminologyPass'] = fhir_terminology_user_password
                
            # perform the request here, catch lots of different exceptions
            has_error = False
            try:
                r = requests.post(cql_eval_url, headers=headers, json=payload)
            except requests.exceptions.HTTPError as e:
                print('\n*** CQLExecutionTask HTTP error: "{0}" ***\n'.format(e))
                has_error = True
            except requests.exceptions.ConnectionError as e:
                print('\n*** CQLExecutionTask ConnectionError: "{0}" ***\n'.format(e))
                has_error = True
            except requests.exceptions.Timeout as e:
                print('\n*** CQLExecutionTask Timeout: "{0}" ***\n'.format(e))
                has_error = True
            except requests.exceptions.RequestException as e:
                print('\n*** CQLEXecutionTask RequestException: "{0}" ***\n'.format(e))
                has_error = True

            if has_error:
                print('HTTP error, terminating CQLExecutionTask...')
                return
                
            print('Response status code: {0}'.format(r.status_code))

            results = None
            if 200 == r.status_code:
                print('\n*** CQL JSON RESULTS ***\n')
                print(r.json())
                print()

                # data_earliest == earliest datetime in the data
                # data_latest   == latest datetime in the data
                results, data_earliest, data_latest = _json_to_objs(r.json())
                print('\tfound {0} results'.format(len(results)))
            else:
                print('\n*** CQLExecutionTask: HTTP status code {0} ***\n'.format(r.status_code))
                return

            if results is None:
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
                        
            patient_obj = {}
            for obj in results:

                mongo_obj = {}
                
                # get patient info once
                # all others duplicate the patient info in new records
                # move the mongo write to after each observation
                if isinstance(obj, crp.PatientResource):
                    print('\tFOUND PATIENT RESOURCE')
                    # don't write the patient resource yet; instead, include
                    # the patient data with every additional write
                    _extract_patient_resource(obj, patient_obj)
                    continue
                elif isinstance(obj, crp.ProcedureResource):
                    print('\tFOUND PROCEDURE RESOURCE')
                    _extract_procedure_resource(obj, mongo_obj)
                elif isinstance(obj, crp.ConditionResource):
                    print('\tFOUND CONDITION RESOURCE')
                    _extract_condition_resource(obj, mongo_obj)
                elif isinstance(obj, crp.ObservationResource):
                    print('\tFOUND OBSERVATION RESOURCE')
                    _extract_observation_resource(obj, mongo_obj)
                elif isinstance(obj, crp.MedicationStatementResource):
                    print('\tFOUND MEDICATION STATEMENT RESOURCE')
                    _extract_medication_statement_resource(obj, mongo_obj)
                elif isinstance(obj, crp.MedicationRequestResource):
                    print('\tFOUND MEDICATION REQUEST RESOURCE')
                    _extract_medication_request_resource(obj, mongo_obj)
                else:
                    print('\tFOUND UNKNOWN RESOURCE')
                    continue

                # copy patient data
                for k,v in patient_obj.items():
                    mongo_obj[k] = v

                self.write_result_data(temp_file, mongo_client, None, mongo_obj)


###############################################################################
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='test CQL Engine result decoding locally')

    parser.add_argument('-f', '--filepath',
                        help='path to JSON file containing CQL Engine results')

    args = parser.parse_args()

    filpath = None
    if 'filepath' in args and args.filepath:
        filepath = args.filepath
        if not os.path.isfile(filepath):
            print('Unknown file specified: "{0}"'.format(filepath))
            sys.exit(-1)

    with open(filepath, 'rt') as infile:
        json_string = infile.read()
        json_data = json.loads(json_string)

        results, data_earliest, data_latest = _json_to_objs(json_data)
        print('\tfound {0} results'.format(len(results)))
        if results is not None:

            counter = 0
            patient_obj = {}
            for obj in results:

                mongo_obj = {}
                
                # get patient info once
                # all others duplicate the patient info in new records
                # move the mongo write to after each observation
                if isinstance(obj, crp.PatientResource):
                    print('\tFOUND PATIENT RESOURCE')
                    # don't write the patient resource yet; instead, include
                    # the patient data with every additional write
                    _extract_patient_resource(obj, patient_obj)
                    continue
                elif isinstance(obj, crp.ProcedureResource):
                    print('\tFOUND PROCEDURE RESOURCE')
                    _extract_procedure_resource(obj, mongo_obj)
                elif isinstance(obj, crp.ConditionResource):
                    print('\tFOUND CONDITION RESOURCE')
                    _extract_condition_resource(obj, mongo_obj)
                elif isinstance(obj, crp.ObservationResource):
                    print('\tFOUND OBSERVATION RESOURCE')
                    _extract_observation_resource(obj, mongo_obj)
                elif isinstance(obj, crp.MedicationStatementResource):
                    print('\tFOUND MEDICATION STATEMENT RESOURCE')
                    _extract_medication_statement_resource(obj, mongo_obj)
                elif isinstance(obj, crp.MedicationRequestResource):
                    print('\tFOUND MEDICATION REQUEST RESOURCE')
                    _extract_medication_request_resource(obj, mongo_obj)
                else:
                    print('\tFOUND UNKNOWN RESOURCE')
                    continue

                # copy patient data
                for k,v in patient_obj.items():
                    mongo_obj[k] = v

                # print out
                print('RESULT {0}'.format(counter))
                for k,v in mongo_obj.items():
                    if dict == type(v):
                        print('\t{0}'.format(k))
                        for k2,v2 in v.items():
                            print('\t\t{0} => {1}'.format(k2, v2))
                    else:
                        print('\t{0} => {1}'.format(k,v))
                counter += 1
