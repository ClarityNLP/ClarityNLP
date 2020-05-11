#!/usr/bin/env python3
"""
Module used to process JSON results from the FHIR CQL Engine. The CQL Engine
project can be found here:

    https://github.com/gt-health/cql_execution_service
"""

import re
import os
import sys
import json
import base64
import argparse
from collections import namedtuple
from datetime import datetime, timezone, timedelta, time

if __name__ == '__main__':
    # modify path for local testing
    cur_dir = sys.path[0]
    nlp_dir, tail = os.path.split(cur_dir)
    sys.path.append(nlp_dir)
    sys.path.append(os.path.join(nlp_dir, 'algorithms', 'finder'))    
    import time_finder    
    from flatten import flatten
else:
    from data_access.flatten import flatten
    from algorithms.finder import time_finder

from claritynlp_logging import log, ERROR, DEBUG
    
# exported for result display
KEY_VALUE_NAME    = 'value_name'
KEY_VALUE         = 'value'
KEY_UNITS         = 'unit'
KEY_DATE_TIME     = 'date_time'
KEY_END_DATE_TIME = 'end_date_time'
    
_VERSION_MAJOR = 0
_VERSION_MINOR = 11
_MODULE_NAME   = 'cql_result_parser.py'

# set to True to enable debug output
_TRACE = False

# regex used to recognize components of datetime strings
_str_datetime = r'\A(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<day>\d\d)' \
    r'(T(?P<time>\d\d:\d\d:\d\d[-+\.Z\d:]*))?\Z'
_regex_datetime = re.compile(_str_datetime)

_regex_coding = re.compile(r'\Acode_coding_(?P<num>\d)_')

_KEY_END         = 'end'
_KEY_START       = 'start'
_KEY_SUBJECT     = 'subject'
_KEY_PATIENT_REF = 'patient_reference'
_KEY_SUBJECT_REF = 'subject_reference'
_KEY_EDT         = 'effectiveDateTime'
_KEY_EP_START    = 'effectivePeriod_start'
_KEY_EP_END      = 'effectivePeriod_end'
_KEY_RESULT      = 'result'

_STR_RESOURCE_TYPE = 'resourceType'
_CHAR_FWDSLASH = '/'


###############################################################################
def enable_debug():

    global _TRACE
    _TRACE = True


###############################################################################
def _dump_dict(dict_obj, msg=None):
    """
    Print the key-value pairs for the given dict to stdout.
    """

    assert dict == type(dict_obj)

    if msg is not None:
        log(msg)
    for k,v in dict_obj.items():
        if k.endswith('div'):
            log('\t{0} => {1}...'.format(k, v[:16]))
        else:
            log('\t{0} => {1}'.format(k, v))

    
###############################################################################
def _convert_datetimes(flattened_obj):
    """
    Convert FHIR datetimes to python datetime objects. The input is a flattened
    JSON representation of a FHIR resource.
    """

    assert dict == type(flattened_obj)
    
    for k,v in flattened_obj.items():
        if str == type(v):
            match = _regex_datetime.match(v)
            if match:
                year  = int(match.group('year'))
                month = int(match.group('month'))
                day   = int(match.group('day'))
                time_str = match.group('time')

                if time_str is None:
                    datetime_obj = datetime(
                        year  = year,
                        month = month,
                        day   = day
                    )
                else:
                    json_time = time_finder.run(time_str)
                    time_list = json.loads(json_time)
                    assert 1 == len(time_list)
                    the_time = time_list[0]
                    time_obj = time_finder.TimeValue(**the_time)

                    us = 0
                    if time_obj.fractional_seconds is not None:
                        # convert to int and keep us resolution
                        frac_seconds = int(time_obj.fractional_seconds)
                        us = frac_seconds % 999999

                    # get correct sign for UTC offset
                    mult = 1
                    if time_obj.gmt_delta_sign is not None:
                        if '-' == time_obj.gmt_delta_sign:
                            mult = -1
                    delta_hours = 0
                    if time_obj.gmt_delta_hours is not None:
                        delta_hours = mult * time_obj.gmt_delta_hours
                    delta_min = 0
                    if time_obj.gmt_delta_minutes is not None:
                        delta_min   = time_obj.gmt_delta_minutes
                    offset = timedelta(
                        hours=delta_hours,
                        minutes = delta_min
                    )
                
                    datetime_obj = datetime(
                        year        = year,
                        month       = month,
                        day         = day,
                        hour        = time_obj.hours,
                        minute      = time_obj.minutes,
                        second      = time_obj.seconds,
                        microsecond = us,
                        tzinfo      = timezone(offset=offset)
                    )

                flattened_obj[k] = datetime_obj
                
    return flattened_obj


###############################################################################
def _set_list_length(obj, prefix_str):
    """
    Determine the length of a flattened list whose element keys share the
    given prefix string. Add a new key of the form 'len_' + prefix_str that
    contains this length.
    """

    str_search = r'\A' + prefix_str + r'_(?P<num>\d+)_?'

    max_num = None
    for k,v in obj.items():
        match = re.match(str_search, k)
        if match:
            num = int(match.group('num'))
            if max_num is None:
                max_num = 0
            if num > max_num:
                max_num = num

    if max_num is None:
        return 0
    else:
        length = max_num + 1
        obj['len_' + prefix_str] = length
        return length


