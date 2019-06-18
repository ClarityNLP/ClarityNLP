#!/usr/bin/env python3
"""
Import-only module used to decode JSON results from the FHIR CQL wrapper.
"""

import re
import os
import sys
import json
import optparse
from datetime import datetime, timezone
from collections import namedtuple

_VERSION_MAJOR = 0
_VERSION_MINOR = 2
_MODULE_NAME   = 'cibmtr_data_parser.py'

# set to True to enable debug output
_TRACE = False

# dict keys used to extract portions of the JSON data
_KEY_ABATEMENT_DATE_TIME = 'abatementDateTime'
_KEY_CATEGORY            = 'category'
_KEY_CODE                = 'code'
_KEY_CODING              = 'coding'
_KEY_CONTEXT             = 'context'
_KEY_DISPLAY             = 'display'
_KEY_DOB                 = 'birthDate'
_KEY_EFF_DATE_TIME       = 'effectiveDateTime'
_KEY_FAMILY_NAME         = 'family'
_KEY_GENDER              = 'gender'
_KEY_GIVEN_NAME          = 'given'
_KEY_ID                  = 'id'
_KEY_LOCATION            = 'location'
_KEY_NAME                = 'name'
_KEY_ONSET_DATE_TIME     = 'onsetDateTime'
_KEY_PERFORMED_DATE_TIME = 'performedDateTime'
_KEY_REFERENCE           = 'reference'
_KEY_RESOURCE_TYPE       = 'resourceType'
_KEY_RESULT              = 'result'
_KEY_RESULT_TYPE         = 'resultType'
_KEY_STATUS              = 'status'
_KEY_SUBJECT             = 'subject'
_KEY_SYSTEM              = 'system'
_KEY_UNIT                = 'unit'
_KEY_VALUE               = 'value'
_KEY_VALUE_QUANTITY      = 'valueQuantity'

_STR_BUNDLE      = 'FhirBundleCursorStu3'
#_STR_CONCEPT     = 'Concept'
_STR_CONDITION   = 'Condition'
_STR_OBSERVATION = 'Observation'
_STR_PATIENT     = 'Patient'
_STR_PROCEDURE   = 'Procedure'

# fields extracted from a 'Patient' FHIR resource
PATIENT_FIELDS = [
    'subject',   # patient_id
    'name_list', # list of (first_name, last_name) tuples
    'gender',
    'date_of_birth'
]
PatientResource = namedtuple('PatientResource', PATIENT_FIELDS)

# All namedtuples below have a date_time field, which is an instance
# of a python datetime object.

# fields extracted from a 'Procedure' FHIR resource
PROCEDURE_FIELDS = [
    'id_value', 
    'status',
    'coding_systems_list',
    'subject_reference',
    'subject_display',
    'context_reference',
    'date_time'
]
ProcedureResource = namedtuple('ProcedureResource', PROCEDURE_FIELDS)

# fields extracted from a 'Condition' FHIR resource
CONDITION_FIELDS = [
    'id_value',
    'category_list',
    'coding_systems_list',
    'subject_reference',
    'subject_display',
    'context_reference',
    'date_time',
    'end_date_time'
]
ConditionResource = namedtuple('ConditionResource', CONDITION_FIELDS)


# fields extracted from an 'Observation' FHIR resource
OBSERVATION_FIELDS = [
    'subject_reference',
    'subject_display',
    'context_reference',
    'date_time',
    'value',
    'unit',
    'unit_system',
    'unit_code',
    'coding_systems_list'
]
ObservationResource = namedtuple('ObservationResource', OBSERVATION_FIELDS)

CODING_FIELDS = ['code', 'system', 'display']
CodingObj = namedtuple('CodingObj', CODING_FIELDS)

# regex used to recognize UTC offsets in a FHIR datetime string
_regex_fhir_utc_offset = re.compile(r'\+\d\d:\d\d\Z')


###############################################################################
def enable_debug():

    global _TRACE
    _TRACE = True


