#!/usr/bin/env python3
"""
Import-only module used to decode JSON results from the FHIR CQL wrapper.
"""

import re
import os
import sys
import json
import base64
import optparse
from datetime import datetime, timezone
from collections import namedtuple

_VERSION_MAJOR = 0
_VERSION_MINOR = 3
_MODULE_NAME   = 'cibmtr_result_parser.py'

# set to True to enable debug output
_TRACE = True

# dict keys used to extract portions of the JSON data
_KEY_ABATEMENT_DATE_TIME = 'abatementDateTime'
_KEY_ASSIGNER            = 'assigner'
_KEY_ATTACHMENT          = 'attachment'
_KEY_AUTHENTICATOR       = 'authenticator'
_KEY_AUTHOR              = 'author'
_KEY_CATEGORY            = 'category'
_KEY_CODE                = 'code'
_KEY_CODING              = 'coding'
_KEY_CONTAINED           = 'contained'
_KEY_CONTENT             = 'content'
_KEY_CONTEXT             = 'context'
_KEY_CREATION            = 'creation'
_KEY_CUSTODIAN           = 'custodian'
_KEY_DATA                = 'data'
_KEY_DATE                = 'date'
_KEY_DESCRIPTION         = 'description'
_KEY_DISPLAY             = 'display'
_KEY_DOB                 = 'birthDate'
_KEY_DOC_STATUS          = 'docStatus'
_KEY_EFF_DATE_TIME       = 'effectiveDateTime'
_KEY_ENCOUNTER           = 'encounter'
_KEY_EVENT               = 'event'
_KEY_FACILITY_TYPE       = 'facilityType'
_KEY_FAMILY_NAME         = 'family'
_KEY_FORMAT              = 'format'
_KEY_GENDER              = 'gender'
_KEY_GIVEN_NAME          = 'given'
_KEY_ID                  = 'id'
_KEY_IDENTIFIER          = 'identifier'
_KEY_LOCATION            = 'location'
_KEY_MASTER_IDENTIFIER   = 'masterIdentifier'
_KEY_NAME                = 'name'
_KEY_ONSET_DATE_TIME     = 'onsetDateTime'
_KEY_PERFORMED_DATE_TIME = 'performedDateTime'
_KEY_PERIOD              = 'period'
_KEY_PRACTICE_SETTING    = 'practiceSetting'
_KEY_REFERENCE           = 'reference'
_KEY_RELATED             = 'related'
_KEY_RELATES_TO          = 'relatesTo'
_KEY_RESOURCE_TYPE       = 'resourceType'
_KEY_RESULT              = 'result'
_KEY_RESULT_TYPE         = 'resultType'
_KEY_SECURITY_LABEL      = 'securityLabel'
_KEY_SOURCE_PATIENT_INFO = 'sourcePatientInfo'
_KEY_STATUS              = 'status'
_KEY_SUBJECT             = 'subject'
_KEY_SYSTEM              = 'system'
_KEY_TARGET              = 'target'
_KEY_TEXT                = 'text'
_KEY_TYPE                = 'type'
_KEY_UNIT                = 'unit'
_KEY_USE                 = 'use'
_KEY_VALUE               = 'value'
_KEY_VALUE_QUANTITY      = 'valueQuantity'

# 2.3.0 Reference
_KEYS_REFERENCE = ['reference', 'type', 'identifier', 'display']
ReferenceObj = namedtuple('ReferenceObj', _KEYS_REFERENCE)

# 2.24.0.3 Attachment
_KEYS_ATTACHMENT = ['contentType', 'language', 'data', 'url', 'size', 'hash', 'title', 'creation']
AttachmentObj = namedtuple('AttachmentObj', _KEYS_ATTACHMENT)

# 2.24.0.4 Coding
_KEYS_CODING = ['system', 'version', 'code', 'display', 'userSelected']
CodingObj = namedtuple('CodingObj', _KEYS_CODING)

# 2.24.0.5 CodableConcept
_KEYS_CODABLE_CONCEPT = ['coding', 'text']
CodableConceptObj = namedtuple('CodableConceptObj', _KEYS_CODABLE_CONCEPT)