###############################################################################
def _base_init(obj):
    """
    Initialize list lengths in the base resource objects.
    """

    identifier_count = _set_list_length(obj, 'identifier')
    for i in range(identifier_count):
        key_name = 'identifier_{0}_type_coding'.format(i)
        _set_list_length(obj, key_name)

    for field in ['extension', 'modifierExtension']:
        count = _set_list_length(obj, field)
        for i in range(count):
            key_name = '{0}_{1}_valueCodeableConcept_coding'.format(field, i)
            _set_list_length(obj, key_name)
            key_name = '{0}_{1}_valueTiming_event'.format(field, i)
            _set_list_length(obj, key_name)
            key_name = '{0}_{1}_valueTiming_code_coding'.format(field, i)
            _set_list_length(obj, key_name)
            key_name = '{0}_{1}_valueAddress_line'.format(field, i)
            _set_list_length(obj, key_name)
            for hn_field in ['family', 'given', 'prefix', 'suffix']:
                key_name = '{0}_{1}_valueHumanName_{2}'.format(field, i, hn_field)
                _set_list_length(obj, key_name)
            key_name = '{0}_{1}_valueSignature_type_coding'.format(field, i)
            _set_list_length(obj, key_name)
            # set lengths of inner extension lists
            key_name = '{0}_{1}_extension'.format(field, i)
            _set_list_length(obj, key_name)
        

###############################################################################        
def _contained_med_resource_init(obj):
    """
    Process a flattened FHIR Medication resource, which appears only as a
    contained resource inside other FHIR resources. 
    """

    contained_count = _set_list_length(obj, 'contained')
    for i in range(contained_count):
        for field in [
                'code_coding', 'product_form', 'product_ingredient',
                'product_batch', 'package_container_coding',
                'package_content']:
            key_name = 'contained_{0}_{1}'.format(i, field)
            _set_list_length(obj, key_name)

    # DSTU3
    for i in range(contained_count):
        for field in ['form_coding', 'package_batch', 'image']:
            key_name = 'contained_{0}_{1}'.format(i, field)
            _set_list_length(obj, key_name)

        key_name = 'contained_{0}_ingredient'.format(i)
        ingredient_count = _set_list_length(obj, key_name)
        for j in range(ingredient_count):
            key2_name = '{0}_{1}_itemCodeableConcept_coding'.format(key_name, j)
            len_k = _set_list_length(obj, key2_name)
        key_name = 'contained_{0}_package_container_coding'.format(i)
        _set_list_length(obj, key_name)
        key_name = 'contained_{0}_package_content'.format(i)
        len_j = _set_list_length(obj, key_name)
        for j in range(len_j):
            key2_name = '{0}_{1}_coding'.format(key_name, j)
            _set_list_length(obj, key2_name)
    

###############################################################################
def _set_dosage_fields(obj, dosage_field_name):
    """
    Set list lengths for a FHIR DSTU3 Dosage embedded resource.
    """

    dosage_count = _set_list_length(obj, dosage_field_name)
    for i in range(dosage_count):
        key_name = '{0}_{1}_additionalInstruction'.format(dosage_field_name, i)
        count_j = _set_list_length(obj, key_name)
        for j in range(count_j):
            key2_name = '{0}_{1}_coding'.format(key_name, j)
            _set_list_length(obj, key2_name)
        for field in ['site', 'route', 'method']:
            key_name = '{0}_{1}_{2}_coding'.format(dosage_field_name, i, field)
            _set_list_length(obj, key_name)
        

###############################################################################
def _process_datetime(obj):
    """
    Process a FHIR datetime resource.
    """

    _KEY_RESULT = 'result'
    
    assert dict == type(obj)

    # flatten the JSON and convert the timestring
    flattened_dt = flatten(obj)
    flattened_dt = _convert_datetimes(flattened_dt)

    # add 'date_time' field for time sorting
    if _KEY_RESULT in obj:
        dt = obj[_KEY_RESULT]
        obj[KEY_DATE_TIME] = dt
    
    if _TRACE:
        _dump_dict(flattened_dt, 'Flattened dateTime resource: ')

    return flattened_dt
    
    
###############################################################################
def _process_string(obj):
    """
    Process a FHIR string resource.
    """

    assert dict == type(obj)

    # flatten the JSON
    flattened_string = flatten(obj)
    
    if _TRACE:
        _dump_dict(flattened_string, 'Flattened string resource: ')

    return flattened_string
    
            