###############################################################################
def _fixup_fhir_datetime(fhir_datetime_str):
    """
    The FHIR server returns a date time as follows:

        '2156-09-17T09:01:02+03:04

    Need to remove the final colon in the UTC offset portion (+03:04) to
    match the python strftime format for the UTC offset.
    """
    
    new_str = fhir_datetime_str
    match = _regex_fhir_utc_offset.search(fhir_datetime_str)
    if match:
        pos = match.start() + 3
        new_str = fhir_datetime_str[:pos] + fhir_datetime_str[pos+1:]
        
    return new_str

    
###############################################################################
def _decode_value_quantity(obj):
    value_quantity_dict = obj[_KEY_VALUE_QUANTITY]
    assert dict == type(value_quantity_dict)

    value = None
    unit = None
    unit_system = None
    unit_code = None

    if _KEY_VALUE in value_quantity_dict:
        value = value_quantity_dict[_KEY_VALUE]
    if _KEY_UNIT in value_quantity_dict:
        unit = value_quantity_dict[_KEY_UNIT]
    if _KEY_SYSTEM in value_quantity_dict:
        unit_system = value_quantity_dict[_KEY_SYSTEM]
    if _KEY_CODE in value_quantity_dict:
        unit_code = value_quantity_dict[_KEY_CODE]

    return (value, unit, unit_system, unit_code)


###############################################################################
def _decode_code_dict(obj):
    """
    Extract the coding systems, codes, and display names and return as a
    list of CodingObj namedtuples.
    """

    coding_systems_list = []
    if _KEY_CODE in obj:
        code_dict = obj[_KEY_CODE]
        # should have a 'coding' key
        if _KEY_CODING in code_dict:
            # value should be a list
            coding_list = code_dict[_KEY_CODING]
            assert list == type(coding_list)
            # list elements should be dicts
            for coding_dict in coding_list:
                assert dict == type(coding_dict)
                code = None
                if _KEY_CODE in coding_dict:
                    code = coding_dict[_KEY_CODE]
                system = None
                if _KEY_SYSTEM in coding_dict:
                    system = coding_dict[_KEY_SYSTEM]
                display = None
                if _KEY_DISPLAY in coding_dict:
                    display = coding_dict[_KEY_DISPLAY]

                coding_systems_list.append( CodingObj(code, system, display))

    return coding_systems_list


###############################################################################
def _decode_subject_info(obj):
    """
    Extract and return patient info.
    """

    subject_reference = None
    subject_display   = None
    
    if _KEY_SUBJECT in obj:
        subject_dict = obj[_KEY_SUBJECT]
        assert dict == type(subject_dict)

        # get the patient ID, which is in the 'reference' field
        # appears as 'Patient/5930', for instance
        if _KEY_REFERENCE in subject_dict:
            subject_reference = subject_dict[_KEY_REFERENCE]
        if _KEY_DISPLAY in subject_dict:
            subject_display = subject_dict[_KEY_DISPLAY]
            
    return (subject_reference, subject_display)
    

###############################################################################
def _decode_context_info(obj):
    """
    """

    context_reference = None
    if _KEY_CONTEXT in obj:
        context_dict = obj[_KEY_CONTEXT]
        assert dict == type(context_dict)
        if _KEY_REFERENCE in context_dict:
            context_reference = context_dict[_KEY_REFERENCE]

    return context_reference
            

###############################################################################
def _decode_id_value(obj):

    id_value = None
    if _KEY_ID in obj:
        id_value = obj[_KEY_ID]

    return id_value


###############################################################################
def _decode_observation(obj):
    """
    Decode a FHIR observation result from the 'obj' dict.
    """

    # First decipher the coding info, which includes the code system, the
    # code, and the name of whatever the code applies to. There could
    # potentially be multiple coding tuples for the same object.
    #
    # For example:
    #     system  = 'http://loinc.org'
    #     code    = '804-5'
    #     display = 'Leukocytes [#/volume] in Blood by Manual count'
    #

    coding_systems_list = _decode_code_dict(obj)
    subject_reference, subject_display = _decode_subject_info(obj)
    context_reference = _decode_context_info(obj)
            
    value = None
    unit = None
    unit_system = None
    unit_code = None
    if _KEY_VALUE_QUANTITY in obj:
        value, unit, unit_system, unit_code = _decode_value_quantity(obj)

    date_time = None    
    if _KEY_EFF_DATE_TIME in obj:
        date_time = obj[_KEY_EFF_DATE_TIME]
        date_time = _fixup_fhir_datetime(date_time)
        date_time = datetime.strptime(date_time, '%Y-%m-%dT%H:%M:%S%z')        

    observation = ObservationResource(
        subject_reference,
        subject_display,
        context_reference,
        date_time,
        value,
        unit,
        unit_system,
        unit_code,
        coding_systems_list
    )
        
    return observation