# 2.24.0.10 Period
_KEYS_PERIOD = ['start', 'end']
PeriodObj = namedtuple('PeriodObj', _KEYS_PERIOD)

# 2.24.0.12 Identifier
_KEYS_IDENTIFIER = ['use', 'type', 'system', 'value', 'period', 'assigner']
IdentifierObj = namedtuple('IdentifierObj', _KEYS_IDENTIFIER)

# relatesTo (from DocumentReference)
_KEYS_RELATES_TO = ['code', 'target']
RelatesToObj = namedtuple('RelatesToObj', _KEYS_RELATES_TO)

# content (from DocumentReference)
_KEYS_CONTENT = ['attachment', 'format']
ContentObj = namedtuple('ContentObj', _KEYS_CONTENT)

# context (from DocumentReference)
_KEYS_CONTEXT = ['encounter', 'event', 'period', 'facility_type',
                 'practice_setting', 'source_patient_info', 'related']
ContextObj = namedtuple('ContextObj', _KEYS_CONTEXT)

_STR_BUNDLE      = 'FhirBundleCursorStu3'
_STR_CONDITION   = 'Condition'
_STR_OBSERVATION = 'Observation'
_STR_PATIENT     = 'Patient'
_STR_PROCEDURE   = 'Procedure'
_STR_DOCREF      = 'DocumentReference'
_STR_DIAGREPT    = 'DiagnosticReport'
_STR_MEDADMIN    = 'MedicationAdministration'
_STR_MEDREQ      = 'MedicationRequest'
_STR_MEDSTMT     = 'MedicationStatement'

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

DOCUMENT_REFERENCE_FIELDS = [
    'id_str',
    'contained_list',
    'master_identifier',
    'identifier_list',
    'status',
    'doc_status',
    'type_str',
    'category_list',
    'subject',
    'date',
    'author_list',
    'authenticator',
    'custodian',
    'relates_to_list',
    'description',
    'security_label_list',
    'content_list',
    'context'
]

DocumentReferenceResource = namedtuple('DocumentReferenceResource',
                                       DOCUMENT_REFERENCE_FIELDS)


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
def _decode_coding(obj):
    """
    Decode a FHIR v4 'Coding' datatype (2.24.0.4) and return a Coding
    namedtuple.
    """

    assert dict == type(obj)

    new_dict = {}
    for k in _KEYS_CODING:
        new_dict[k] = obj.get(k) # returns None if key doesn't exist
    coding_obj = CodingObj(**new_dict)
    return coding_obj


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
                coding_obj = _decode_coding(coding_dict)
                coding_systems_list.append(coding_obj)
                        
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
def _decode_name_list(name_entries):

    name_list = []
    
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

    return name_list


###############################################################################
def _decode_codable_concept(obj):
    """
    Decode a FHIR 'CodableConcept' datatype (2.24.0.5) and return a
    CodableConceptObj namedtuple.
    """

    text = None
    if _KEY_TEXT in obj:
        text = obj[_KEY_TEXT]
    coding_list = []
    if _KEY_CODING in obj:
        coding_entries = obj[_KEY_CODING]
        obj_type = type(coding_entries)
        assert list == obj_type
        for elt in coding_entries:
            # 'Coding' datatype, 2.24.0.4
            coding_obj = _decode_coding(elt)
            coding_list.append(coding_obj)

    codable_concept_obj = CodableConceptObj(
        coding=coding_obj,
        text=text
    )
    return codable_concept_obj
        

###############################################################################
def _decode_period(obj):
    """
    Decode a FHIR 'Period' datatype (2.24.0.10) and return a Period namedtuple.
    """

    assert dict == type(obj)
    
    new_dict = {}
    for k in _KEYS_PERIOD:
        # these are datetimes
        tmp = _fixup_fhir_datetime(obj.get(k))
        new_dict[k] = datetime.strptime(tmp, '%Y-%m-%dT%H:%M:%S%z')
    period_obj = PeriodObj(**new_dict)
    return period_obj
    