###############################################################################
def _process_observation(obj):
    """
    Process a flattened FHIR 'Observation' resource.
    """

    assert dict == type(obj)

    if _TRACE:
        _dump_dict(obj, '[BEFORE]: Flattened Observation: ')
    
    # add 'date_time' field for time sorting
    if _KEY_EDT in obj:
        edt = obj[_KEY_EDT]
        obj[KEY_DATE_TIME] = edt
    if _KEY_EP_START in obj:
        start = obj[_KEY_EP_START]
        obj[KEY_DATE_TIME] = start
    if _KEY_EP_END in obj:
        end = obj[_KEY_EP_END]
        obj[KEY_END_DATE_TIME] = end

    _base_init(obj)
    _set_list_length(obj, 'category_coding')
    _set_list_length(obj, 'code_coding')
    _set_list_length(obj, 'performer')
    _set_list_length(obj, 'valueCodeableConcept_coding')
    _set_list_length(obj, 'dataAbsentReason_coding')
    _set_list_length(obj, 'interpretation_coding')
    _set_list_length(obj, 'bodySite_coding')
    _set_list_length(obj, 'method_coding')
    rr_count = _set_list_length(obj, 'referenceRange')
    for i in range(rr_count):
        key = 'referenceRange_{0}_meaning_coding'.format(i)
        _set_list_length(obj, key)
    component_count = _set_list_length(obj, 'component')
    for i in range(component_count):
        for field in ['code_coding',
                      'valueCodeableConcept_coding',
                      'dataAbsentReason_coding',
                      'referenceRange']:
            key = 'component_{0}_{1}'.format(i, field)
            _set_list_length(obj, key)

    # DSTU3
    # could have a contained Patient resource - TBD
    _set_list_length(obj, 'basedOn')
    category_count = _set_list_length(obj, 'category')
    for i in range(category_count):
        key_name = 'category_{0}_coding'.format(i)
        _set_list_length(obj, key_name)
    for i in range(rr_count):
        key_name = 'referenceRange_{0}_appliesTo'.format(i)
        applies_to_count = _set_list_length(obj, key)
        for j in range(applies_to_count):
            key2_name = '{0}_{1}_coding'.format(key_name, j)
            _set_list_length(obj, key2_name)
    for i in range(component_count):
        key_name = 'component_{0}_interpretation_coding'.format(i)
        _set_list_length(obj, key_name)
            
    # set value and units for result display
    KEY_VQ    = 'valueQuantity_value'
    KEY_VU    = 'valueQuantity_unit'
    KEY_VS    = 'valueString'
    KEY_DISP  = 'code_text'
    KEY_DISP2 = 'code_coding_0_display'
    if KEY_VQ in obj:
        obj[KEY_VALUE] = obj[KEY_VQ]
    if KEY_VU in obj:
        obj[KEY_UNITS] = obj[KEY_VU]

    if KEY_VS in obj:
        obj[KEY_VALUE] = obj[KEY_VS]

    if KEY_DISP in obj:
        obj[KEY_VALUE_NAME] = obj[KEY_DISP]
    elif KEY_DISP2 in obj:
        obj[KEY_VALUE_NAME] = obj[KEY_DISP2]

    # set patient id
    if _KEY_SUBJECT_REF in obj:
        subject_ref = obj[_KEY_SUBJECT_REF]
        if _CHAR_FWDSLASH in subject_ref:
            resource_type, patient_id = subject_ref.split(_CHAR_FWDSLASH)
        else:
            resource_type = subject_ref
            patient_id = None
        obj[_KEY_SUBJECT] = patient_id
        
    if _TRACE:
        _dump_dict(obj, '[AFTER] Flattened Observation: ')
            
    return obj


###############################################################################
def _process_medication_administration(obj):
    """
    Process a flattened FHIR 'MedicationAdministration' resource.
    """

    assert dict == type(obj)

    if _TRACE:
        _dump_dict(obj, '[BEFORE]: Flattened MedicationAdministration: ')
    
    # add fields for time sorting (DSTU2)
    KEY_EDT = 'effectiveTimeDateTime'
    KEY_EP_START = 'effectiveTimePeriod_start'
    KEY_EP_END   = 'effectiveTimePeriod_end'
    if KEY_EDT in obj:
        edt = obj[KEY_EDT]
        obj[KEY_DATE_TIME] = edt
    if KEY_EP_START in obj:
        start = obj[KEY_EP_START]
        obj[KEY_DATE_TIME] = start
    if KEY_EP_END in obj:
        end = obj[KEY_EP_END]
        obj[KEY_END_DATE_TIME] = end

    # STU3
    if _KEY_EDT in obj:
        edt = obj[_KEY_EDT]
        obj[KEY_DATE_TIME] = edt
    if _KEY_EP_START in obj:
        start = obj[_KEY_EP_START]
        obj[KEY_DATE_TIME] = start
    if _KEY_EP_END in obj:
        end = obj[_KEY_EP_END]
        obj[KEY_END_DATE_TIME] = end
        
    _base_init(obj)
    _contained_med_resource_init(obj)
    
    reason_count = _set_list_length(obj, 'reasonNotGiven')
    for i in range(reason_count):
        key = 'reasonNotGiven_{0}_coding'
        _set_list_length(obj, key)
    reason_count = _set_list_length(obj, 'reasonGiven')
    for i in range(reason_count):
        key = 'reasonGiven_{0}_coding'
        _set_list_length(obj, key)
    _set_list_length(obj, 'medicationCodeableConcept_coding')
    _set_list_length(obj, 'device')
    _set_list_length(obj, 'dosage_siteCodeableConcept_coding')
    _set_list_length(obj, 'dosage_route_coding')
    _set_list_length(obj, 'dosage_method_coding')

    # DSTU3
    _set_list_length(obj, 'definition')
    _set_list_length(obj, 'partOf')
    _set_list_length(obj, 'category_coding')
    _set_list_length(obj, 'supportingInformation')
    _set_list_length(obj, 'performer')
    reason_count = _set_list_length(obj, 'reasonCode')
    for i in range(reason_count):
        key_name = 'reasonCode_{0}_coding'.format(i)
        _set_list_length(obj, key_name)
    _set_list_length(obj, 'reasonReference')
    _set_list_length(obj, 'note')
    _set_list_length(obj, 'eventHistory')
    
    # set data for result display
    KEY_DISP = 'medicationCodeableConcept_coding_0_display'
    if KEY_DISP in obj:
        obj[KEY_VALUE_NAME] = obj[KEY_DISP]
    else:
        KEY_REF = 'medicationReference_display'
        if KEY_REF in obj:
            obj[KEY_VALUE_NAME] = obj[KEY_REF]

    # set patient id
    if _KEY_PATIENT_REF in obj:
        patient_ref = obj[_KEY_PATIENT_REF]
        if _CHAR_FWDSLASH in patient_ref:
            resource_type, patient_id = patient_ref.split(_CHAR_FWDSLASH)
        else:
            resource_type = patient_ref
            patient_id = None
        obj[_KEY_SUBJECT] = patient_id
            
    if _TRACE:
        _dump_dict(obj, '[AFTER]: Flattened MedicationAdministration: ')

    return obj


