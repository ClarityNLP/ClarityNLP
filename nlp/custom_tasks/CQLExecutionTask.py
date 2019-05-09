# A custom task for running CQL queries via ClarityNLP.

from tasks.task_utilities import BaseTask
from pymongo import MongoClient
import util
import multiprocessing
from datetime import datetime

import re
import os
import json
import requests
import data_access.cql_result_parser as crp


_VERSION_MAJOR = 0
_VERSION_MINOR = 4

_KEY_FHIR_URL = 'fhir_url'
_KEY_FHIR_AUTH_TYPE = 'fhir_auth_type'
_KEY_FHIR_AUTH_TOKEN = 'fhir_auth_token'
_KEY_PATIENT_ID = 'patient_id'
_KEY_TERMINOLOGY_SERVICE_URI = 'terminologyServiceUri'
_KEY_TERMINOLOGY_USER = 'terminologyUser'
_KEY_TERMINOLOGY_PASS = 'terminologyPass'
        
# number of unique task indices among all Luigi clones of this task
_MAX_TASK_INDEX = 1000

# Array for coordinating clones of this task, all initialized to -1.
_shared_array = multiprocessing.Array('i', [-1]*_MAX_TASK_INDEX)


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
def _fixup_fhir_datetime(fhir_datetime_str):
    """
    The FHIR server returns a date time as follows:

        '2156-09-17T09:01:02+03:04

    Need to remove the final colon in the UTC offset portion (+03:04) to
    match the python strftime format for the UTC offset.
    """

    _regex_fhir_utc_offset = re.compile(r'\+\d\d:\d\d\Z')
    
    new_str = fhir_datetime_str
    match = _regex_fhir_utc_offset.search(fhir_datetime_str)
    if match:
        pos = match.start() + 3
        new_str = fhir_datetime_str[:pos] + fhir_datetime_str[pos+1:]
        
    return new_str
    

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

    return results


###############################################################################
def _extract_coding_systems_list(obj, mongo_obj, prefix):
    """
    Extract the list of (code, system, display) tuples.
    """
    
    coding_systems_list = getattr(obj, 'coding_systems_list')
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

    # patient id is in the 'subject' field
    patient_id = getattr(obj, 'subject')
    mongo_obj['patient_subject'] = patient_id

    # get the list of (first_name, last_name) tuples and create numbered fields
    name_list = getattr(obj, 'name_list')
    counter = 1
    for first, last in name_list:
        key_fname = 'patient_fname_{0}'.format(counter)
        key_lname = 'patient_lname_{0}'.format(counter)
        mongo_obj[key_fname] = first
        mongo_obj[key_lname] = last
        counter += 1

    gender = getattr(obj, 'gender')
    mongo_obj['patient_gender'] = gender

    # dob is in YYYY-MM-DD format
    dob = getattr(obj, 'date_of_birth')
    mongo_obj['patient_date_of_birth'] = datetime.strptime(dob, '%Y-%m-%d')
    

###############################################################################
def _extract_procedure_resource(obj, mongo_obj):
    """
    Extract data from the FHIR procedure resource and load into mongo dict.
    """

    assert isinstance(obj, crp.ProcedureResource)

    id_value = getattr(obj, 'id_value')
    mongo_obj['procedure_id_value'] = id_value

    status = getattr(obj, 'status')
    mongo_obj['procedure_status'] = status

    _extract_coding_systems_list(obj, mongo_obj, 'procedure')

    subject_ref = getattr(obj, 'subject_reference')
    mongo_obj['procedure_subject_ref'] = subject_ref

    subject_display = getattr(obj, 'subject_display')
    mongo_obj['procedure_subject_display'] = subject_display

    context_ref = getattr(obj, 'context_reference')
    mongo_obj['procedure_context_ref'] = context_ref

    performed_date_time = getattr(obj, 'performed_date_time')
    if performed_date_time is not None:
        performed_date_time = _fixup_fhir_datetime(performed_date_time)
        mongo_obj['procedure_performed_date_time'] = datetime.strptime(performed_date_time,
                                                                       '%Y-%m-%dT%H:%M:%S%z')