###############################################################################
def _decode_identifier(obj):
    """
    Decode a FHIR 'Identifier' datatype (2.24.0.12). An identifier can include
    a reference ('assigner' field), which could potentially include another
    identifier field if an indirect reference. The spec seems to strongly
    indicate that the 'assigner' is a direct reference and is often just text.
    """

    use = None
    if _KEY_USE in obj:
        use = obj[_KEY_USE]
    the_type = None
    if _KEY_TYPE in obj:
        the_type = _decode_codable_concept(obj[_KEY_TYPE])
    system = None
    if _KEY_SYSTEM in obj:
        system = obj[_KEY_SYSTEM]
    value = None
    if _KEY_VALUE in obj:
        value = obj[_KEY_VALUE]
    period_obj = None
    if _KEY_PERIOD in obj:
        period_obj = _decode_period(obj[_KEY_PERIOD])
    assigner = None
    if _KEY_ASSIGNER in obj:
        # get the display string only
        assigner_obj = obj[_KEY_ASSIGNER]
        if _KEY_DISPLAY in assigner_obj:
            assigner = assigner_obj[_KEY_DISPLAY]

    identifier_obj = IdentifierObj(
        use=use,
        type=the_type,
        system=system,
        value=value,
        period=period_obj,
        assigner=assigner
    )
    return identifier_obj

        
###############################################################################
def _decode_reference(obj):
    """
    Decode a FHIR 'Reference' datatype (2.3.0) and return a ReferenceObj
    namedtuple.
    """

    assert dict == type(obj)

    reference = None
    if _KEY_REFERENCE in obj:
        reference = obj[_KEY_REFERENCE]
    the_type = None
    if _KEY_TYPE in obj:
        the_type = obj[_KEY_TYPE]
    identifier_obj = None
    if _KEY_IDENTIFIER in obj:
        identifier_obj = _decode_identifier(obj[_KEY_IDENTIFIER])
    display=None
    if _KEY_DISPLAY in obj:
        display = obj[_KEY_DISPLAY]

    reference_obj = ReferenceObj(
        reference=reference,
        type=the_type,
        identifier=identifier_obj,
        display=display
    )
    return reference_obj


###############################################################################
def _decode_instant(instant_str):
    """
    Decode a FHIR 'instant' timestring and return a python datetime obj.
    """

    tmp = _fixup_fhir_datetime(instant_str)
    the_instant = datetime.strptime(tmp, '%Y-%m-%dT%H:%M:%S%z')
    return the_instant
    

###############################################################################
def _decode_attachment(obj):
    """
    Decode a FHIR 'Attachment' datatype (2.24.0.3) and return an
    AttachmentObj namedtuple.
    """

    assert dict == type(obj)

    new_dict = {}
    for k in _KEYS_ATTACHMENT:
        new_dict[k] = obj.get(k)

    # fix the 'creation' timestamp
    creation_timestamp = new_dict[_KEY_CREATION]
    if creation_timestamp is not None:
        tmp = _fixup_fhir_datetime(creation_timestamp)
        new_dict[_KEY_CREATION] = datetime.strptime(tmp, '%Y-%m-%dT%H:%M:%S%z')

    # decode the base64 data, if any
    data = new_dict[_KEY_DATA]
    if data is not None:
        decoded_data = base64.b64decode(data)
        new_dict[_KEY_DATA] = decoded_data
            
    attachment_obj = AttachmentObj(**new_dict)
    return attachment_obj
    

###############################################################################
def _decode_content(obj):
    """
    Decode the 'content' field of a FHIR DocumentReference resource.
    """

    assert dict == type(obj)
    attachment_obj = None
    if _KEY_ATTACHMENT in obj:
        attachment_obj = _decode_attachment(obj[_KEY_ATTACHMENT])        
    format_obj = None
    if _KEY_FORMAT in obj:
        format_obj = _decode_coding(obj[_KEY_FORMAT])

    content_obj = ContentObj(
        attachment=attachment_obj,
        format=format_obj
    )
    return content_obj