###############################################################################
def _process_medication_request(obj):
    """
    Process a flattened FHIR 'MedicationRequest' resource.
    """

    assert dict == type(obj)

    if _TRACE:
        _dump_dict(obj, '[BEFORE]: Flattened MedicationRequest: ')
    
    # add fields for time sorting
    KEY_DW = 'authoredOn'
    if KEY_DW in obj:
        dw = obj[KEY_DW]
        obj[KEY_DATE_TIME] = dw

    _base_init(obj)
    _contained_med_resource_init(obj)

    _set_list_length(obj, 'definition')
    _set_list_length(obj, 'basedOn')
    _set_list_length(obj, 'groupIdentifier_type_coding')
    _set_list_length(obj, 'category_coding')
    _set_list_length(obj, 'medicationCodeableConcept_coding')
    _set_list_length(obj, 'supportingInformation')
    rc_count = _set_list_length(obj, 'reasonCode')
    for i in range(rc_count):
        key_name = 'reasonCode_{0}_coding'.format(i)
        _set_list_length(obj, key_name)
    _set_list_length(obj, 'reasonReference')
    _set_list_length(obj, 'note')
    _set_dosage_fields(obj, 'dosageInstruction')
    _set_list_length(obj, 'detectedIssue')
    _set_list_length(obj, 'eventHistory')
    
    # set data for result display
    KEY_DISP = 'medicationCodeableConcept_coding_0_display'
    if KEY_DISP in obj:
        obj[KEY_VALUE_NAME] = obj[KEY_DISP]
    else:
        KEY_REF = 'medicationReference_display'
        if KEY_REF in obj:
            obj[KEY_VALUE_NAME] = obj[KEY_REF]

    # set patient id
    if _KEY_PATIENT_REF in obj:
        patient_ref = obj[_KEY_PATIENT_REF]
        if _CHAR_FWDSLASH in patient_ref:
            resource_type, patient_id = patient_ref.split(_CHAR_FWDSLASH)
        else:
            resource_type = patient_ref
            patient_id = None
        obj[_KEY_SUBJECT] = patient_id
    
    if _TRACE:
        _dump_dict(obj, '[AFTER]: Flattened MedicationRequest: ')

    return obj

    
###############################################################################
def _process_medication_order(obj):
    """
    Process a flattened FHIR 'MedicationOrder' resource.
    """

    assert dict == type(obj)

    if _TRACE:
        _dump_dict(obj, '[BEFORE]: Flattened MedicationOrder: ')
    
    # add fields for time sorting
    KEY_DW = 'dateWritten'
    if KEY_DW in obj:
        dw = obj[KEY_DW]
        obj[KEY_DATE_TIME] = dw

    KEY_DE = 'dateEnded'
    if KEY_DE in obj:
        de = obj[KEY_DE]
        obj[KEY_END_DATE_TIME] = de

    _base_init(obj)
    _contained_med_resource_init(obj)
    
    _set_list_length(obj, 'reasonEnded_coding')
    _set_list_length(obj, 'reasonCodeableConcept_coding')
    _set_list_length(obj, 'medicationCodeableConcept_coding')
    inst_count = _set_list_length(obj, 'dosageInstruction')
    for i in range(inst_count):
        for field in ['additionalInstructions_coding',
                      'timing_code_coding',
                      'asNeededCodeableConcept_coding',
                      'siteCodeableConcept_coding',
                      'route_coding', 'method_coding']:
            key = 'dosageInstruction_{0}_{1}'.format(i, field)
            _set_list_length(obj, key)
    _set_list_length(obj, 'dispenseRequest_medicationCodeableConcept_coding')
    _set_list_length(obj, 'substitution_type_coding')
    _set_list_length(obj, 'substitution_reason_coding')

    # set data for result display
    KEY_DISP = 'medicationCodeableConcept_coding_0_display'
    if KEY_DISP in obj:
        obj[KEY_VALUE_NAME] = obj[KEY_DISP]
    else:
        KEY_REF = 'medicationReference_display'
        if KEY_REF in obj:
            obj[KEY_VALUE_NAME] = obj[KEY_REF]

    # set patient id
    if _KEY_PATIENT_REF in obj:
        patient_ref = obj[_KEY_PATIENT_REF]
        if _CHAR_FWDSLASH in patient_ref:
            resource_type, patient_id = patient_ref.split(_CHAR_FWDSLASH)
        else:
            resource_type = patient_ref
            patient_id = None
        obj[_KEY_SUBJECT] = patient_id
    
    if _TRACE:
        _dump_dict(obj, '[AFTER]: Flattened MedicationOrder: ')

    return obj
                

