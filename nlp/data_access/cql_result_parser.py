#!/usr/bin/env python3
"""
Module used to decode JSON results from the FHIR CQL wrapper.
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
    from flatten import flatten
else:
    from data_access.flatten import flatten
    from algorithms.finder import time_finder

_VERSION_MAJOR = 0
_VERSION_MINOR = 5
_MODULE_NAME   = 'cql_result_parser.py'

# set to True to enable debug output
_TRACE = False

# dict keys used to extract portions of the JSON data
_KEY_ABATEMENT_DATE_TIME  = 'abatementDateTime'
_KEY_AUTHORED_ON          = 'authoredOn'
_KEY_CATEGORY             = 'category'
_KEY_CODE                 = 'code'
_KEY_CODING               = 'coding'
_KEY_CONTEXT              = 'context'
_KEY_DISPLAY              = 'display'
_KEY_DOB                  = 'birthDate'
_KEY_DOSAGE               = 'dosage'
_KEY_DOSE_QUANTITY        = 'doseQuantity'
_KEY_EFF_DATE_TIME        = 'effectiveDateTime'
_KEY_EFF_PERIOD           = 'effectivePeriod'
_KEY_FAMILY_NAME          = 'family'
_KEY_GENDER               = 'gender'
_KEY_GIVEN_NAME           = 'given'
_KEY_ID                   = 'id'
_KEY_LOCATION             = 'location'
_KEY_MED_CODEABLE_CONCEPT = 'medicationCodeableConcept'
_KEY_NAME                 = 'name'
_KEY_ONSET_DATE_TIME      = 'onsetDateTime'
_KEY_PERFORMED_DATE_TIME  = 'performedDateTime'
_KEY_REFERENCE            = 'reference'
_KEY_RESOURCE_TYPE        = 'resourceType'
_KEY_RESULT               = 'result'
_KEY_RESULT_TYPE          = 'resultType'
_KEY_STATUS               = 'status'
_KEY_SUBJECT              = 'subject'
_KEY_SYSTEM               = 'system'
_KEY_TAKEN                = 'taken'
_KEY_UNIT                 = 'unit'
_KEY_VALUE                = 'value'
_KEY_VALUE_QUANTITY       = 'valueQuantity'

_STR_BUNDLE2                   = 'FhirBundleCursorStu2'
_STR_BUNDLE3                   = 'FhirBundleCursorStu3'
_STR_CONDITION                 = 'Condition'
_STR_OBSERVATION               = 'Observation'
_STR_PATIENT                   = 'Patient'
_STR_PROCEDURE                 = 'Procedure'
_STR_MEDICATION_ADMINISTRATION = 'MedicationAdministration'
_STR_MEDICATION_STATEMENT      = 'MedicationStatement'
_STR_MEDICATION_ORDER          = 'MedicationOrder'
_STR_MEDICATION_REQUEST        = 'MedicationRequest'

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

DOSE_QUANTITY_FIELDS = ['value', 'unit', 'system', 'code']
DoseQuantityObj = namedtuple('DoseQuantityObj', DOSE_QUANTITY_FIELDS)

# fields extracted from a 'MedicationStatement' FHIR resource
MEDICATION_STATEMENT_FIELDS = [
    'id_value',
    'context_reference',
    'coding_systems_list',
    'subject_reference',
    'subject_display',
    'taken',         # Boolean
    'dosage_list',   # list of DoseQuantity objects
    'date_time',
    'end_date_time'
]
MedicationStatementResource = namedtuple('MedicationStatementResource',
                                         MEDICATION_STATEMENT_FIELDS)

MEDICATION_REQUEST_FIELDS = [
    'id_value',
    'coding_systems_list',
    'subject_reference',
    'subject_display',
    'date_time'
]

MedicationRequestResource = namedtuple('MedicationRequestResource',
                                       MEDICATION_REQUEST_FIELDS)

# temporary - need confirmation on fields returned by CQL Engine
MEDICATION_ADMINISTRATION_FIELDS = [
    'id_value',
    'coding_systems_list',
    'subject_reference',
    'subject_display',
    'dosage_list'
    'date_time'
]

MedicationAdministrationResource = namedtuple('MedicationAdministrationResource',
                                              MEDICATION_ADMINISTRATION_FIELDS)

# regex used to recognize UTC offsets in a FHIR datetime string
_regex_fhir_utc_offset = re.compile(r'[-\+]\d\d:\d\d\Z')

# regexes used to recognize date formats
_regex_ymd = re.compile(r'\d\d\d\d-\d\d-\d\d')
_regex_ym  = re.compile(r'\d\d\d\d-\d\d')
_regex_y   = re.compile(r'\d\d\d\d')

## KEEP

# regex used to recognize components of datetime strings
_str_datetime = r'\A(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<day>\d\d)' \
    r'(T(?P<time>\d\d:\d\d:\d\d[-+\.Z\d:]*))?\Z'
_regex_datetime = re.compile(_str_datetime)

_regex_coding = re.compile(r'\Acode_coding_(?P<num>\d)_')

_KEY_DATE_TIME     = 'date_time'
_KEY_END           = 'end'
_KEY_END_DATE_TIME = 'end_date_time'
_KEY_START         = 'start'


###############################################################################
def enable_debug():

    global _TRACE
    _TRACE = True


###############################################################################
def _dump_dict(dict_obj, msg=None):
    """
    Print to stdout the key-value pairs for the given dict.
    """

    assert dict == type(dict_obj)

    if msg is not None:
        print(msg)
    for k,v in dict_obj.items():
        print('\t{0} => {1}'.format(k, v))

    
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
                        us = time_obj.fractional_seconds % 999999

                    # get correct sign for UTC offset
                    mult = 1
                    if '-' == time_obj.gmt_delta_sign:
                        mult = -1
                    delta_hours = mult * time_obj.gmt_delta_hours
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
def _decode_boolean(obj):

    obj_type = type(obj)
    assert bool == obj_type or str == obj_type
    
    if bool == obj_type:
        if obj:
            return True
        else:
            return False
    else:
        tf = obj.lower()
        if 'true' == tf:
            return True
        else:
            return False

###############################################################################
def _decode_int(obj):

    assert int == type(obj)
    return int(obj)

        
###############################################################################
def _decode_quantity(obj):
    """
    Decode a FHIR STU2 'Quantity' object (1.19.0.6).
    """

    # all simple fields
    FIELD_NAMES = ['value', 'comparator', 'unit', 'system', 'code']

    result = {}
    for field_name in FIELD_NAMES:
        if field_name in obj:
            result[field_name] = obj[field_name]

    return result


###############################################################################
def _decode_range(obj):
    """
    Decode a FHIR STU2 'Range' object (1.19.0.7).
    """

    # all Quantity objects
    FIELD_NAMES = ['low', 'high']

    result = {}
    for field_name in FIELD_NAMES:
        if field_name in obj:
            result[field_name] = _decode_quantity(obj[field_name])

    return result


###############################################################################
def _decode_ratio(obj):
    """
    Decode a FHIR STU2 'Ratio' object (1.19.0.8).
    """

    # all Quantity objects
    FIELD_NAMES = ['numerator', 'denominator']

    result = {}
    for field_name in FIELD_NAMES:
        if field_name in obj:
            result[field_name] = _decode_quantity(obj[field_name])

    return result


###############################################################################
def _decode_sampled_data(obj):
    """
    Decode a FHIR STU2 'SampledData' object (1.19.0.10).
    """

    FIELD_ORIGIN = 'origin'

    result = {}
    if FIELD_ORIGIN in obj:
        result[FIELD_ORIGIN] = _decode_quantity(obj[FIELD_ORIGIN])

    SIMPLE_FIELDS = ['period', 'factor', 'lowerLimit',
                     'upperLimit', 'dimensions', 'data']

    for field_name in SIMPLE_FIELDS:
        if field_name in obj:
            result[field_name] = obj[field_name]

    return result


###############################################################################
def _decode_attachment(obj):
    """
    Decode a FHIR STU2 'Attachment' object (1.19.0.3).
    """

    SIMPLE_FIELDS = ['contentType', 'language', 'url', 'size', 'title']
    
    # the 'creation' field is a dateTime
    FIELD_CREATION = 'creation'

    # these fields are bse64 binary
    FIELD_DATA = 'data'
    FIELD_HASH = 'hash'
    
    result = {}
    
    for field_name in SIMPLE_FIELDS:
        if field_name in obj:
            result[field_name] = obj[field_name]
    
    if FIELD_CREATION in obj:
        result[FIELD_CREATION] = _decode_date_time(obj[FIELD_CREATION])

    if FIELD_HASH in obj:
        # convert hash to hex string
        result[FIELD_HASH] = '{0:x}'.format(obj[FIELD_HASH])

    if FIELD_DATA in obj:
        base64_encoded = obj[FIELD_DATA]
        decoded = base64.b64decode(base64_encoded)
        result[field_data] = decoded

    return result
                     

###############################################################################
def _decode_time(obj):
    """
    Decode a FHIR STU2 time value.

    Valid formats:
        HH:MM:SS
        HH:MM:SS.sss...
    """

    assert str == type(obj)
    time_str = obj.strip()

    # extract microseconds, if any
    us = 0
    pos = time_str.find('.')
    if -1 != pos:
        us = float(time_str[pos:])
        us = int(1000000.0 * us)
        time_str = time_str[:pos]

    h,m,s = time_str.split(':')
    return time(int(h), int(m), int(s), us)
        

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
def _decode_date_time(obj):
    """
    Decode a FHIR 'instant' or 'dateTime' timestring and return a python
    datetime obj.

    Valid formats:
        YYYY                           %Y 
        YYYY-MM                        %Y-%m
        YYYY-MM-DD                     %Y-%m-%d
        YYYY-MM-DDThh:mm:ssZ
        YYYY-MM-DDThh:mm:ss.sss
        YYYY-MM-DDThh:mm:ss.sssZ
        YYYY-MM-DDThh:mm:ss+zzzz       %Y-%m-%dT%H:%M:%S%z
        YYYY-MM-DDThh:mm:ss.sss+zzzz   %Y-%m-%dT%H:%M:%S.%f%z
    """

    assert str == type(obj)
    instant_str = obj.strip()
    
    # correct the UTC offset, if any (change +zz:zz to +zzzz)
    tmp = _fixup_fhir_datetime(instant_str)

    pos = tmp.find('.')
    if -1 != pos:
        if tmp.endswith('Z'):
            # fractional seconds and endswith 'Z'
            tmp = tmp[:-1]
            datetime_obj = datetime.strptime(tmp, '%Y-%m-%dT%H:%M:%S.%f')
        else:
            end_str = tmp[pos+1:]
            has_plus  = -1 != end_str.find('+')
            has_minus = -1 != end_str.find('-')
            if has_plus or has_minus:
                # fractional seconds and a UTC offset
                datetime_obj = datetime.strptime(tmp, '%Y-%m-%dT%H:%M:%S.%f%z')
            else:
                # fractional seconds only
                datetime_obj = datetime.strptime(tmp, '%Y-%m-%dT%H:%M:%S.%f')
    elif -1 != tmp.find('Z'):
        # only remaining format with a 'Z' char
        datetime_obj = datetime.strptime(tmp[:-1], '%Y-%m-%dT%H:%M:%S')
    elif -1 != tmp.find('T'):
        # only remaining format with a 'T' char
        datetime_obj = datetime.strptime(tmp, '%Y-%m-%dT%H:%M:%S%z')
    elif _regex_ymd.match(tmp):
        datetime_obj = datetime.strptime(tmp, '%Y-%m-%d')
    elif _regex_ym.match(tmp):
        datetime_obj = datetime.strptime(tmp, '%Y-%m')
    elif _regex_y.match(tmp):
        datetime_obj = datetime.strptime(tmp, '%Y')
    else:
        print('\n*** {0}: unknown time format: "{1}"'.
              format(_MODULE_NAME, instant_str))
        return None

    return datetime_obj


###############################################################################
def _decode_period(obj):
    """
    Decode a FHIR STU2 Period object (2.14.0.10).
    """

    FIELD_NAMES = ['start', 'end']

    result = {}
    for field_name in FIELD_NAMES:
        if field_name in obj:
            result[field_name] = _decode_date_time(obj[field_name])

    return result


###############################################################################
def _decode_address(obj):
    """
    Decode a FHIR STU2 Address object (1.19.0.13).
    """

    result = {}

    SIMPLE_FIELDS = ['use', 'type', 'text', 'city',
                     'district', 'state', 'postalCode', 'country']
    for f in SIMPLE_FIELDS:
        if f in obj:
            result[f] = obj[f]

    FIELD_LINE = 'line'
    if FIELD_LINE in obj:
        decoded_list = []
        elt_list = obj[FIELD_LINE]
        for elt in elt_list:
            decoded_obj = elt
            decoded_list.append(elt)
        result[FIELD_LINE] = decoded_list

    FIELD_PERIOD = 'period'
    if FIELD_PERIOD in obj:
        result[FIELD_PERIOD] = _decode_period(obj[FIELD_PERIOD])

    return result


###############################################################################
def _decode_human_name(obj):
    """
    Decode a FHIR STU2 HumanName object (1.19.0.12).
    """

    result = {}
    
    SCALAR_FIELDS = ['use', 'text']
    for f in SCALAR_FIELDS:
        if f in obj:
            result[f] = obj[f]

    ARRAY_FIELDS = ['family', 'given', 'prefix', 'suffix']
    for f in ARRAY_FIELDS:
        if f in obj:
            decoded_list = []
            elt_list = obj[f]
            for elt in elt_list:
                decoded_obj = elt
                decoded_list.append(elt)
            result[f] = decoded_list
            
    FIELD_PERIOD = 'period'
    if FIELD_PERIOD in obj:
        result[FIELD_PERIOD] = _decode_period(obj[FIELD_PERIOD])

    return result


###############################################################################
def _decode_contact_point(obj):
    """
    Decode a FHIR STU2 ContactPoint object (1.19.0.14).
    """

    result = {}

    SIMPLE_FIELDS = ['system', 'value', 'use', 'rank']
    for f in SIMPLE_FIELDS:
        if f in obj:
            result[f] = obj[f]

    FIELD_PERIOD = 'period'
    if FIELD_PERIOD in obj:
        result[FIELD_PERIOD] = _decode_period(obj[FIELD_PERIOD])

    return result


###############################################################################
def _decode_coding(obj):
    """
    Decode a FHIR STU2 Coding object (1.19.0.4).
    """

    # all simple fields
    FIELD_NAMES = ['system', 'version', 'code', 'display', 'userSelected']

    result = {}
    for field_name in FIELD_NAMES:
        if field_name in obj:
            result[field_name] = obj[field_name]

    return result

    
###############################################################################
def _decode_codeable_concept(obj):
    """
    Decode a FHIR STU2 CodeableConcept object (1.19.0.5).
    """

    result = {}

    FIELD_CODING = 'coding'
    if FIELD_CODING in obj:
        decoded_list = []
        elt_list = obj[FIELD_CODING]
        for elt in elt_list:
            decoded_obj = _decode_coding(elt)
            decoded_list.append(decoded_obj)
        result[FIELD_CODING] = decoded_list
        
    FIELD_TEXT = 'text'
    if FIELD_TEXT in obj:
        result[FIELD_TEXT] = obj[FIELD_TEXT]
            
    return result


###############################################################################
def _decode_reference_no_identifier(obj):
    """
    Decode a FHIR SHU2 Reference object (2.3.0) and ignore the contained
    Identifier, if any. This function is only called from a _decode_identifier
    call and prevents circular references.
    """

    # all simple fields
    FIELD_NAMES = ['reference', 'type', 'display']
    
    result = {}
    for field_name in FIELD_NAMES:
        if field_name in obj:
            result[field_name] = obj[field_name]

    return result


###############################################################################
def _decode_identifier(obj):
    """
    Decode a FHIR STU2 Identifier object (1.19.0.11).
    """

    structure = [
        ('use',      None),
        ('type',     _decode_codeable_concept),
        ('system',   None),
        ('value',    None),
        ('period',   _decode_period),
        ('assigner', _decode_reference_no_identifier)
    ]

    result = {}
    for field_name, decoder in structure:
        if field_name not in obj:
            continue
        if decoder is None:
            result[field_name] = obj[field_name]
        else:
            result[field_name] = decoder(obj[field_name])

    return result


###############################################################################
def _decode_reference(obj):
    """
    Decode a FHIR STU2 Reference object (2.3.0).
    """

    SIMPLE_FIELDS = ['reference', 'type', 'display']

    result = {}
    for field_name in SIMPLE_FIELDS:
        if field_name in obj:
            result[field_name] = obj[field_name]

    if 'identifier' in obj:
        result['identifier'] = _decode_identifier(obj['identifier'])

    return result


###############################################################################
def _decode_related(obj):
    """
    Decode a FHIR STU2 related internal object.
    Currently ignores extensions.
    """

    result = {}
    
    FIELD_TYPE = 'type'
    if FIELD_TYPE in obj:
        result[FIELD_TYPE] = obj[FIELD_TYPE]

    FIELD_TARGET = 'target'
    if FIELD_TARGET in obj:
        result[FIELD_TARGET] = _decode_reference(obj[FIELD_TARGET])

    return result


###############################################################################
def _decode_value(obj, result):
    """
    Decode a FHIR STU2 value field.
    """

    structure = [
        ('valueDateTime',        None,     _decode_date_time),
        ('valueDate',            None,     _decode_date_time),
        ('valueInstant',         None,     _decode_date_time),
        ('valueString',          None,     None),
        ('valueUri',             None,     None),
        ('valueCode',            None,     None),
        ('valueCoding',          None,     _decode_coding),
        ('valueCodeableConcept', None,     _decode_codeable_concept),
        ('valueIdentifier',      None,     _decode_identifier),
        ('valueQuantity',        None,     _decode_quantity),
        ('valueRange',           None,     _decode_range),
        ('valuePeriod',          None,     _decode_period),
        ('valueRatio',           None,     _decode_ratio),
        ('valueHumanName',       None,     _decode_human_name),
        ('valueSampledData',     None,     _decode_sampled_data),
        ('valueAttachment',      None,     _decode_attachment),
        ('valueTime',            None,     _decode_time),
    ]

    FIELD_VI = 'valueInteger'
    if FIELD_VI in obj:
        result[FIELD_VI] = int(obj[FIELD_VI])
        return

    FIELD_VD = 'valueDecimal'
    if FIELD_VD in obj:
        result[FIELD_VD] = float(obj[FIELD_VD])
        return

    FIELD_VB = 'valueBoolean'
    if FIELD_VB in obj:
        tf = obj[FIELD_VB].lower()
        if 'true' == tf:
            result[FIELD_VB] = True
        else:
            result[FIELD_VB] = False
        return
    
    _decode_from_structure(obj, structure, result)


###############################################################################
def _decode_meta(obj):
    """
    Decode a FHIR STU2 ResourceMetadata object (1.11.3.3).
    """

    result = {}

    SIMPLE_FIELDS = ['versionId', 'profile']
    for f in SIMPLE_FIELDS:
        if f in obj:
            result[f] = obj[f]

    FIELD_LU = 'lastUpdated'
    if FIELD_LU in obj:
        result[FIELD_LU] = _decode_date_time(obj[FIELD_LU])

    CODING_FIELDS = ['security', 'tag']
    for f in CODING_FIELDS:
        decoded_list = []
        if f in obj:
            # these are lists
            elt_list = obj[f]
            for elt in elt_list:
                decoded_obj = _decode_coding(obj[f])
                decoded_list.append(decoded_obj)
            result[f] = decoded_list

    return result


###############################################################################
def _decode_narrative(obj):
    """
    Decode a FHIR STU2 Narrative object (1.16.0).
    """

    result = {}
    
    FIELD_NAMES = ['status', 'div']
    for f in FIELD_NAMES:
        if f in obj:
            result[f] = obj[f]
        
    return result


###############################################################################
def _decode_extension(obj):
    """
    Decode A FHIR STU2 Extension object (1.17.0.1).
    """

    result = {}

    FIELD_URL = 'url'
    if FIELD_URL in obj:
        result[FIELD_URL] = obj[FIELD_URL]

    _decode_value(obj, result)

    # check for contained extensions and make recursive call
    FIELD_EXT = 'extension'
    if FIELD_EXT in obj:
        decoded_list = []
        elt_list = obj[FIELD_EXT]
        for elt in elt_list:
            decoded_ext = _decode_extension(elt)
            decoded_list.append(decoded_ext)
        result[FIELD_EXT] = decoded_list
    
    return result
            
    
###############################################################################
def _decode_from_structure(obj, structure, result):
    """
    Decode fields of obj using the field structure info.
    """

    for field_name, obj_type, decoder in structure:
        if field_name not in obj:
            continue

        if decoder is None:
            if obj_type is None:
                # scalar
                result[field_name] = obj[field_name]
            elif obj_type is list:
                decoded_list = []
                assert list == type(elt_list)
                elt_list = obj[field_name]
                for elt in elt_list:
                    decoded_list.append(elt)
                result[field_name] = decoded_list
        else:
            if obj_type is None:
                result[field_name] = decoder(obj[field_name])
            elif obj_type is list:
                decoded_list = []
                elt_list = obj[field_name]
                assert list == type(elt_list)
                for elt in elt_list:
                    decoded_obj = decoder(elt)
                    decoded_list.append(decoded_obj)
                result[field_name] = decoded_list
                
                
###############################################################################
def _decode_base_resource(obj, result):
    """
    Decode a FHIR STU2 BaseResource object (1.11.3).
    """

    SIMPLE_FIELDS = ['id', 'uri', 'code']
    for f in SIMPLE_FIELDS:
        if f in obj:
            result[f] = obj[f]

    FIELD_META = 'meta'
    if FIELD_META in obj:
        result[FIELD_META] = _decode_meta(obj[FIELD_META])
        

###############################################################################
def _decode_package_content(obj):
    """
    Decode the FHIR STU2 content object contained in a Medication resource
    package object.
    """

    result = {}

    structure = [
        ('item',   None,   None),
        ('amount', None,   None)
    ]

    _decode_from_structure(obj, structure, result)
    return result

    
###############################################################################
def _decode_medication_package(obj):
    """
    Decode the FHIR STU2 package object contained in a Medication resource.
    """

    result = {}

    structure = [
        ('container',  None,  _decode_codeable_concept),
        ('content',    list,  _decode_package_content)
    ]

    _decode_from_structure(obj, structure, result)
    return result

    
###############################################################################
def _decode_product_batch(obj):
    """
    Decode the FHIR STU2 batch object contained in a Medication
    product object.
    """

    result = {}

    structure = [
        ('lotNumber',      None,  None),
        ('expirationDate', None,  _decode_date_time)
    ]

    _decode_from_structure(obj, structure, result)
    return result
    

###############################################################################
def _decode_product_ingredient(obj):
    """
    Decode the FHIR STU2 ingredient object contained in a Medication
    product object.
    """

    result = {}

    structure = [
        ('item',   None,  _decode_reference),
        ('amount', None,  _decode_ratio)
    ]

    _decode_from_structure(obj, structure, result)
    return result

    
###############################################################################
def _decode_medication_product(obj):
    """
    Decode the FHIR STU2 product object contained in a Medication resource.
    """

    result = {}

    structure = [
        ('form',        None,   _decode_codeable_concept),
        ('ingredient',  list,   _decode_product_ingredient),
        ('batch',       list,   _decode_product_batch),
    ]

    _decode_from_structure(obj, structure, result)
    return result

    
###############################################################################
def _decode_medication(obj):
    """
    Decode a FHIR STU2 Medication resource object (4.12.2). This can be
    a contained resource inside other Medication-related resources.
    """

    result = {}

    _decode_base_resource(obj, result)

    # decode domain resource fields, if any
    # no 'text' field (narrative) for contained resources
    # no contained resources either

    EXT_FIELDS = ['extension', 'modifierExtension']
    for f in EXT_FIELDS:
        if f in obj:
            decoded_list = []
            elt_list = obj[f]
            for elt in elt_list:
                decoded_obj = _decode_extension(elt)
                decoded_list.append(decoded_obj)
            result[f] = decoded_list

    structure = [
        ('code',          None,   _decode_codeable_concept),
        ('isBrand',       None,   _decode_boolean),
        ('manufacturer',  None,   _decode_reference),
        ('product',       None,   _decode_medication_product),
        ('package',       None,   _decode_medication_package),
    ]

    _decode_from_structure(obj, structure, result)
    return result


###############################################################################
def _decode_domain_resource(obj, result):
    """
    Decode a FHIR STU2 DomainResource object (1.20.3).
    """

    FIELD_TEXT = 'text'
    if FIELD_TEXT in obj:
        result[FIELD_TEXT] = _decode_narrative(obj[FIELD_TEXT])

    FIELD_CONTAINED = 'contained'
    if FIELD_CONTAINED in obj:
        decoded_list = []
        elt_list = obj[FIELD_CONTAINED]
        for elt in elt_list:
            FIELD_RT = 'resourceType'
            if FIELD_RT in elt:
                rt = elt[FIELD_RT]
                if 'Medication' == rt:
                    decoded_obj = _decode_medication(elt)
                    decoded_list.append(decoded_obj)
        if len(decoded_list) > 0:
            result[FIELD_CONTAINED] = decoded_list

    EXT_FIELDS = ['extension', 'modifierExtension']
    for f in EXT_FIELDS:
        if f in obj:
            decoded_list = []
            elt_list = obj[f]
            for elt in elt_list:
                decoded_obj = _decode_extension(elt)
                decoded_list.append(decoded_obj)
            result[f] = decoded_list


###############################################################################
def _decode_annotation(obj):
    """
    Decode a FHIR STU2 Annotation object (1.19.0.17).
    """

    result = {}

    structure = [
        ('authorReference',   None,   _decode_reference),
        ('authorString',      None,   None),
        ('time',              None,   _decode_date_time),
        ('text',              None,   None)
    ]

    _decode_from_structure(obj, structure, result)
    return result


###############################################################################
def _decode_timing_repeat(obj):
    """
    Decode a FHIR STU2 repeat object embedded in a Timing object.
    """

    result = {}

    structure = [
        ('boundsQuantity',   None,   None),
        ('boundsRange',      None,   _decode_range),
        ('boundsPeriod',     None,   _decode_period),
        ('count',            None,   None),
        ('duration',         None,   None),
        ('durationMax',      None,   None),
        ('durationUnits',    None,   None),
        ('frequency',        None,   None),
        ('frequencyMax',     None,   None),
        ('period',           None,   None),
        ('periodMax',        None,   None),
        ('periodUnits',      None,   None),
        ('when',             None,   None)
    ]

    _decode_from_structure(obj, structure, result)
    return result


###############################################################################
def _decode_timing(obj):
    """
    Decode a FHIR STU2 Timing object (1.19.0.15).
    """

    result = {}

    structure = [
        ('event',     list,    _decode_date_time),
        ('repeat',    None,    _decode_timing_repeat),
        ('code',      None,    _decode_codeable_concept)
    ]

    _decode_from_structure(obj, structure, result)
    return result


###############################################################################
def _decode_med_dosage(obj):
    """
    Decode a FHIR STU2 dosage object embedded in a medication-related
    resource.
    """

    result = {}

    structure = [
        ('text',                    None,    None),
        ('timing',                  None,    _decode_timing),
        ('asNeededBoolean',         None,    _decode_boolean),
        ('asNeededCodeableConcept', None,    _decode_codeable_concept),
        ('siteCodeableConcept',     None,    _decode_codeable_concept),
        ('siteReference',           None,    _decode_reference),
        ('route',                   None,    _decode_codeable_concept),
        ('method',                  None,    _decode_codeable_concept),
        ('quantityQuantity',        None,    _decode_quantity),
        ('quantityRange',           None,    _decode_range),
        ('rateRatio',               None,    _decode_ratio),
        ('rateRange',               None,    _decode_range),
        ('maxDosePerPeriod',        None,    _decode_ratio)
    ]

    _decode_from_structure(obj, structure, result)
    return result


###############################################################################
def _decode_med_dosage_instruction(obj):
    """
    Decode a FHIR STU2 dosage instruction object embedded in a
    MedicationOrder resource.
    """

    result = {}

    structure = [
        ('text',                    None,   None),
        ('additionalInstructions',  None,  _decode_codeable_concept),
        ('timing',                  None,  _decode_timing),
        ('asNeededBoolean',         None,  _decode_boolean),
        ('asNeededCodeableConcept', None,  _decode_codeable_concept),
        ('siteCodeableConcept',     None,  _decode_codeable_concept),
        ('siteReference',           None,  _decode_reference),
        ('route',                   None,  _decode_codeable_concept),
        ('method',                  None,  _decode_codeable_concept),
        ('doseRange',               None,  _decode_range),
        ('doseQuantity',            None,  _decode_quantity),
        ('rateRatio',               None,  _decode_ratio),
        ('rateRange',               None,  _decode_range),
        ('maxDosePeriod',           None,  _decode_ratio)
    ]

    _decode_from_structure(obj, structure, result)
    return result


###############################################################################
def _decode_med_dispense_request(obj):
    """
    Decode a FHIR STU2 dispense request object embedded in a
    MedicationOrder resource.
    """

    result = {}

    structure = [
        ('medicationCodeableConcept',   None,   _decode_codeable_concept),
        ('medicationReference',         None,   _decode_reference),
        ('validityPeriod',              None,   _decode_period),
        ('numberOfRepeatsAllowed',      None,   _decode_int),
        ('quantity',                    None,   _decode_quantity),
        ('expectedSupplyDuration',      None,   None)
    ]

    _decode_from_structure(obj, structure, result)
    return result


###############################################################################
def _decode_med_substitution(obj):
    """
    Decode a FHIR STU2 'substitution' object embedded in a MedicationOrder
    resource.
    """

    result = {}

    structure = [
        ('type',   None,  _decode_codeable_concept),
        ('reason', None,  _decode_codeable_concept)
    ]

    _decode_from_structure(obj, structure, result)
    return result


###############################################################################
def _decode_condition_evidence(obj):
    """
    Decode a FHIR STU2 evidence object embedded in a Condition resource.
    """

    result = {}

    structure = [
        ('modifierExtension',   list,    _decode_extension),
        ('code',                None,    _decode_codeable_concept),
        ('detail',              list,    _decode_reference)
    ]

    _decode_from_structure(obj, structure, result)
    return result


###############################################################################
def _decode_condition_stage(obj):
    """
    Decode a FHIR STU2 stage object embedded in a Condition resource.
    """

    result = {}

    structure = [
        ('modifierExtension',   list,    _decode_extension),
        ('summary',             None,    _decode_codeable_concept),
        ('assessment',          list,    _decode_reference)
    ]

    _decode_from_structure(obj, structure, result)
    return result


###############################################################################
def _decode_procedure_focal_device(obj):
    """
    Decode a FHIR STU2 performer focal device object  embedded in a
    Procedure resource.
    """

    result = {}

    structure = [
        ('modifierExtension',   list,   _decode_extension),
        ('action',              None,   _decode_codeable_concept),
        ('manipulated',         None,   _decode_reference)
    ]

    _decode_from_structure(obj, structure, result)
    return result


###############################################################################
def _decode_procedure_performer(obj):
    """
    Decode a FHIR STU2 performer object embedded in a Procedure resource.
    """

    result = {}

    structure = [
        ('modifierExtension',   list,   _decode_extension),
        ('actor',               None,   _decode_reference),
        ('role',                None,   _decode_codeable_concept)
    ]

    _decode_from_structure(obj, structure, result)
    return result

                
###############################################################################
def _decode_obs_reference_range(obj):
    """
    Decode a FHIR STU2 referenceRange object embedded in an Observation
    resource.
    """

    result = {}

    structure = [
        # from BackboneElement
        ('modifierExtension',   list,   _decode_extension),
        ('low',                 None,   None),
        ('high',                None,   None),
        ('meaning',             None,   _decode_codeable_concept),
        ('age',                 None,   _decode_range),
        ('text',                None,   None)
    ]
    
    _decode_from_structure(obj, structure, result)
    return result


###############################################################################
def _decode_obs_component(obj):
    """
    Decode a FHIR STU2 'component' object embedded in an Observation resource.
    """

    result = {}

    FIELD_CODE = 'code'
    if FIELD_CODE in obj:
        result[FIELD_CODE] = _decode_codeable_concept(obj[FIELD_CODE])
        
    _decode_value(obj, result)

    FIELD_AR = 'dataAbsentReason'
    if FIELD_AR in obj:
        result[FIELD_AR] = _decode_codeable_concept(obj[FIELD_AR])

    FIELD_RR = 'referenceRange'
    if FIELD_RR in obj:
        decoded_list = []
        elt_list = obj[FIELD_RR]
        for elt in elt_list:
            decoded_obj = _decode_obs_reference_range(elt)
            decoded_list.append(decoded_obj)
        result[FIELD_RR] = decoded_list
    
    return result


###############################################################################
def _decode_patient_contact(obj):
    """
    Decode a FHIR STU2 Contact object embedded in a Patient resource.
    """

    result = {}

    structure = [
        # from BackboneElememnt
        ('modifierExtension',  list,    _decode_extension),

        # from embedded contact object
        ('relationship',       list,    _decode_codeable_concept),
        ('name',               None,    _decode_human_name),
        ('telecom',            list,    _decode_contact_point),
        ('address',            None,    _decode_address),
        ('gender',             None,    None),
        ('organization',       None,    _decode_reference),
        ('period',             None,    _decode_period)
    ]

    _decode_from_structure(obj, structure, result)
    return result


###############################################################################
def _decode_patient_communication(obj):
    """
    Decode a FHIR STU2 Communiation object embedded in a Patient resource.
    """

    result = {}

    structure = [
        # from BackboneElement
        ('modifierExtension',   list,   _decode_extension),

        # from embedded communication object
        ('language',            None,   _decode_codeable_concept),
        ('preferred',           None,   _decode_boolean)
    ]

    _decode_from_structure(obj, structure, result)
    return result


###############################################################################
def _decode_observation_stu2(obj):
    """
    Decode a FHIR STU2 Observation resource object (4.20.3).
    """

    observation = {}

    _decode_base_resource(obj, observation)
    _decode_domain_resource(obj, observation)

    # structure of this resource
    structure = [
        ('identifier',           list,     _decode_identifier),
        ('status',               None,     None),
        ('category',             None,     _decode_codeable_concept),
        ('code',                 None,     _decode_codeable_concept),
        ('subject',              None,     _decode_reference),
        ('encounter',            None,     _decode_reference),
        ('effectiveDateTime',    None,     _decode_date_time),
        ('effectivePeriod',      None,     _decode_period),
        ('issued',               None,     _decode_date_time),
        # value handled separately
        ('performer',            list,     _decode_reference),
        ('dataAbsentReason',     None,     _decode_codeable_concept),
        ('interpretation',       None,     _decode_codeable_concept),
        ('comments',             None,     None),
        ('bodySite',             None,     _decode_codeable_concept),
        ('method',               None,     _decode_codeable_concept),
        ('specimen',             None,     _decode_reference),
        ('device',               None,     _decode_reference),
        ('referenceRange',       list,     _decode_obs_reference_range),
        ('related',              list,     _decode_related),
        ('component',            list,     _decode_obs_component)
    ]

    _decode_from_structure(obj, structure, observation)
    _decode_value(obj, observation)
    return observation


###############################################################################
def _decode_patient_stu2(obj):
    """
    Decode a FHIR STU2 Patient resource object (5.1.2).
    """

    patient = {}

    _decode_base_resource(obj, patient)
    _decode_domain_resource(obj, patient)

    structure = [
        ('identifier',           list,     _decode_identifier),
        ('active',               None,     None),
        ('name',                 list,     _decode_human_name),
        ('telecom',              list,     _decode_contact_point),
        ('gender',               None,     None),
        ('birthDate',            None,     _decode_date_time),
        ('deceasedBoolean',      None,     _decode_boolean),
        ('deceasedDateTime',     None,     _decode_date_time),
        ('address',              None,     _decode_address),
        ('maritalStatus',        None,     _decode_codeable_concept),
        ('multipleBirthBoolean', None,     _decode_boolean),
        ('multipleBirthInteger', None,     None),
        ('contact',              list,     _decode_patient_contact),
        ('communication',        list,     _decode_patient_communication),
        ('careProvider',         list,     _decode_reference)
    ]

    _decode_from_structure(obj, structure, patient)
    return patient


###############################################################################
def _decode_procedure_stu2(obj):
    """
    Decode a FHIR STU2 Procedure resource object (4.8.3).
    """

    procedure = {}

    _decode_base_resource(obj, procedure)
    _decode_domain_resource(obj, procedure)

    structure = [
        ('identifier',            list,     _decode_identifier),
        ('subject',               None,     _decode_reference),
        ('status',                None,     None),
        ('category',              None,     _decode_codeable_concept),
        ('code',                  None,     _decode_codeable_concept),
        ('notPerformed',          None,     _decode_boolean),
        ('reasonNotPerformed',    list,     _decode_codeable_concept),
        ('bodySite',              list,     _decode_codeable_concept),
        ('reasonCodeableConcept', None,     _decode_codeable_concept),
        ('reasonReference',       None,     _decode_codeable_concept),
        ('performer',             list,     _decode_procedure_performer),
        ('performedDateTime',     None,     _decode_date_time),
        ('performedPeriod',       None,     _decode_period),
        ('encounter',             None,     _decode_reference),
        ('location',              None,     _decode_reference),
        ('outcome',               None,     _decode_codeable_concept),
        ('report',                list,     _decode_reference),
        ('complication',          list,     _decode_codeable_concept),
        ('followUp',              list,     _decode_codeable_concept),
        ('request',               None,     _decode_reference),
        ('notes',                 list,     _decode_annotation),
        ('focalDevice',           list,     _decode_procedure_focal_device),
        ('used',                  list,     _decode_reference)
    ]

    _decode_from_structure(obj, structure, procedure)
    return procedure


###############################################################################
def _decode_condition_stu2(obj):
    """
    Decode a FHIR STU2 Condition resource object (4.3.3).
    """

    condition = {}

    _decode_base_resource(obj, condition)
    _decode_domain_resource(obj, condition)

    structure = [
        ('identifier',            list,     _decode_identifier),
        ('patient',               None,     _decode_reference),
        ('encounter',             None,     _decode_reference),
        ('asserter',              None,     _decode_reference),
        ('dateRecorded',          None,     _decode_date_time),
        ('code',                  None,     _decode_codeable_concept),
        ('category',              None,     _decode_codeable_concept),
        ('clinicalStatus',        None,     None),
        ('verificationStatus',    None,     None),
        ('severity',              None,     _decode_codeable_concept),
        ('onsetDateTime',         None,     _decode_date_time),
        ('onsetQuantity',         None,     None),
        ('onsetPeriod',           None,     _decode_period),
        ('onsetRange',            None,     _decode_range),
        ('onsetString',           None,     None),
        ('abatementDateTime',     None,     _decode_date_time),
        ('abatementQuantity',     None,     None),
        ('abatementBoolean',      None,     _decode_boolean),
        ('abatementPeriod',       None,     _decode_period),
        ('abatementRange',        None,     _decode_range),
        ('abatementString',       None,     None),
        ('stage',                 None,     _decode_condition_stage),
        ('evidence',              list,     _decode_condition_evidence),
        ('bodySite',              list,     _decode_codeable_concept),
        ('notes',                 None,     None)
    ]

    _decode_from_structure(obj, structure, condition)
    return condition


###############################################################################
def _decode_medication_statement_stu2(obj):
    """
    Decode a FHIR STU2 MedicationStatement resource object (4.16.3).
    """

    med_stmt = {}

    _decode_base_resource(obj, med_stmt)
    _decode_domain_resource(obj, med_stmt)

    structure = [
        ('identifier',                  list,     _decode_identifier),
        ('patient',                     None,     _decode_reference),
        ('informationSource',           None,     _decode_reference),
        ('dateAsserted',                None,     _decode_date_time),
        ('status',                      None,     None),
        ('wasNotTaken',                 None,     _decode_boolean),
        ('reasonForUseCodeableConcept', None,     _decode_codeable_concept),
        ('reasonForUseReference',       None,     _decode_reference),
        ('effectiveDateTime',           None,     _decode_date_time),
        ('effectivePeriod',             None,     _decode_period),
        ('note',                        None,     None),
        ('supportingInformation',       list,     _decode_reference),
        ('medicationCodeableConcept',   None,     _decode_codeable_concept),
        ('medicationReference',         None,     _decode_reference),
        ('dosage',                      list,     _decode_med_dosage)
    ]

    _decode_from_structure(obj, structure, med_stmt)
    return med_stmt


###############################################################################
def _decode_medication_order_stu2(obj):
    """
    Decode a FHIR STU2 MedicationOrder resource object (4.13.3).
    """

    med_order = {}

    _decode_base_resource(obj, med_order)
    _decode_domain_resource(obj, med_order)

    structure = [
        ('identifier',                  list,     _decode_identifier),
        ('dateWritten',                 None,     _decode_date_time),
        ('status',                      None,     None),
        ('dateEnded',                   None,     _decode_date_time),
        ('reasonEnded',                 None,     _decode_codeable_concept),
        ('patient',                     None,     _decode_reference),
        ('prescriber',                  None,     _decode_reference),
        ('encounter',                   None,     _decode_reference),
        ('reasonCodeableConcept',       None,     _decode_codeable_concept),
        ('reasonReference',             None,     _decode_reference),
        ('note',                        None,     None),
        ('medicationCodeableConcept',   None,     _decode_codeable_concept),
        ('medicationReference',         None,     _decode_reference),
        ('dosageInstruction',           list,     _decode_med_dosage_instruction),
        ('dispenseRequest',             None,     _decode_med_dispense_request),
        ('substitution',                None,     _decode_med_substitution),
        ('priorPrescription',           None,     _decode_reference)
    ]

    _decode_from_structure(obj, structure, med_order)
    return med_order


###############################################################################
def _decode_medication_administration_stu2(obj):
    """
    Decode a FHIR STU2 MedicationAdministration resource object (4.14.3).
    """

    med_admin = {}

    _decode_base_resource(obj, med_admin)
    _decode_domain_resource(obj, med_admin)

    structure = [
        ('identifier',                 list,     _decode_identifier),
        TBD
    ]

    _decode_from_structure(obj, structure, med_admin)
    return med_admin



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
    code_dict = None
    if _KEY_CODE in obj:
        code_dict = obj[_KEY_CODE]
    elif _KEY_MED_CODEABLE_CONCEPT in obj:
        code_dict = obj[_KEY_MED_CODEABLE_CONCEPT]
    if code_dict is not None:
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
def _decode_effective_period(obj):

    if _KEY_START in obj:
        start_date_time = obj[_KEY_START]
        start_date_time = _fixup_fhir_datetime(start_date_time)
        start_date_time = datetime.strptime(start_date_time,
                                            '%Y-%m-%dT%H:%M:%S%z')
    if _KEY_END in obj:
        end_date_time = obj[_KEY_END]
        end_date_time = _fixup_fhir_datetime(end_date_time)
        end_date_time = datetime.strptime(end_date_time,
                                          '%Y-%m-%dT%H:%M:%S%z')
        
    return (start_date_time, end_date_time)


###############################################################################
def _decode_dosage(obj):

    dosage_list = []
    
    if _KEY_DOSAGE in obj:
        dl = obj[_KEY_DOSAGE]
        assert list == type(dl)
        for elt in dl:
            dq_obj = None
            if _KEY_DOSE_QUANTITY in elt:
                dq = elt[_KEY_DOSE_QUANTITY]
                assert dict == type(dq)
                value = None
                if _KEY_VALUE in dq:
                    value = dq[_KEY_VALUE]
                unit = None
                if _KEY_UNIT in dq:
                    unit = dq[_KEY_UNIT]
                system = None
                if _KEY_SYSTEM in dq:
                    system = dq[_KEY_SYSTEM]
                code = None
                if _KEY_CODE in dq:
                    code = dq[_KEY_CODE]
                dq_obj = DoseQuantityObj(value, unit, system, code)
            if dq_obj is not None:
                dosage_list.append(dq_obj)

    return dosage_list

                    
###############################################################################
def _decode_medication_statement(obj):
    """
    Decode a CQL Engine 'MedicationStatement' result.
    """

    if _TRACE: print('Decoding MedicationStatement resource...')

    obj_type = type(obj)
    assert dict == obj_type

    id_value = _decode_id_value(obj)
    subject_reference, subject_display = _decode_subject_info(obj)
    context_reference = _decode_context_info(obj)    
    code_systems_list = _decode_code_dict(obj)

    date_time = None
    end_date_time = None
    if _KEY_EFF_PERIOD in obj:
        eff_period_obj = obj[_KEY_EFF_PERIOD]
        date_time, end_date_time = _decode_effective_period(eff_period_obj)

    taken = False
    if _KEY_TAKEN in obj:
        taken_char = obj[_KEY_TAKEN]
        if 'y' == taken_char:
            taken = True

    dosage_list = _decode_dosage(obj)
            
    med_stmt = MedicationStatementResource(
        id_value = id_value,
        context_reference = context_reference,
        coding_systems_list = code_systems_list,
        subject_reference = subject_reference,
        subject_display = subject_display,
        taken = taken,
        dosage_list = dosage_list,
        date_time = date_time,
        end_date_time = end_date_time
    )

    return med_stmt


###############################################################################
def _decode_medication_order(obj):
    """
    Decode A CQL Engine 'MedicationRequest' or 'MedicationOrder' result.
    """

    if _TRACE: print('Decoding MedicationRequest/Order resource...')

    obj_type = type(obj)
    assert dict == obj_type

    id_value = _decode_id_value(obj)
    subject_reference, subject_display = _decode_subject_info(obj)
    code_systems_list = _decode_code_dict(obj)

    date_time = None
    if _KEY_AUTHORED_ON in obj:
        date_time = obj[_KEY_AUTHORED_ON]
        date_time = _fixup_fhir_datetime(date_time)
        date_time = datetime.strptime(date_time, '%Y-%m-%dT%H:%M:%S%z')

    med_req = MedicationRequestResource (
        id_value = id_value,
        coding_systems_list = code_systems_list,
        subject_reference = subject_reference,
        subject_display = subject_display,
        date_time = date_time
    )

    return med_req
    

###############################################################################
def _decode_medication_administration(obj):
    """
    Decode a CQL Engine 'MedicationAdministration' result.
    """

    if _TRACE: print('Decoding MedicationAdministration resource...')

    obj_type = type(obj)
    assert dict == obj_type

    id_value = _decode_id_value(obj)
    subject_reference, subject_display = _decode_subject_info(obj)
    code_systems_list = _decode_code_dict(obj)

    dosage_list = _decode_dosage(obj)

    date_time = None
    # need date_time key name

    med_admin = MedicationAdministrationResource(
        id_value = id_value,
        coding_systems_list = code_systems_list,
        subject_reference = subject_reference,
        subject_display = subject_display,
        dosage_list = dosage_list,
        date_time = date_time
    )

    return med_admin


###############################################################################
def _set_list_length(obj, prefix_str):
    """
    Determine the length of a flattened list whose element keys share the
    given prefix string. Add a new key of the form 'len_' + prefix_str that
    contains this length.
    """

    str_search = r'\A' + prefix_str + r'_(?P<num>\d)_'
    
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

    _set_list_length(obj, 'identifier')
    
    extension_count = _set_list_length(obj, 'extension')
    for i in range(extension_count):
        # set lengths of inner extension lists
        key_name = 'extension_{0}_extension'.format(i)
        _set_list_length(obj, key_name)
    

###############################################################################
def _decode_flattened_observation(obj):
    """
    Decode a flattened FHIR 'Observation' resource.
    """

    assert dict == type(obj)
    
    # add 'date_time' field for time sorting
    KEY_EDT = 'effectiveDateTime'
    KEY_EP  = 'effectivePeriod'
    if KEY_EDT in obj:
        edt = obj[KEY_EDT]
        obj[_KEY_DATE_TIME] = edt
    if KEY_EP in obj:
        if _KEY_START in obj[KEY_EP]:
            start = obj[KEY_EP][_KEY_START]
            obj[_KEY_DATE_TIME] = start
        if _KEY_END in obj[KEY_EP]:
            end = obj[KEY_EP][_KEY_END]
            obj[KEY_END_DATE_TIME] = end

    _base_init(obj)            
    _set_list_length(obj, 'code_coding')
    _set_list_length(obj, 'performer')
    _set_list_length(obj, 'referenceRange')
    component_count = _set_list_length(obj, 'component')
    for i in range(component_count):
        key = 'component_{0}_referenceRange'
        if key in obj:
            _set_list_length(obj, key)

    if _TRACE:
        _dump_dict(obj, 'Flattened Observation: ')
            
    return obj


###############################################################################
def _decode_flattened_medication_order(obj):
    """
    Decode a flattened FHIR DSTU2 'MedicationOrder' resource.
    """

    assert dict == type(obj)

    

###############################################################################
def _decode_flattened_medication_statement(obj):
    """
    Decode a flattened FHIR 'MedicationStatement' resource.
    """

    assert dict == type(obj)

    # add 'date_time' field for time sorting
    KEY_DA = 'dateAsserted'
    if KEY_DA in obj:
        da = obj[KEY_DA]
        obj[_KEY_DATE_TIME] = da
    
    _base_init(obj)
    reason_count = _set_list_length(obj, 'reasonNotTaken')
    for i in range(reason_count):
        key = 'reason_{0}_coding'
        if key in obj:
            _set_list_length(obj, key)
    _set_list_length(obj, 'reasonForUseCodeableConcept_coding')
    _set_list_length(obj, 'supportingInformation')
    _set_list_length(obj, 'medicationCodeableConcept_coding')
    dosage_count = _set_list_length(obj, 'dosage')
    for i in range(dosage_count):
        for field in ['asNeededCodeableConcept_coding',
                      'siteCodeableConcept_coding',
                      'route_coding', 'method_coding']:
            key = 'dosage_{0}_{1}'.format(field)
            if key in obj:
                _set_list_length(obj, key)
    
    if _TRACE:
        _dump_dict(obj, 'Flattened Medication Statement: ')

    return obj


###############################################################################
def _decode_flattened_condition(obj):
    """
    Decode a flattened FHIR 'Condition' resource.
    """

    assert dict == type(obj)

    KEY_ODT = 'onsetDateTime'
    KEY_OP  = 'onsetPeriod'
    KEY_ADT = 'abatementDateTime'
    KEY_AP  = 'abatementPeriod'

    if KEY_ODT in obj:
        odt = obj[KEY_ODT]
        obj[_KEY_DATE_TIME] = odt
    if KEY_ADT in obj:
        adt = obj[KEY_ADT]
        obj[_KEY_END_DATE_TIME] = adt

    if KEY_OP in obj:
        start = obj[KEY_OP][_KEY_START]
        obj[_KEY_DATE_TIME] = start
    if KEY_AP in obj:
        end = obj[KEY_AP][_KEY_END]
        obj[_KEY_END_DATE_TIME] = end
    
    _base_init(obj)
    _set_list_length(obj, 'code_coding')
    _set_list_length(obj, 'category_coding')
    _set_list_length(obj, 'stage_assessment')
    evidence_len = _set_list_length(obj, 'evidence')
    for i in range(evidence_len):
        key = 'evidence_{0}_{1}'.format('evidence', 'detail')
        if key in obj:
            _set_list_length(obj, key)
    _set_list_length(obj, 'bodySite')

    if _TRACE:
        _dump_dict(obj, '[AFTER] Flattened Condition: ')

    return obj
    

###############################################################################
def _decode_flattened_procedure(obj):
    """
    Decode a flattened FHIR 'Procedure' resource.
    """

    assert dict == type(obj)

    # add date_time fields for sorting
    KEY_PDT = 'performedDateTime'
    KEY_PP  = 'performedPeriod'
    if KEY_PDT in obj:
        # only a single timestamp
        pdt = obj[KEY_PDT]
        obj[_KEY_DATE_TIME] = pdt
    if KEY_PP in obj:
        # period, one or both timestamps could be present
        if _KEY_START in obj[KEY_PP]:
            start = obj[KEY_PP][_KEY_START]
            obj[_KEY_DATE_TIME] = start
        if _KEY_END in obj[KEY_PP]:
            end = obj[KEY_PP][_KEY_END]
            obj[_KEY_END_DATE_TIME] = end
    
    _base_init(obj)
    _set_list_length(obj, 'code_coding')
    _set_list_length(obj, 'reasonNotPerformed')
    _set_list_length(obj, 'performer')
    _set_list_length(obj, 'report')
    _set_list_length(obj, 'complication')
    _set_list_length(obj, 'followUp')
    _set_list_length(obj, 'notes')
    _set_list_length(obj, 'focalDevice')
    _set_list_length(obj, 'used')

    if _TRACE:
        _dump_dict(obj, 'Flattened Procedure: ')

    return obj
    

###############################################################################
def _decode_flattened_patient(obj):
    """
    Flatten and decode a FHIR 'Patient' resource.
    """

    # should be the string representation of a dict at this point
    obj_type = type(obj)
    assert str == obj_type

    try:
        obj = json.loads(obj)
    except json.decoder.JSONDecoderError as e:
        print('\t{0}: String conversion (patient) failed with error: "{1}"'.
              format(_MODULE_NAME, e))
        return result

    # the type instantiated from the string should be a dict
    obj_type = type(obj)
    assert dict == obj_type

    flattened_patient = flatten(obj)
    flattened_patient = _convert_datetimes(flattened_patient)

    _base_init(flattened_patient)

    name_count = _set_list_length(flattened_patient, 'name')
    for i in range(name_count):
        for field in ['family', 'given', 'prefix', 'suffix']:
            key = 'name_{0}_{1}'.format(i, field)
            if key in flattened_patient:
                _set_list_length(flattened_patient, key)

    _set_list_length(flattened_patient, 'telecom')
    _set_list_length(flattened_patient, 'address')
    _set_list_length(flattened_patient, 'careProvider')
    
    contact_count = _set_list_length(flattened_patient, 'contact')
    for i in range(contact_count):
        for field in ['relationship', 'telecom']:
            key = 'contact_{0}_{1}'.format(i, field)
            if key in flattened_patient:
                _set_list_length(flattened_patient, key)

    if _TRACE:
        _dump_dict(flattened_patient, '[AFTER] Flattened Patient resource: ')

    return flattened_patient






###############################################################################
def _decode_observation(obj):
    """
    Decode a CQL Engine 'Observation' result.
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
    Decode a CQL Engine 'Condition' result.
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
    Decode a CQL Engine 'Procedure' result.
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
    Decode a CQL Engine 'Patient' result.
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
    Decode a CQL Engine bundle object.
    """

    if _TRACE: print('Decoding BUNDLE resource...')

    STR_RES_TYPE = 'resourceType'
    
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

        # flatten the JSON, convert time strings to datetimes
        flattened_elt = flatten(elt)
        flattened_elt = _convert_datetimes(flattened_elt)

        # read the resource type and process accordingly
        if STR_RES_TYPE in flattened_elt:
            rt = elt[STR_RES_TYPE]
            if 'Observation' == rt:
                observation = _decode_flattened_observation(flattened_elt)
                bundled_objs.append(observation)
            elif 'Procedure' == rt:
                procedure = _decode_flattened_procedure(flattened_elt)
                bundled_objs.append(procedure)
            elif 'Condition' == rt:
                condition = _decode_flattened_condition(flattened_elt)
                bundled_objs.append(condition)
            elif 'MedicationStatement' == rt:
                med_statement = _decode_flattened_medication_statement(flattened_elt)
                bundled_objs.append(med_statement)
            elif 'MedicationOrder' == rt:
                med_order = _decode_flattened_medication_order(flattened_elt)
                bundled_objs.append(med_request)
            # elif 'MedicationAdministration' == rt:
            #     med_admin = _decode_medication_administration(elt)
            #     bundled_objs.append(med_admin)
    
    return bundled_objs


###############################################################################
def decode_top_level_obj(obj):
    """
    Decode the outermost object type returned by the CQL Engine.
    """

    KEY_NAME        = 'name'
    KEY_RESULT      = 'result'
    KEY_RESULT_TYPE = 'resultType'
    
    STR_PATIENT     = 'Patient'
    STR_BUNDLE2     = 'FhirBundleCursorStu2'
    STR_BUNDLE3     = 'FhirBundleCursorStu3'
    
    result_obj = None
    
    obj_type = type(obj)
    if dict == obj_type:
        if _TRACE: print('top_level_obj dict keys: {0}'.format(obj.keys()))

        name = None
        if KEY_NAME in obj:
            name = obj[KEY_NAME]
        if KEY_RESULT_TYPE in obj and KEY_RESULT in obj:
            result_obj = obj[KEY_RESULT]
            result_type_str = obj[KEY_RESULT_TYPE]
            
            if STR_PATIENT == result_type_str:
                result_obj = _decode_flattened_patient(result_obj)
                if _TRACE: print('decoded patient')
            elif STR_BUNDLE2 == result_type_str or STR_BUNDLE3 == result_type_str:
                result_obj = _decode_bundle(name, result_obj)
            else:
                if _TRACE: print('no decode')
                result_obj = None
    else:
        # don't know what else to expect here
        assert False

    return result_obj


###############################################################################
def _get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Decode results from the CQL Engine')

    parser.add_argument('-v', '--version',
                        action='store_true',
                        help='show the version string and exit')
    parser.add_argument('-f', '--filepath',
                        help='path to JSON file containing CQL Engine results')

    args = parser.parse_args()

    if 'version' in args and args.version:
        print(_get_version())
        sys.exit(0)

    filepath = None
    if 'filepath' in args and args.filepath:
        filepath = args.filepath
        if not os.path.isfile(filepath):
            print('Unknown file specified: "{0}"'.format(filepath))
            sys.exit(-1)
    
    with open(filepath, 'rt') as infile:
        json_string = infile.read()
        json_data = json.loads(json_string)

        # for obj in json_data:
        #     result = decode_top_level_obj(obj)
        #     if result is not None:
        #         for elt in result:
        #             print(elt)

        # flattened = flatten(json_data)
        # for k,v in flattened.items():
        #    print('{0} => {1}'.format(k,v))
        # sys.exit(0)

        obj = json_data
        result = None
        if 'resourceType' in obj:
            rt = obj['resourceType']
            if 'Observation' == rt:
                result = _decode_observation_stu2(obj)
            elif 'Patient' == rt:
                result = _decode_patient_stu2(obj)
            elif 'Procedure' == rt:
                result = _decode_procedure_stu2(obj)
            elif 'Condition' == rt:
                result = _decode_condition_stu2(obj)
            elif 'MedicationStatement' == rt:
                result = _decode_medication_statement_stu2(obj)
            elif 'MedicationOrder' == rt:
                result = _decode_medication_order_stu2(obj)
            elif 'MedicationAdministration' == rt:
                result = _decode_medication_administration_stu2(obj)

        if result is not None:
            for k,v in result.items():
                if dict == type(v):
                    print('{0}'.format(k))
                    for k2,v2 in v.items():
                        print('\t{0} => {1}'.format(k2, v2))
                elif list == type(v):
                    print('{0}'.format(k))
                    for index, v2 in enumerate(v):
                        print('\t[{0}]:\t{1}'.format(index, v2))
                else:
                    print('{0} => {1}'.format(k,v))

        # TODO - what about _text field? See cerner_med_order4.json
    # STR_RT        = 'resourceType'
    # STR_OBS       = 'Observation'
    # STR_PT        = 'Patient'
    # STR_PROC      = 'Procedure'
    # STR_COND      = 'Condition'
    # STR_MED_STMT  = 'MedicationStatement'
    # STR_MED_ORD   = 'MedicationOrder'
    # STR_MED_ADMIN = 'MedicationAdministration'