###############################################################################
def _decode_context(obj):
    """
    Decode the 'context' field of a FHIR DocumentReference resource.
    """

    assert dict == type(obj)
    
    encounter_list = []
    if _KEY_ENCOUNTER in obj:
        elt_list = obj[_KEY_ENCOUNTER]
        assert list == type(elt_list)
        for elt in elt_list:
            encounter_obj = _decode_reference(elt)
            encounter_list.append(encounter_obj)
             
    event_list = []
    if _KEY_EVENT in obj:
        elt_list = obj[_KEY_EVENT]
        assert list == type(elt_list)
        for elt in elt_list:
            event_obj = _decode_codable_concept(elt)
            event_list.append(event_obj)

    period_obj = None
    if _KEY_PERIOD in obj:
        period = _decode_period(obj[_KEY_PERIOD])

    facility_type = None
    if _KEY_FACILITY_TYPE in obj:
        facility_type = _decode_codable_concept(obj[_KEY_FACILITY_TYPE])

    practice_setting = None
    if _KEY_PRACTICE_SETTING in obj:
        practice_setting = _decode_codable_concept(obj[_KEY_PRACTICE_SETTING])

    source_patient_info = None
    if _KEY_SOURCE_PATIENT_INFO in obj:
        source_patient_info = _decode_reference(obj[_KEY_SOURCE_PATIENT_INFO])

    related_list = []
    if _KEY_RELATED in obj:
        elt_list = obj[_KEY_RELATED]
        assert list == type(elt_list)
        for elt in elt_list:
            related_obj = _decode_reference(elt)
            related_list.append(related_obj)

    context_obj = ContextObj(
        encounter = encounter_list,
        event = event_list,
        period = period_obj,
        facility_type = facility_type,
        practice_setting = practice_setting,
        source_patient_info = source_patient_info,
        related = related_list
    )
    return context_obj
    

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
def _decode_document_reference(obj):
    """
    Decode a FHIR 'DocumentReference' object from the JSON data.
    """

    if _TRACE: print('Decoding DOCUMENTREFERENCE resource...')

    result = []

    obj_type = type(obj)
    assert dict == obj_type

    id_str = None
    if _KEY_ID in obj:
        id_str = obj[_KEY_ID]

    # contained
    contained_list = []
    if _KEY_CONTAINED in obj:
        the_list = obj[_KEY_CONTAINED]
        obj_type = type(the_list)
        assert list == obj_type
        for elt in the_list:

            elt_resource_type = None
            if _KEY_RESOURCE_TYPE in elt:
                elt_resource_type = elt[_KEY_RESOURCE_TYPE]
            elt_id = None
            if _KEY_ID in elt:
                elt_id = elt[_KEY_ID]
            elt_namelist = []
            if _KEY_NAME in elt:
                name_entries = elt[_KEY_NAME]
                elt_namelist = _decode_name_list(name_entries)

            contained_list.append( (elt_resource_type, elt_id, elt_namelist))

    # masterIdentifier
    master_identifier = None
    if _KEY_MASTER_IDENTIFIER in obj:
        master_identifier = _decode_identifier(obj[_KEY_MASTER_IDENTIFIER])
    identifier_list = []
    if _KEY_IDENTIFIER in obj:
        the_list = obj[_KEY_IDENTIFIER]
        obj_type = type(the_list)
        assert list == obj_type
        for elt in the_list:
            identifier = _decode_identifier(elt)
            identifier_list.append(identifier)

    # status
    status = None
    if _KEY_STATUS in obj:
        status = obj[_KEY_STATUS]
    doc_status = None
    if _KEY_DOC_STATUS in obj:
        doc_status = obj[_KEY_DOC_STATUS]

    # type
    the_type = None
    if _KEY_TYPE in obj:
        the_type = obj[_KEY_TYPE]
        # this is a CodableConcept
        the_type = _decode_codable_concept(the_type)

    # category (list of CodableConcept)
    category_list = []
    if _KEY_CATEGORY in obj:
        elt_list = obj[_KEY_CATEGORY]
        obj_type = type(elt_list)
        assert list == obj_type
        for elt in elt_list:
            codable_concept_obj = _decode_codable_concept(elt)
            category_list.append(codable_concept_obj)

    # subject
    subject_obj = None
    if _KEY_SUBJECT in obj:
        subject_obj = _decode_reference(obj[_KEY_SUBJECT])
            
    # date
    date = None
    if _KEY_DATE in obj:
        date = _decode_instant(obj[_KEY_DATE])

    # author list (list of Reference datatypes)
    author_list = []
    if _KEY_AUTHOR in obj:
        elt_list = obj[_KEY_AUTHOR]
        obj_type = type(elt_list)
        assert list == obj_type
        print('elt_list: {0}'.format(elt_list))
        print('length of elt list: {0}'.format(len(elt_list)))
        for elt in elt_list:
            print('type of elt: {0}'.format(type(elt)))
            author_obj = _decode_reference(elt)
            author_list.append(author_obj)

    # authenticator (Reference)
    authenticator = None
    if _KEY_AUTHENTICATOR in obj:
        authenticator = _decode_reference(obj[_KEY_AUTHENTICATOR])
            
    # custodian (Reference)
    custodian = None
    if _KEY_CUSTODIAN in obj:
        custodian = _decode_reference(obj[_KEY_CUSTODIAN])

    # relatesTo array
    relates_to_list = []
    if _KEY_RELATES_TO in obj:
        elt_list = obj[_KEY_RELATES_TO]
        obj_type = type(elt_list)
        assert list == obj_type
        for elt in elt_list:
            code = None
            if _KEY_CODE in elt:
                code = elt[_KEY_CODE]
            target_obj = None
            if _KEY_TARGET in elt:
                target_obj = _decode_reference(elt[_KEY_TARGET])
            relates_to_obj = RelatesToObj(code=code, target=target_obj)
            relates_to_list.append(relates_to_obj)

    # description
    description = None
    if _KEY_DESCRIPTION in obj:
        description = obj[_KEY_DESCRIPTION]

    # security label list (CodableConcept elements)
    security_label_list = []
    if _KEY_SECURITY_LABEL in obj:
        elt_list = obj[_KEY_SECURITY_LABEL]
        obj_type = type(elt_list)
        assert list == obj_type
        for elt in elt_list:
            sl_obj = _decode_codable_concept(elt)
            security_label_list.append(sl_obj)

    # content list (Content elements)
    content_list = []
    if _KEY_CONTENT in obj:
        elt_list = obj[_KEY_CONTENT]
        obj_type = type(elt_list)
        assert list == obj_type
        for elt in elt_list:
            content_obj = _decode_content(elt)
            content_list.append(content_obj)

    # context
    context_obj = None
    if _KEY_CONTEXT in obj:
        context_obj = _decode_context(obj[_KEY_CONTEXT])
        
    docref_obj = DocumentReferenceResource(
        id_str = id_str,
        contained_list = contained_list,
        master_identifier = master_identifier,
        identifier_list = identifier_list,
        status = status,
        doc_status = doc_status,
        type_str = the_type,
        category_list = category_list,
        subject = subject_obj,
        date = date,
        author_list = author_list,
        authenticator = authenticator,
        custodian = custodian,
        relates_to_list = relates_to_list,
        description = description,
        security_label_list = security_label_list,
        content_list = content_list,
        context = context_obj
    )

    print(docref_obj)
    return docref_obj
    

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
    except json.decoder.JSONDecodeError as e:
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
        name_list = _decode_name_list(name_entries)

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
            elif _STR_DOCREF == resource_type_str:
                docref_obj = _decode_document_reference(elt)
                bundled_objs.append(docref_obj)
    
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

        # DocumentReference example from FHIR website
        #if _KEY_RESOURCE_TYPE in obj and _STR_DOCREF == obj[_KEY_RESOURCE_TYPE]:
        #    result_obj = _decode_document_reference(obj)
        #    if _TRACE: print('decoded documentreference')

    else:
        # don't know what else to expect here
        assert False

    return result_obj