###############################################################################
def _extract_condition_resource(obj, mongo_obj):
    """
    Extract dta from the FHIR condition resource and load into mongo dict.
    """

    assert isinstance(obj, crp.ConditionResource)

    id_value = getattr(obj, 'id_value')
    mongo_obj['condition_id_value'] = id_value

    category_list = getattr(obj, 'category_list')
    counter = 1
    for elt in category_list:
        if isinstance(elt, crp.CodingObj):
            mongo_obj['condition_category_code_{0}'.format(counter)] = elt.code
            mongo_obj['condition_category_system_{0}'.format(counter)] = elt.system
            mongo_obj['condition_category_display_{0}'.format(counter)] = elt.display
            counter += 1

    _extract_coding_systems_list(obj, mongo_obj, 'condition')
        
    subject_ref = getattr(obj, 'subject_reference')
    mongo_obj['condition_subject_ref'] = subject_ref

    subject_display = getattr(obj, 'subject_display')
    mongo_obj['condition_subject_display'] = subject_display

    context_ref = getattr(obj, 'context_reference')
    mongo_obj['condition_context_ref'] = context_ref

    onset_date_time = getattr(obj, 'onset_date_time')
    if onset_date_time is not None:
        onset_date_time = _fixup_fhir_datetime(onset_date_time)
        mongo_obj['condition_onset_date_time'] = datetime.strptime(onset_date_time,
                                                                   '%Y-%m-%dT%H:%M:%S%z')
    
    abatement_date_time = getattr(obj, 'abatement_date_time')
    if abatement_date_time is not None:
        abatement_date_time = _fixup_fhir_datetime(abatement_date_time)
        mongo_obj['condition_abatement_date_time'] = datetime.strptime(abatement_date_time,
                                                                   '%Y-%m-%dT%H:%M:%S%z')
            
        
###############################################################################
def _extract_observation_resource(obj, mongo_obj):
    """
    Extract data from the FHIR observation resource and load into mongo dict.
    """

    assert isinstance(obj, crp.ObservationResource)

    subject_ref = getattr(obj, 'subject_reference')

    # The subject_ref has the form Patient/9940, where the number after the
    # fwd slash is the patient ID. Extract this ID and store in the 'subject'
    # field.
    if subject_ref is not None:
        assert '/' in subject_ref
        text, num = subject_ref.split('/')
        mongo_obj['subject'] = num
    mongo_obj['obs_subject_ref'] = subject_ref

    subject_display = getattr(obj, 'subject_display')
    mongo_obj['obs_subject_display'] = subject_display

    context_ref = getattr(obj, 'context_reference')
    mongo_obj['obs_context_ref'] = context_ref

    eff_date_time = getattr(obj, 'date_time')
    if eff_date_time is not None:
        eff_date_time = _fixup_fhir_datetime(eff_date_time)
        mongo_obj['obs_effective_date_time'] = datetime.strptime(eff_date_time,
                                                                 '%Y-%m-%dT%H:%M:%S%z')
    else:
        mongo_obj['obs_effective_date_time'] = None

    value = getattr(obj, 'value')
    if value is not None:
        # store this in the 'value' field also
        mongo_obj['value'] = value
    mongo_obj['obs_value'] = value

    unit = getattr(obj, 'unit')
    mongo_obj['obs_unit'] = unit

    unit_system = getattr(obj, 'unit_system')
    mongo_obj['obs_unit_system'] = unit_system

    unit_code = getattr(obj, 'unit_code')
    mongo_obj['obs_unit_code'] = unit_code

    _extract_coding_systems_list(obj, mongo_obj, 'obs')
        
    