###############################################################################
def _process_medication_statement(obj):
    """
    Process a flattened FHIR 'MedicationStatement' resource.
    """

    assert dict == type(obj)

    if _TRACE:
        _dump_dict(obj, '[BEFORE]: Flattened Medication Statement: ')    

    # add fields for time sorting
    KEY_DA = 'dateAsserted'
    if KEY_DA in obj:
        da = obj[KEY_DA]
        obj[KEY_DATE_TIME] = da
    
    _base_init(obj)
    _contained_med_resource_init(obj)
    
    reason_count = _set_list_length(obj, 'reasonNotTaken')
    for i in range(reason_count):
        key = 'reason_{0}_coding'
        _set_list_length(obj, key)
    _set_list_length(obj, 'reasonForUseCodeableConcept_coding')
    _set_list_length(obj, 'supportingInformation')
    _set_list_length(obj, 'medicationCodeableConcept_coding')
    dosage_count = _set_list_length(obj, 'dosage')
    for i in range(dosage_count):
        for field in ['asNeededCodeableConcept_coding',
                      'siteCodeableConcept_coding',
                      'route_coding', 'method_coding']:
            key = 'dosage_{0}_{1}'.format(i, field)
            _set_list_length(obj, key)

    # DSTU3 only
    _set_list_length(obj, 'basedOn')
    _set_list_length(obj, 'partOf')
    category_count = _set_list_length(obj, 'category')
    for i in range(category_count):
        key_name = 'category_{0}_coding'.format(i)
        _set_list_length(obj, key_name)
    _set_list_length(obj, 'derivedFrom')
    reason_code_count = _set_list_length(obj, 'reasonCode')
    for i in range(reason_code_count):
        key_name = 'reasonCode_{0}_coding'.format(i)
        _set_list_length(obj, key_name)
    reason_ref_count = _set_list_length(obj, 'reasonReference')
    _set_list_length(obj, 'note')
    for i in range(dosage_count):
        key_name = 'dosage_{0}_additionalInstruction'.format(i)
        count_j = _set_list_length(obj, key_name)
        for j in range(count_j):
            key2_name = '{0}_{1}_coding'.format(key_name, j)
            _set_list_length(obj, key2_name)
        key_name = 'site_{0}_coding'.format(i)
        _set_list_length(obj, key_name)
    
    # set data for result display
    KEY_DISP = 'medicationCodeableConcept_coding_0_display'
    if KEY_DISP in obj:
        obj[KEY_VALUE_NAME] = obj[KEY_DISP]
    else:
        KEY_REF = 'medicationReference_display'
        if KEY_REF in obj:
            obj[KEY_VALUE_NAME] = obj[KEY_REF]

    # set patient id
    if _KEY_PATIENT_REF in obj:
        patient_ref = obj[_KEY_PATIENT_REF]
        if _CHAR_FWDSLASH in patient_ref:
            resource_type, patient_id = patient_ref.split(_CHAR_FWDSLASH)
        else:
            resource_type = patient_ref
            patient_id = None
        obj[_KEY_SUBJECT] = patient_id
                
    if _TRACE:
        _dump_dict(obj, '[AFTER]: Flattened Medication Statement: ')

    return obj


###############################################################################
def _process_condition(obj):
    """
    Process a flattened FHIR 'Condition' resource.
    """

    assert dict == type(obj)

    if _TRACE:
        _dump_dict(obj, '[BEFORE]: Flattened Condition: ')    

    KEY_ODT      = 'onsetDateTime'
    KEY_OP_START = 'onsetPeriod_start'
    KEY_ADT      = 'abatementDateTime'
    KEY_AP_END   = 'abatementPeriod_end'

    # add fields for time sorting
    if KEY_ODT in obj:
        odt = obj[KEY_ODT]
        obj[KEY_DATE_TIME] = odt
    if KEY_ADT in obj:
        adt = obj[KEY_ADT]
        obj[KEY_END_DATE_TIME] = adt

    if KEY_OP_START in obj:
        start = obj[KEY_OP_START]
        obj[KEY_DATE_TIME] = start
    if KEY_AP_END in obj:
        end = obj[KEY_AP_END]
        obj[KEY_END_DATE_TIME] = end
    
    _base_init(obj)
    _set_list_length(obj, 'code_coding')
    _set_list_length(obj, 'category_coding')
    _set_list_length(obj, 'severity_coding')
    _set_list_length(obj, 'stage_assessment')
    evidence_len = _set_list_length(obj, 'evidence')
    for i in range(evidence_len):
        for field in ['code_coding', 'detail']:
            key = 'evidence_{0}_{1}'.format(i, field)
            _set_list_length(obj, key)
    site_count = _set_list_length(obj, 'bodySite')
    for i in range(site_count):
        key_name = 'bodySite_{0}_coding'.format(i)
        _set_list_length(obj, key_name)

    # DSTU3 only
    category_count = _set_list_length(obj, 'category')
    for i in range(category_count):
        key_name = 'category_{0}_coding'.format(i)
        _set_list_length(obj, key_name)
    for i in range(evidence_len):
        key_name = 'evidence_{0}_code'.format(i)
        code_len = _set_list_length(obj, key_name)
        for j in range(code_len):
            key2_name = '{0}_{1}_coding'.format(key_name, j)
            coding_len = _set_list_length(obj, key2_name)
            for k in range(coding_len):
                key3_name = '{0}_{1}_coding'.format(key2_name, k)
                _set_list_length(obj, key3_name)
    note_count = _set_list_length(obj, 'note')
        
    # set data for result display
    KEY_DISP = 'code_coding_0_display'
    if KEY_DISP in obj:
        obj[KEY_VALUE_NAME] = obj[KEY_DISP]

    # set patient id
    if _KEY_PATIENT_REF in obj:
        patient_ref = obj[_KEY_PATIENT_REF]
        if _CHAR_FWDSLASH in patient_ref:
            resource_type, patient_id = patient_ref.split(_CHAR_FWDSLASH)
        else:
            resource_type = patient_ref
            patient_id = None
        obj[_KEY_SUBJECT] = patient_id
        
    if _TRACE:
        _dump_dict(obj, '[AFTER]: Flattened Condition: ')

    return obj
    