###############################################################################
def _decode_condition(obj):
    """
    Decode a FHIR 'Condition' object from the JSON data.
    """

    if _TRACE: print('Decoding CONDITION resource...')

    result = []

    obj_type = type(obj)
    assert dict == obj_type

    id_value = _decode_id_value(obj)
    category_list = []
    if _KEY_CATEGORY in obj:
        obj_list = obj[_KEY_CATEGORY]
        assert list == type(obj_list)
        for elt in obj_list:
            if dict == type(elt):
                if _KEY_CODING in elt:
                    coding_list = elt[_KEY_CODING]
                    for coding_dict in coding_list:
                        assert dict == type(coding_dict)
                        code = None
                        if _KEY_CODE in coding_dict:
                            code = coding_dict[_KEY_CODE]
                        system = None
                        if _KEY_SYSTEM in coding_dict:
                            system = coding_dict[_KEY_SYSTEM]
                        display = None
                        if _KEY_DISPLAY in coding_dict:
                            display = coding_dict[_KEY_DISPLAY]

                        category_list.append( CodingObj(code, system, display))
                
            # any other keys of relevance for elts of category_list?
    coding_systems_list = _decode_code_dict(obj)
    subject_reference, subject_display = _decode_subject_info(obj)
    context_reference = _decode_context_info(obj)

    onset_date_time = None
    abatement_date_time = None
    if _KEY_ONSET_DATE_TIME in obj:
        onset_date_time = obj[_KEY_ONSET_DATE_TIME]
        onset_date_time = _fixup_fhir_datetime(onset_date_time)
        onset_date_time = datetime.strptime(onset_date_time, '%Y-%m-%dT%H:%M:%S%z')
    if _KEY_ABATEMENT_DATE_TIME in obj:
        abatement_date_time = obj[_KEY_ABATEMENT_DATE_TIME]
        abatement_date_time = _fixup_fhir_datetime(abatement_date_time)
        abatement_date_time = datetime.strptime(abatement_date_time, '%Y-%m-%dT%H:%M:%S%z')

    condition = ConditionResource(
        id_value,
        category_list,
        coding_systems_list,
        subject_reference,
        subject_display,
        context_reference,
        date_time=onset_date_time,
        end_date_time=abatement_date_time
    )
        
    return condition


###############################################################################
def _decode_procedure(obj):
    """
    Decode a FHIR 'Procedure' object from the JSON data.
    """

    if _TRACE: print('Decoding PROCEDURE resource...')

    result = []

    obj_type = type(obj)
    assert dict == obj_type

    status = None
    if _KEY_STATUS in obj:
        status = obj[_KEY_STATUS]

    id_value = _decode_id_value(obj)
    coding_systems_list = _decode_code_dict(obj)
    subject_reference, subject_display = _decode_subject_info(obj)
    context_reference = _decode_context_info(obj)

    dt = None
    if _KEY_PERFORMED_DATE_TIME in obj:
        performed_date_time = obj[_KEY_PERFORMED_DATE_TIME]
        performed_date_time = _fixup_fhir_datetime(performed_date_time)
        dt = datetime.strptime(performed_date_time, '%Y-%m-%dT%H:%M:%S%z')
    
    procedure = ProcedureResource(
        id_value,
        status,
        coding_systems_list,
        subject_reference,
        subject_display,
        context_reference,
        date_time=dt
    )
    
    return procedure