###############################################################################
def _get_custom_arg(str_key, custom_arg_dict):
    """
    Extract a value at the given key from the given dict, or return None
    if not found.
    """

    value = None
    if str_key in custom_arg_dict:
        value = custom_arg_dict[str_key]

    return value

    
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
        
            # URL of the FHIR server's CQL evaluation endpoint

            # check custom NLPQL params or pipeline config first
            fhir_url = _get_custom_arg(_KEY_FHIR_URL,
                                       self.pipeline_config.custom_arguments)
            if fhir_url is None:
                # look for it as a local param
                try:
                    fhir_url = util.fhir_url
                except:
                    fhir_url = None

            if fhir_url is None:
                print('\n*** CQLExecutionTask: no value for fhir_url ***\n')
                return

            print('fhir_url: {0}'.format(fhir_url))
            
            # ID of the desired patient
            patient_id = _get_custom_arg(_KEY_PATIENT_ID,
                                         self.pipeline_config.custom_arguments)
            # patient_id must be a string
            patient_id = patient_id
            if patient_id is None:
                # look for it as a local param
                try:
                    patient_id = util.fhir_patient_id
                except:
                    patient_id = None

            if patient_id is None:
                print('\n*** CQLExecutionTask: no value for patient_id ***\n')
                return

            # patient_id must be a string
            patient_id = str(patient_id)
            print('patient_id: {0}'.format(patient_id))
            
            # CQL code string verbatim from CQL file
            cql_code = self.pipeline_config.cql
            print('\n*** CQL CODE: ***\n')
            print(cql_code)
            print()
            if cql_code is None or 0 == len(cql_code):
                print('\n*** CQLExecutionTask: no CQL code was found ***\n')
                return
            
            try:
                fhir_service_uri = util.fhir_service_uri
            except:
                fhir_service_uri = None

            try:
                fhir_data_service_uri = util.fhir_data_service_uri
            except:
                fhir_data_service_uri = None
                
            if fhir_service_uri is None:
                print('\n*** CQLExecutionTask: no value for fhir_service_uri ***\n')
                return
            
            if fhir_data_service_uri is None:
                print('\n*** CQLExecutionTask: no value for fhir_data_service_uri ***\n')
                return

            # ensure '/' termination
            if not fhir_data_service_uri.endswith('/'):
                    fhir_data_service_uri += '/'
            
            headers = {'Content-Type':'application/json'}
            
            payload = {
                # the requests lib will properly escape the raw string
                "code":cql_code,
                "fhirServiceUri":fhir_service_uri,
                "dataServiceUri":fhir_data_service_uri,
                "patientId":patient_id,
            }

            fhir_auth_type = _get_custom_arg(_KEY_FHIR_AUTH_TYPE,
                                             self.pipeline_config.custom_arguments)

            fhir_auth_token = _get_custom_arg(_KEY_FHIR_AUTH_TOKEN,
                                              self.pipeline_config.custom_arguments)

            if fhir_auth_type is not None and fhir_auth_token is not None:
                payload[_KEY_FHIR_AUTH_TYPE] = fhir_auth_type
                payload[_KEY_FHIR_AUTH_TOKEN] = fhir_auth_token

            # params for UMLS OID code lookup
            try:
                terminologyServiceUri = util.fhir_terminology_service_uri
            except:
                terminologyServiceUri = None

            # ensure '/' termination
            if terminologyServiceUri is not None:
                if not terminologyServiceUri.endswith('/'):
                    terminologyServiceUri += '/'
                    
            try:
                terminologyUser = util.fhir_terminology_user
            except:
                terminologyUser = None

            try:
                terminologyPass = util.fhir_terminology_password
            except:
                terminologyPass = None

            # setup terminology server capability
            if terminologyServiceUri is not None and \
               terminologyUser is not None and terminologyUser != 'username' and \
               terminologyPass is not None and terminologyPass != 'password':
                payload[_KEY_TERMINOLOGY_SERVICE_URI] = terminologyServiceUri
                payload[_KEY_TERMINOLOGY_USER] = terminologyUser
                payload[_KEY_TERMINOLOGY_PASS] = terminologyPass
                print('terminologyServiceUri: {0}'.format(terminologyServiceUri))
                print('terminologyUser: {0}'.format(terminologyUser))
                print('terminologyPass: {0}'.format(terminologyPass))
                
            exception_thrown = False

            # perform the request here, catch lots of different exceptions
            try:
                r = requests.post(fhir_url, headers=headers, json=payload)
            except requests.exceptions.HTTPError as e:
                print('\n*** CQLExecutionTask HTTP error: "{0}" ***\n'.format(e))
                exception_thrown = True
            except requests.exceptions.ConnectionError as e:
                print('\n*** CQLExecutionTask ConnectionError: "{0}" ***\n'.format(e))
                exception_thrown = True
            except requests.exceptions.Timeout as e:
                print('\n*** CQLExecutionTask Timeout: "{0}" ***\n'.format(e))
                exception_thrown = True
            except requests.exceptions.RequestException as e:
                print('\n*** CQLEXecutionTask RequestException: "{0}" ***\n'.format(e))
                exception_thrown = True

            print('Response status code: {0}'.format(r.status_code))

            results = None
            if 200 == r.status_code:
                print('\n*** CQL JSON RESULTS ***\n')
                print(r.json())
                print()
                
                results = _json_to_objs(r.json())
                print('\tfound {0} results'.format(len(results)))            

            if results is None:
                return
                
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
                else:
                    print('\tFOUND UNKNOWN RESOURCE')
                    continue

                # copy patient data
                for k,v in patient_obj.items():
                    mongo_obj[k] = v

                self.write_result_data(temp_file, mongo_client, None, mongo_obj)