###############################################################################
def _process_encounter(obj):
    """
    Process a FHIR 'Ecounter resource.
    """

    assert dict == type(obj)
    
    if _TRACE:
        _dump_dict(obj, '[BEFORE]: Flattened Encounter: ')

    # add fields for time sorting
    
    KEY_PS = 'period_start'
    KEY_PE = 'period_end'
    if KEY_PS in obj:
        start = obj[KEY_PS]
        obj[KEY_DATE_TIME] = start
    if KEY_PE in obj:
        end = obj[KEY_PE]
        obj[KEY_END_DATE_TIME] = end

    _base_init(obj)
    _set_list_length(obj, 'statusHistory')
    count = _set_list_length(obj, 'type')
    for i in range(count):
        key_name = 'type_{0}_coding'.format(i)
        _set_list_length(obj, key_name)
    
    _set_list_length(obj, 'episodeOfCare')
    _set_list_length(obj, 'incomingReferral')
    participant_count = _set_list_length(obj, 'participant')
    for i in range(participant_count):
        key_name = 'participant_{0}_type'.format(i)
        type_count = _set_list_length(obj, key_name)
        for j in range(type_count):
            key2_name = '{0}_{1}_{2}'.format(key_name, j, 'coding')
            _set_list_length(obj, key2_name)
    _set_list_length(obj, 'priority_coding')
    reason_count = _set_list_length(obj, 'reason')
    for i in range(reason_count):
        key_name = 'reason_{0}_coding'.format(i)
        _set_list_length(obj, key_name)
    _set_list_length(obj, 'indication')
    _set_list_length(obj, 'hospitalization_admitSource_coding')
    _set_list_length(obj, 'hospitalization_admittingDiagnosis')
    _set_list_length(obj, 'hospitalization_reAdmission_coding')
    hdp_count = _set_list_length(obj, 'hospitalization_dietPreference')
    for i in range(hdp_count):
        key_name = 'hospitalization_dietPreference_{0}_coding'.format(i)
        _set_list_length(obj, key_name)
    sc_count = _set_list_length(obj, 'hospitalization_specialCourtesy')
    for i in range(sc_count):
        key_name = 'hospitalization_specialCourtesy_{0}_coding'.format(i)
        _set_list_length(obj, key_name)
    sa_count = _set_list_length(obj, 'hospitalization_specialArrangement')
    for i in range(sa_count):
        key_name = 'hospitalization_specialArrangement_{0}_coding'.format(i)
        _set_list_length(obj, key_name)
    _set_list_length(obj, 'hospitalization_dischargeDiagnosis')
    coding_count = _set_list_length(obj, 'hospitalization_dischargeDisposition_coding')
    _set_list_length(obj, 'location')

    _set_list_length(obj, 'classHistory')
    _set_list_length(obj, 'account')
    count = _set_list_length(obj, 'diagnosis')
    for i in range(count):
        key_name = 'diagnosis_{0}_role_coding'.format(i)
        _set_list_length(obj, key_name)
    
    if _TRACE:
        _dump_dict(obj, '[AFTER]: Flattened Encounter: ')

    return obj