###############################################################################
def _decode_patient(name, patient_obj):
    """
    Decode a FHIR 'Patient' object from the JSON data.
    """

    if _TRACE: print('Decoding PATIENT resource...')

    result = []

    # the patient object should be the string representation of a dict
    obj_type = type(patient_obj)
    assert str == obj_type

    try:
        obj = json.loads(patient_obj)
    except json.decoder.JSONDecoderError as e:
        print('\t{0}: String conversion (patient) failed with error: "{1}"'.
              format(_MODULE_NAME, e))
        return result

    # the type instantiated from the string should be a dict
    obj_type = type(obj)
    assert dict == obj_type

    subject = None
    if _KEY_ID in obj:
        subject = obj[_KEY_ID]
    name_list = []
    if _KEY_NAME in obj:
        # this is a list of dicts
        name_entries = obj[_KEY_NAME]
        obj_type = type(name_entries)
        assert list == obj_type
        for elt in name_entries:
            assert dict == type(elt)

            # single last name, should be a string
            last_name  = elt[_KEY_FAMILY_NAME]
            assert str == type(last_name)

            # list of first name strings
            first_name_list = elt[_KEY_GIVEN_NAME]
            assert list == type(first_name_list)
            for first_name in first_name_list:
                assert str == type(first_name)
                name_list.append( (first_name, last_name))                

    gender = None
    if _KEY_GENDER in obj:
        gender = obj[_KEY_GENDER]
        assert str == type(gender)

    date_of_birth = None
    if _KEY_DOB in obj:
        dob = obj[_KEY_DOB]
        assert str == type(dob)

        # dob is in YYYY-MM-DD format; convert to datetime obj
        date_of_birth = datetime.strptime(dob, '%Y-%m-%d')
            
    patient = PatientResource(
        subject,
        name_list,
        gender,
        date_of_birth
    )

    return patient
    
    
###############################################################################
def _decode_bundle(name, bundle_obj):
    """
    Decode a FHIR bundle object from the JSON data.
    """

    if _TRACE: print('Decoding BUNDLE resource...')

    bundled_objs = []

    # this bundle should be a string representation of a list of dicts
    obj_type = type(bundle_obj)
    assert str == obj_type
    
    try:
        obj = json.loads(bundle_obj)
    except json.decoder.JSONDecodeError as e:
        print('\t{0}: String conversion (bundle) failed with error: "{1}"'.
              format(_MODULE_NAME, e))
        return []

    # now find out what type of obj was created from the string
    obj_type = type(obj)
    assert list == obj_type
    
    for elt in obj:
        obj_type = type(elt)
        assert dict == obj_type
        
        if _KEY_RESOURCE_TYPE in elt:
            resource_type_str = elt[_KEY_RESOURCE_TYPE]
            if _STR_OBSERVATION == resource_type_str:
                observation = _decode_observation(elt)
                bundled_objs.append(observation)
            elif _STR_PROCEDURE == resource_type_str:
                procedure = _decode_procedure(elt)
                bundled_objs.append(procedure)
            elif _STR_CONDITION == resource_type_str:
                condition = _decode_condition(elt)
                bundled_objs.append(condition)
    
    return bundled_objs


###############################################################################
def decode_top_level_obj(obj):
    """
    Decode the outermost object type returned by the FHIR server via the
    CQL wrapper.
    """

    result_obj = None
    
    obj_type = type(obj)
    if dict == obj_type:
        if _TRACE: print('top_level_obj dict keys: {0}'.format(obj.keys()))

        name = None
        if _KEY_NAME in obj:
            name = obj[_KEY_NAME]
        if _KEY_RESULT_TYPE in obj and _KEY_RESULT in obj:
            result_obj = obj[_KEY_RESULT]
            result_type_str = obj[_KEY_RESULT_TYPE]
            
            #if _RESULT_TYPE_CONCEPT == result_type_str:
                # skip the concept, just a string
            #    pass
            if _STR_PATIENT == result_type_str:
                result_obj = _decode_patient(name, result_obj)
                if _TRACE: print('decoded patient')
            elif _STR_BUNDLE == result_type_str:
                result_obj = _decode_bundle(name, result_obj)
            else:
                if _TRACE: print('no decode')
                result_obj = None
    else:
        # don't know what else to expect here
        assert False

    return result_obj