###############################################################################
def _process_procedure(obj):
    """
    Process a flattened FHIR 'Procedure' resource.
    """

    assert dict == type(obj)

    if _TRACE:
        _dump_dict(obj, '[BEFORE]: Flattened Procedure: ')

    # add fields for time sorting
    KEY_PDT = 'performedDateTime'
    KEY_PP_START = 'performedPeriod_start'
    KEY_PP_END   = 'performedPeriod_end'
    if KEY_PDT in obj:
        # only a single timestamp
        pdt = obj[KEY_PDT]
        obj[KEY_DATE_TIME] = pdt
    if KEY_PP_START in obj:
        start = obj[KEY_PP_START]
        obj[KEY_DATE_TIME] = start
    if KEY_PP_END in obj:
        end = obj[KEY_PP_END]
        obj[KEY_END_DATE_TIME] = end
    
    _base_init(obj)
    _contained_med_resource_init(obj)

    _set_list_length(obj, 'category_coding')
    _set_list_length(obj, 'code_coding')
    _set_list_length(obj, 'reasonNotPerformed_coding')
    site_count = _set_list_length(obj, 'bodySite')
    for i in range(site_count):
        key_name = 'bodySite_{0}_coding'.format(i)
        _set_list_length(obj, key_name)
    _set_list_length(obj, 'reasonCodeableConcept_coding')
    performer_count = _set_list_length(obj, 'performer')
    for i in range(performer_count):
        key_name = 'performer_{0}_role_coding'.format(i)
        _set_list_length(obj, key_name)
    _set_list_length(obj, 'outcome_coding')
    _set_list_length(obj, 'report')
    complication_count = _set_list_length(obj, 'complication')
    for i in range(complication_count):
        key_name = 'complication_{0}_coding'.format(i)
        _set_list_length(obj, key_name)
    followup_count = _set_list_length(obj, 'followUp')
    for i in range(followup_count):
        key_name = 'followUp_{0}_coding'.format(i)
        _set_list_length(obj, key_name)
    _set_list_length(obj, 'notes')
    device_count = _set_list_length(obj, 'focalDevice')
    for i in range(device_count):
        key_name = 'focalDevice_{0}_action_coding'.format(i)
        _set_list_length(obj, key_name)
    _set_list_length(obj, 'used')

    # DSTU3 only
    _set_list_length(obj, 'definition')
    _set_list_length(obj, 'basedOn')
    _set_list_length(obj, 'partOf')
    _set_list_length(obj, 'reasonNotDone_coding')
    reason_count = _set_list_length(obj, 'reasonCode')
    for i in range(reason_count):
        key_name = 'reasonCode_{0}_coding'.format(i)
        _set_list_length(obj, key_name)
    _set_list_length(obj, 'reasonReference')
    _set_list_length(obj, 'complicationDetail')
    _set_list_length(obj, 'note')
    used_code_count = _set_list_length(obj, 'usedCode')
    for i in range(used_code_count):
        key_name = 'usedCode_{0}_coding'.format(i)
        _set_list_length(obj, key_name)
    
    # set data for result display
    KEY_DISP = 'code_coding_0_display'
    if KEY_DISP in obj:
        obj[KEY_VALUE_NAME] = obj[KEY_DISP]

    # set patient ID
    if _KEY_SUBJECT_REF in obj:
        subject_ref = obj[_KEY_SUBJECT_REF]
        if _CHAR_FWDSLASH in subject_ref:
            resource_type, patient_id = subject_ref.split(_CHAR_FWDSLASH)
        else:
            resource_type = subject_ref
            patient_id = None
        obj[_KEY_SUBJECT] = patient_id
    
    if _TRACE:
        _dump_dict(obj, '[AFTER]: Flattened Procedure: ')

    return obj
        
        
###############################################################################
def _process_patient(obj):
    """
    Process a FHIR 'Patient' resource.
    """

    obj_type = type(obj)
    if str == obj_type:
        
        # not flattened yet
        try:
            obj = json.loads(obj)
        except json.decoder.JSONDecoderError as e:
            log('\t{0}: String conversion (patient) failed with error: "{1}"'.
                  format(_MODULE_NAME, e))
            return result

        # the type instantiated from the string should be a dict
        obj_type = type(obj)
        
    assert dict == obj_type

    flattened_patient = flatten(obj)
    flattened_patient = _convert_datetimes(flattened_patient)

    if _TRACE:
        _dump_dict(flattened_patient, '[BEFORE] Flattened Patient resource: ')
    
    _base_init(flattened_patient)

    name_count = _set_list_length(flattened_patient, 'name')
    for i in range(name_count):
        for field in ['family', 'given', 'prefix', 'suffix']:
            key_name = 'name_{0}_{1}'.format(i, field)
            count = _set_list_length(flattened_patient, key_name)
            for j in range(count):
                key = '{0}_{1}'.format(key_name, j)
                _set_list_length(flattened_patient, key)

    _set_list_length(flattened_patient, 'telecom')
    addr_count = _set_list_length(flattened_patient, 'address')
    for i in range(addr_count):
        key_name = 'address_{0}_line'.format(i)
        _set_list_length(flattened_patient, key_name)

    _set_list_length(flattened_patient, 'maritalStatus_coding')
    
    contact_count = _set_list_length(flattened_patient, 'contact')
    for i in range(contact_count):
        for field in ['relationship', 'telecom']:
            key_name = 'contact_{0}_{1}'.format(i, field)
            count = _set_list_length(flattened_patient, key_name)
            for j in range(count):
                key = '{0}_{1}_coding'.format(key_name, j)
                _set_list_length(flattened_patient, key)

    _set_list_length(flattened_patient, 'animal_species_coding')
    _set_list_length(flattened_patient, 'animal_breed_coding')
    _set_list_length(flattened_patient, 'animal_genderStatus_coding')    

    comm_count = _set_list_length(flattened_patient, 'communication')
    for i in range(comm_count):
        key_name = 'communication_{0}_language_coding'.format(i)
        _set_list_length(flattened_patient, key_name)

    # DSTU2 uses 'careProvider'; DSTU3 uses 'generalPractitioner'
    _set_list_length(flattened_patient, 'careProvider')
    _set_list_length(flattened_patient, 'generalPractitioner')
    
    _set_list_length(flattened_patient, 'link')

    # set data for result display
    family = ''
    if 'name_0_family' in flattened_patient:
        family = flattened_patient['name_0_family']
    elif 'name_0_family_0' in flattened_patient:
        family = flattened_patient['name_0_family_0']
    given = ''
    if 'name_0_given' in flattened_patient:
        given = flattened_patient['name_0_given']
    elif 'name_0_given_0' in flattened_patient:
        given = flattened_patient['name_0_given_0']
    name = '{0}, {1}'.format(family, given)
    flattened_patient[KEY_VALUE_NAME] = name

    # set 'subject' field to the patient_id
    if 'id' in flattened_patient:
        flattened_patient[_KEY_SUBJECT] = str(flattened_patient['id'])
    
    if _TRACE:
        _dump_dict(flattened_patient, '[AFTER] Flattened Patient resource: ')

    return flattened_patient


###############################################################################
def _process_resource(obj):
    """
    Flatten and process FHIR resources of the indicated types.
    """

    obj_type = type(obj)
    assert dict == obj_type

    # flatten the JSON, convert time strings to datetimes
    flattened_obj = flatten(obj)
    flattened_obj = _convert_datetimes(flattened_obj)

    # read the resource type and process accordingly
    result = None
    if _STR_RESOURCE_TYPE in flattened_obj:
        rt = obj[_STR_RESOURCE_TYPE]
##        if 'Patient' == rt:
##            result = _process_patient(flattened_obj)
        if 'Encounter' == rt:
            result = _process_encounter(flattened_obj)
        elif 'Observation' == rt:
            result = _process_observation(flattened_obj)
        elif 'Procedure' == rt:
            result = _process_procedure(flattened_obj)
        elif 'Condition' == rt:
            result = _process_condition(flattened_obj)
        elif 'MedicationStatement' == rt:
            result = _process_medication_statement(flattened_obj)
        elif 'MedicationOrder' == rt:
            result = _process_medication_order(flattened_obj)
        elif 'MedicationRequest' == rt:
            result = _process_medication_request(flattened_obj)
        elif 'MedicationAdministration' == rt:
            result = _process_medication_administration(flattened_obj)

    return result
    

###############################################################################
def _process_bundle(name, bundle_obj, result_type_str):
    """
    Process a DSTU2 or DSTU3 resource bundle returned from the CQL Engine.
    """

    if _TRACE: log('Decoding BUNDLE resource...')

    # this bundle should be a string representation of a list of dicts
    obj_type = type(bundle_obj)
    assert str == obj_type
    
    try:
        obj = json.loads(bundle_obj)
    except json.decoder.JSONDecodeError as e:
        log('\t{0}: String conversion (bundle) failed with error: "{1}"'.
              format(_MODULE_NAME, e))
        return []

    # now find out what type of obj was created from the string
    obj_type = type(obj)
    assert list == obj_type

    rts = result_type_str.lower()
    
    bundled_objs = []    
    for elt in obj:
        if rts.endswith('stu2') or rts.endswith('stu3'):
            result = _process_resource(elt)
        if result is not None:
            bundled_objs.append(result)
    
    return bundled_objs


###############################################################################
def decode_top_level_obj(obj):
    """
    Decode the outermost object type returned by the CQL Engine and process
    accordingly.
    """

    KEY_NAME        = 'name'
    KEY_RESULT      = 'result'
    KEY_RESULT_TYPE = 'resultType'
    STR_PATIENT     = 'patient'
    STR_STR         = 'string'
    STR_DT          = 'datetime'
    
    result_obj = None
    
    obj_type = type(obj)
    if dict == obj_type:
        if _TRACE: log('top_level_obj dict keys: {0}'.format(obj.keys()))

        name = None
        if KEY_NAME in obj:
            name = obj[KEY_NAME]
        if KEY_RESULT_TYPE in obj and KEY_RESULT in obj:
            result_obj = obj[KEY_RESULT]
            result_type_str = obj[KEY_RESULT_TYPE].lower()

            if STR_STR == result_type_str:
                # process original obj if String type
                result_obj = _process_string(obj)
                if _TRACE:
                    log('decoded string resource')
            elif STR_DT == result_type_str:
                # process original obj if dateTime type
                result_obj = _process_datetime(obj)
                if _TRACE:
                    log('decoded dateTime resource')
      ##      elif STR_PATIENT == result_type_str:
      ##          result_obj = _process_patient(result_obj)
      ##          if _TRACE:
      ##             log('decoded patient resource')
            else:
                # check for DSTU2 or DSTU3 resource bundles
                if result_type_str.endswith('stu2') or \
                   result_type_str.endswith('stu3'):    
                    result_obj = _process_bundle(name,
                                                 result_obj,
                                                 result_type_str)
                else:
                    if _TRACE:
                        log('\n*** decode_top_level_object: no decode ***')
                    result_obj = None
    else:
        # not sure what else to expect here
        assert False

    return result_obj


###############################################################################
def _get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Flatten and process FHIR resource examples')

    parser.add_argument('-v', '--version',
                        action='store_true',
                        help='show the version string and exit')
    parser.add_argument('-f', '--filepath',
                        help='path to JSON file containing CQL Engine results')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='print debug info to stdout')

    args = parser.parse_args()

    if 'version' in args and args.version:
        print(_get_version())
        sys.exit(0)

    if 'debug' in args and args.debug:
        enable_debug()

    filepath = None
    if 'filepath' in args and args.filepath:
        filepath = args.filepath
        if not os.path.isfile(filepath):
            print('Unknown file specified: "{0}"'.format(filepath))
            sys.exit(-1)
    else:
        print('Required "--filepath" argument not found.')
        sys.exit(-1)
    
    with open(filepath, 'rt') as infile:
        json_string = infile.read()
        json_data = json.loads(json_string)

        result = _process_resource(json_data)

        print('RESULT: ')
        if result is not None:
            for k,v in result.items():
                if dict == type(v):
                    print('\t{0}'.format(k))
                    for k2,v2 in v.items():
                        print('\t\t{0} => {1}'.format(k2, v2))
                elif list == type(v):
                    print('\t{0}'.format(k))
                    for index, v2 in enumerate(v):
                        print('\t\t[{0}]:\t{1}'.format(index, v2))
                else:
                    print('\t{0} => {1}'.format(k,v))
