"""
Tuple processing code with test data for Mongo.

Run this code as follows:

    1. Launch mongodb in a separate window:
  
        mongod --config /usr/local/etc/mongod.conf

    3. Load test data below into Mongo and run:
    (use the --cleanup flag to delete the test data on exit)

        python ./tuple_processor.py --debug [--cleanup]


To run in test mode:

    Delete all tuples from the NLPQL file
    Append "_Step1" to all tuple-containing NLPQL define statements
    Run the modififed NLPQL file with Clarity
    Undo the NLPQL file modifications
    Run the original NLPQL file through this test program:
        python ./tuple_processor.py --debug --clarity --jobid 4 --file ~/repos/gtri/rb230_private/nlpql/tuple2.nlpql

"""

import re
import os
import sys
import json
import argparse
from copy import deepcopy
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, BulkWriteError

from collections import namedtuple, defaultdict

try:
    from .tuple_lexer_and_parser import TupleLexer, TupleParser
except:
    from tuple_lexer_and_parser import TupleLexer, TupleParser

# mongo params for testing only
_DB_NAME         = 'tuple_test'
_COLLECTION_NAME = 'collection1'

# mongo params for ClarityNLP (requires the --clarity flag)
_DB_NAME_CLARITY         = 'nlp'
_COLLECTION_NAME_CLARITY = 'phenotype_results'

# tuple definition documents in Mongo have this value for nlpql_feature
_NLPQL_FEATURE_TUPLEDEF = 'tuple_definition'

_FIELD_PATIENT_ID    = 'subject'
_FIELD_TUPLE_DEF     = 'tuple_string'
_FIELD_TUPLE_FEATURE = 'define_text'

# default job id for testing
_JOB_ID = 999999

# regex to identify ClarityNLP a.b constructs
_str_identifier = r'[_a-z\d]+'
_str_dotted_identifier = r'(?P<feature>(' + _str_identifier + r'))' + r'\.' + \
    r'(?P<field>(' + _str_identifier + r'))'
_regex_dotted_identifier = re.compile(_str_dotted_identifier, re.IGNORECASE)

_TUPLE_HEADER = 'Tuple {'
_LEN_TUPLE_HEADER = len(_TUPLE_HEADER)

# appended to NLPQL feature names
_NLPQL_FEATURE_SUFFIX = '_Step1'

# regex to capture non-nested tuples
_str_tuple = r'\b(?P<tuple>Tuple\s+\{[^\}]+\})'
_regex_non_nested_tuple = re.compile(_str_tuple, re.IGNORECASE)

# regex to capture NLPQL "define" statements
_str_nlpql_define = r'\bdefine\s+(final\s+)?(?P<nlpql_feature>[^;]+);'
_regex_nlpql_define = re.compile(_str_nlpql_define, re.IGNORECASE)

# regex to capture NLPQL features in a "define" statement
_str_define = r'\bdefine\s+(final\s+)?(?P<nlpql_feature>[^:]+):'
_regex_define = re.compile(_str_define, re.IGNORECASE)

# set to True to enable debug printout
_TRACE = False


###############################################################################
def _enable_debug():

    global _TRACE
    _TRACE = True


###############################################################################
def _cleanup_db(db_name, mongo_obj, mongo_client_obj):

    # drop the existing collection and database
    if mongo_obj is not None:
        mongo_obj.drop()
    if mongo_client_obj is not None:
        mongo_client_obj.drop_database(db_name)

                
###############################################################################
def insert_docs(mongo_obj, doc_list):
    """
    """

    try:
        result = mongo_obj.insert_many(doc_list, ordered=False)
    except BulkWriteError as e:
        print(e.details['writeErrors'])
        result = None

    return result is not None
    
    
###############################################################################
def _load_test_data(db_name, mongo_obj, mongo_client_obj):

    _cleanup_db(db_name, mongo_obj, mongo_client_obj)

    # WBC results
    wbc_docs = [
        {'job_id':_JOB_ID, 'subject':'1', 'nlpql_feature':'WBC', 'date':'2020-01-01', 'value':4.5,
         'pipeline_type':'ValueExtractor'},
        {'job_id':_JOB_ID, 'subject':'1', 'nlpql_feature':'WBC', 'date':'2020-01-02', 'value':5.1,
         'pipeline_type':'ValueExtractor'},
        {'job_id':_JOB_ID, 'subject':'1', 'nlpql_feature':'WBC', 'date':'2020-01-03', 'value':5.1,
         'pipeline_type':'ValueExtractor'},
        {'job_id':_JOB_ID, 'subject':'1', 'nlpql_feature':'WBC', 'date':'2020-01-04', 'value':5.3,
         'pipeline_type':'ValueExtractor'},
        {'job_id':_JOB_ID, 'subject':'2', 'nlpql_feature':'WBC', 'date':'2020-01-05', 'value':6.5,
         'pipeline_type':'ValueExtractor'},
        {'job_id':_JOB_ID, 'subject':'2', 'nlpql_feature':'WBC', 'date':'2020-01-06', 'value':6.1,
         'pipeline_type':'ValueExtractor'},
        {'job_id':_JOB_ID, 'subject':'2', 'nlpql_feature':'WBC', 'date':'2020-01-07', 'value':6.1,
         'pipeline_type':'ValueExtractor'},
    ]

    if not insert_docs(mongo_obj, wbc_docs):
        return False

    # Temperature results
    temperature_docs = [
        {'job_id':_JOB_ID, 'subject':'1', 'nlpql_feature':'Temperature', 'date':'2020-01-01', 'value':101.1,
         'pipeline_type':'ValueExtractor'},
        {'job_id':_JOB_ID, 'subject':'1', 'nlpql_feature':'Temperature', 'date':'2020-01-02', 'value':101.4,
         'pipeline_type':'ValueExtractor'},
        {'job_id':_JOB_ID, 'subject':'1', 'nlpql_feature':'Temperature', 'date':'2020-01-03', 'value':102.0,
         'pipeline_type':'ValueExtractor'},
        {'job_id':_JOB_ID, 'subject':'1', 'nlpql_feature':'Temperature', 'date':'2020-01-04', 'value':102.0,
         'pipeline_type':'ValueExtractor'},
        {'job_id':_JOB_ID, 'subject':'1', 'nlpql_feature':'Temperature', 'date':'2020-01-05', 'value':101.5,
         'pipeline_type':'ValueExtractor'},
        {'job_id':_JOB_ID, 'subject':'2', 'nlpql_feature':'Temperature', 'date':'2020-01-06', 'value':101.2,
         'pipeline_type':'ValueExtractor'},
        {'job_id':_JOB_ID, 'subject':'2', 'nlpql_feature':'Temperature', 'date':'2020-01-07', 'value':101.1,
         'pipeline_type':'ValueExtractor'},
    ]

    if not insert_docs(mongo_obj, temperature_docs):
        return False

    # ProstateVolueMeasurement docs
    docs = [
        {'job_id':_JOB_ID, 'subject':'3', 'nlpql_feature':'ProstateVolumeMeasurement',
         'dimension_X':30, 'dimension_Y':40, 'dimension_Z':50, 'units':'MILLIMETERS', 'report_id':'100',
         'pipeline_type':'MeasurementFinder'},
        {'job_id':_JOB_ID, 'subject':'3', 'nlpql_feature':'ProstateVolumeMeasurement',
         'dimension_X':31, 'dimension_Y':41, 'dimension_Z':51, 'units':'MILLIMETERS', 'report_id':'101',
         'pipeline_type':'MeasurementFinder'},
        {'job_id':_JOB_ID, 'subject':'4', 'nlpql_feature':'ProstateVolumeMeasurement',
         'dimension_X':35, 'dimension_Y':45, 'dimension_Z':49, 'units':'MILLIMETERS', 'report_id':'102',
         'pipeline_type':'MeasurementFinder'},
        {'job_id':_JOB_ID, 'subject':'4', 'nlpql_feature':'ProstateVolumeMeasurement',
         'dimension_X':36, 'dimension_Y':46, 'dimension_Z':50, 'units':'MILLIMETERS', 'report_id':'103',
         'pipeline_type':'MeasurementFinder'},
    ]

    if not insert_docs(mongo_obj, docs):
        return False
    
    # Example1_Step1 result docs
    # these are the patients who satisfied (hasFever AND (hasDyspnea OR hasTachycardia))
    docs = [
        {'job_id':_JOB_ID, 'subject':'1', 'nlpql_feature':'Example1_Step1', 'doc1':'097b', 'doc2':'30e1'},
        {'job_id':_JOB_ID, 'subject':'1', 'nlpql_feature':'Example1_Step1', 'doc1':'0d45', 'doc2':'30e2'},
        {'job_id':_JOB_ID, 'subject':'1', 'nlpql_feature':'Example1_Step1', 'doc1':'0d46', 'doc2':'30e3'},
        {'job_id':_JOB_ID, 'subject':'1', 'nlpql_feature':'Example1_Step1', 'doc1':'097b', 'doc2':'30e4'},         
        {'job_id':_JOB_ID, 'subject':'1', 'nlpql_feature':'Example1_Step1', 'doc1':'0d45', 'doc2':'3efa'},
        {'job_id':_JOB_ID, 'subject':'1', 'nlpql_feature':'Example1_Step1', 'doc1':'0d46', 'doc2':'868c'},
        {'job_id':_JOB_ID, 'subject':'1', 'nlpql_feature':'Example1_Step1', 'doc1':'097b', 'doc2':'868d'},
        {'job_id':_JOB_ID, 'subject':'1', 'nlpql_feature':'Example1_Step1', 'doc1':'0d45', 'doc2':'8f19'},
        {'job_id':_JOB_ID, 'subject':'1', 'nlpql_feature':'Example1_Step1', 'doc1':'0d46', 'doc2':'92f6'},
        {'job_id':_JOB_ID, 'subject':'1', 'nlpql_feature':'Example1_Step1', 'doc1':'097b', 'doc2':'998c'},         
        {'job_id':_JOB_ID, 'subject':'1', 'nlpql_feature':'Example1_Step1', 'doc1':'0d45', 'doc2':'998d'},
        {'job_id':_JOB_ID, 'subject':'2', 'nlpql_feature':'Example1_Step1', 'doc1':'0a03', 'doc2':'7abc'},
        {'job_id':_JOB_ID, 'subject':'2', 'nlpql_feature':'Example2_Step1', 'doc1':'0a04', 'doc2':'7abd'},         
        {'job_id':_JOB_ID, 'subject':'2', 'nlpql_feature':'Example2_Step1', 'doc1':'0a05', 'doc2':'7abe'},
   ]

    if not insert_docs(mongo_obj, docs):
        return False

    # ProstateVolumeMeasurement_Step1 docs
    # these are the patients who have ProstateVolumeMeasurement.dimension_X > 0
    docs = [
        {'job_id':_JOB_ID, 'subject':'3', 'nlpql_feature':'ProstateVolumeMeasurement_Step1', 'other':'1'},
        {'job_id':_JOB_ID, 'subject':'3', 'nlpql_feature':'ProstateVolumeMeasurement_Step1', 'other':'2'},
        {'job_id':_JOB_ID, 'subject':'4', 'nlpql_feature':'ProstateVolumeMeasurement_Step1', 'other':'3'}
    ]
    
    if not insert_docs(mongo_obj, docs):
        return False
    
    return True
    

###############################################################################
def parse_tuple_definition(tuple_def_string):
    """
    Parse the tuple def, clean up any concatenated strings, and return
    the parser output. If there is a parse error, return None.
    """
    
    lexer = TupleLexer()
    parser = TupleParser()
    try:
        parse_result = parser.parse(lexer.tokenize(tuple_def_string))
    except EOFError:
        parse_result = None
        print('*** ERROR: tuple_processor: tuple parse failed ***')

    return parse_result


###############################################################################
def _build_patient_map(mongo_obj, job_id, tuple_feature, tuple_def_string):
    """
    The patient map is a dict that maps a patient_id to a list of mongo
    ObjectIds. The _id values in the list represent those docs for which
    the nlpql_feature field matches that of the tuple 'define' statement.
    """
    
    # query mongo for all docs with 'nlpql_feature' == tuple_feature
    query = {
        'job_id' : job_id,
        'nlpql_feature' : tuple_feature
    }
    all_docs = mongo_obj.find(query)
    doc_count = all_docs.count()

    if _TRACE:
        print('_build_patient_map found {0} documents'.format(doc_count))

    patient_map = defaultdict(list)
    for doc in all_docs:
        patient_id = doc[_FIELD_PATIENT_ID]
        patient_map[patient_id].append(doc['_id'])

    return patient_map

        
###############################################################################
def _get_feature_lists(mongo_obj, job_id):
    """
    """

    if _TRACE:
        print('Calling _get_feature_lists...')
    
    # find all tuple definition docs
    tuple_def_docs = mongo_obj.find(
        {
            'job_id':job_id,
            'nlpql_feature':_NLPQL_FEATURE_TUPLEDEF
        })

    feature_lists = []
    tuple_features = []
    tuple_defs = []
    for doc in tuple_def_docs:

        # extract 'define_text' and verbatim 'tuple_string'
        assert _FIELD_TUPLE_FEATURE in doc
        assert _FIELD_TUPLE_DEF in doc
        tuple_feature = doc[_FIELD_TUPLE_FEATURE]
        if _TRACE:
            print('\tFound tuple_feature: "{0}"'.format(tuple_feature))

        tuple_def = doc[_FIELD_TUPLE_DEF]
        # collapse repeated whitespace
        tuple_def = re.sub(r'\s+', ' ', tuple_def)

        #if _TRACE:
        #    print('\tTuple definition: ->{0}<-'.format(tuple_def))

        # # parse the tuple def and clean up any concatenated strings
        parse_result = parse_tuple_definition(tuple_def)
        # lexer = TupleLexer()
        # parser = TupleParser()
        # try:
        #     parse_result = parser.parse(lexer.tokenize(tuple_def))
        #     #print('raw parse result: ->{0}<-'.format(parse_result))            
        # except EOFError:
        #     parse_result = None
        #     print('*** ERROR: tuple_processor: tuple parse failed ***')

        if parse_result is None:
            continue

        # parser output becomes the new tuple definition
        tuple_def = parse_result
        
        # build feature list
        feature_set = set()
        iterator = _regex_dotted_identifier.finditer(tuple_def)
        for match in iterator:
            if match:
                feature = match.group('feature')
                field   = match.group('field')
                if _TRACE:
                    print('\t\tTuple "{0}" has feature "{1}" with field "{2}"'.
                          format(doc[_FIELD_TUPLE_FEATURE], feature, field))
                feature_set.add( (feature, field) )
        feature_list = list(feature_set)

        # accumulate on a set of lists
        feature_lists.append(feature_list)
        tuple_features.append(tuple_feature)
        tuple_defs.append(tuple_def)
        
    if _TRACE:
        print('\tReturning from _get_feature_lists...')
        
    return feature_lists, tuple_features, tuple_defs


###############################################################################
def _to_minimal_representation(unique_value_map):
    """
    Build a 'minimal representation' from the items in the map, which has the
    format:

            feature -> {set of values}
    """

    # sort the value sets in decreasing order of length
    meta = [ (len(value_set), feature) for feature,value_set in unique_value_map.items()]
    meta = sorted(meta, key=lambda x: x[0], reverse=True)
    # max length is the length of the list at meta[0]
    max_len = meta[0][0]
    
    new_lists = [ [] for i in range(max_len)]

    features_in_order = []    
    for num, feature in meta:
        features_in_order.append(feature)
        values = list(unique_value_map[feature])
        index = 0
        for i in range(max_len):
            new_lists[i].append(values[index])
            index += 1
            if index >= num:
                index = 0

    for i in range(len(new_lists)):
        new_lists[i] = tuple(new_lists[i])

    return new_lists, features_in_order


###############################################################################
def _to_output_tuples(tuple_def, feature_list, value_tuples):
    """
    Build the unique set of output tuple strings for this patient.
    Feature_list contains the features in the same order as the components
    of the value tuples.
    """

    if _TRACE:
        print('\nCalling _to_output_tuples...')
        print('\t   Tuple def: {0}'.format(tuple_def))
        print('\tfeature_list: {0}'.format(feature_list))
        print('\tvalue_tuples: {0}'.format(value_tuples))
    
    strings = []
    for tup in value_tuples:
        s = tuple_def
        # find offsets of each feature.field to be replaced
        i = 0
        for feature,field in feature_list:
            search_str = '{0}.{1}'.format(feature,field)
            offset = s.find(search_str)
            assert -1 != offset
            value = tup[i]
            s = s[:offset] + str(value) + s[offset + len(search_str):]
            i += 1
        strings.append(s)

    return strings


###############################################################################
def process_tuples(mongo_obj, job_id):
    """
    
    """
    
    feature_lists, tuple_features, tuple_defs = _get_feature_lists(mongo_obj,
                                                                   job_id)

    if _TRACE:
        print('\nResults of _get_feature_list: ')
        for i in range(len(feature_lists)):
            print('\tfeature_list   : {0}'.format(feature_lists[i]))
            print('\ttuple_features : {0}'.format(tuple_features[i]))
            print('\ttuple_defs     : {0}'.format(tuple_defs[i]))
            print()

    if _TRACE:
        print('Calling process_tuples...')
        
    all_writes_ok = True
    for f_index in range(len(feature_lists)):

        feature_list  = feature_lists[f_index]
        tuple_feature = tuple_features[f_index]
        tuple_def     = tuple_defs[f_index]
    
        patient_map = _build_patient_map(mongo_obj, job_id, tuple_feature, tuple_def)
        
        for patient_id, id_list in patient_map.items():
            # print('{0}: {1}'.format(patient_id, id_list))
            if _TRACE:
                print('\n\tPatient {0} has {1} result documents for feature {2}.'.
                      format(patient_id, len(id_list), tuple_feature))

            # find unique combinations of feature.field
            unique_value_map = defaultdict(set)
            for feature,field in feature_list:
                #print('feature: "{0}"'.format(feature))
                #print('  field: "{0}"'.format(field))
                # find all (job_id, patient_id, feature) docs
                query = {
                    'job_id':job_id,
                    'subject':patient_id,
                    'nlpql_feature':feature
                }
                feature_docs = mongo_obj.find(query)
                # get the field value from each doc and find uniques
                for fd in feature_docs:
                    assert field in fd
                    value = fd[field]
                    key = '{0}.{1}'.format(feature, field)
                    unique_value_map[key].add(value)

            if _TRACE:
                print('\tUnique values of feature.field: ')
                for feature, value_set in unique_value_map.items():
                    print('\t\t{0}: {1}'.format(feature, value_set))

            # create minimal representation of these unique values
            # (list of tuples)
            value_tuples, features_in_order = _to_minimal_representation(unique_value_map)
            if _TRACE:
                print('\tMinimal representation: {0}'.format(value_tuples))
                print('\tfeatures_in_order: {0}'.format(features_in_order))

            # get the list of feature.field in the correct order
            feature_list_in_order = []
            for fv in features_in_order:
                # these are actually feature.field strings
                f,v = fv.split('.')
                found_it = False
                for feature,field in feature_list:
                    if f == feature and v == field:
                        found_it = True
                        feature_list_in_order.append( (feature, field))
                        break
                assert found_it
                    
            # compute unique tuple strings for this patient by replacing the
            # field.value constructs with actual data
            tuple_strings = _to_output_tuples(tuple_def,
                                              feature_list_in_order,
                                              value_tuples)

            if _TRACE:
                print('\tOUTPUT TUPLE STRINGS: ')
                for s in tuple_strings:
                    print('\t\t{0}'.format(s))
                print()

            num_strings = len(tuple_strings)
            num_objs = len(id_list)

            if _TRACE:
                print('\tNum strings: {0}'.format(num_strings))
                print('\tNum objs   : {0}'.format(num_objs))
            
            # need at least as many output objects as tuple strings

            copy_objs = []
            if num_objs < num_strings:
                # fewer objects than tuple strings
                # need to generate num_strings - num_objs object copies
                num_to_generate = num_strings - num_objs

                # copy all existing objects
                cursor = mongo_obj.find({'job_id':job_id, '_id': {'$in':id_list}})

                num_generated = 0
                for c in cursor:
                    obj = deepcopy(c)
                    del obj['_id']
                    copy_objs.append(obj)
                    num_generated += 1
                    if num_generated == num_to_generate:
                        break

                while num_generated < num_to_generate:
                    k=0
                    obj = deepcopy(copy_objs[k])
                    copy_objs.append(obj)
                    num_generated += 1
                    k += 1
                    
                assert len(copy_objs) == num_to_generate
                if _TRACE:
                    print('\tCOPIED OBJECTS: ')
                    for e in copy_objs:
                        print('\t{0}'.format(e))
                    print()

            if _TRACE:
                print('\tlen id_list: {0}'.format(len(id_list)))
                print('\tnum_strings: {0}'.format(num_strings))
                print()

            # Update all existing docs by inserting a tuple string into each.
            # Tile the strings if more strings than objects.
            # Also delete the _NLPQL_FEATURE_SUFFIX from the nlpql_feature.
            nlpql_feature = tuple_feature[:-len(_NLPQL_FEATURE_SUFFIX)]

            # 'index' is for the tuple strings
            index = 0
            for obj_id in id_list:
                s = tuple_strings[index]
                index += 1
                if index >= len(tuple_strings):
                    # wrap around to the first tuple string
                    index = 0
                if _TRACE:
                    print('\tUpdating mongo doc with _id == {0}: tuple: {1}'.format(obj_id, s))
                mongo_obj.update_one(
                    {'_id':obj_id},
                    {"$set":{'tuple':s, 'nlpql_feature':nlpql_feature}}
                )

            # Insert a tuple string into the copy_objs and do a bulk insert
            # of these augmented objects into Mongo. Also correct the nlpql_feature
            # field.
            if len(copy_objs) > 0:
                for obj in copy_objs:
                    s = tuple_strings[index]
                    index += 1
                    if index >= len(tuple_strings):
                        index = 0
                    assert 'tuple' not in obj
                    obj['tuple'] = s
                    obj['nlpql_feature'] = nlpql_feature

                if _TRACE:
                    print('\n\tAUGMENTED COPY OBJS: ')
                    print('\t{0}'.format(copy_objs))
                    print()

                # insert these docs into Mongo
                if not insert_docs(mongo_obj, copy_objs):
                    all_writes_ok = False

    return all_writes_ok
                

###############################################################################
def get_tuple_definition(nlpql_define_statement):
    """
    Scan the NLPQL "define" statement and look for a tuple definition. If no
    tuple def is found, return the statement unmodified.

    If a tuple def is found, extract the tuple def from the statement and 
    modify the NLPQL feature by appending _NLPQL_FEATURE_SUFFIX to the feature
    name. Also generate a tuple definition document and return it. The tuple
    definition documents have the 'job_id' field set to None, so the job_id
    must be inserted later in the pipeline.

    Returns a modified "define" statement with these changes:

         nlpql_feature name has been modified
         tuple definition has been removed

    Example:

         define WBC:
             Tuple {
                 "Question" : "What is the white blood cell count?",
                 "Answer" : "The WBC is " + WBC.value
             }
         where (WBC.value > 11.0);

         This would be returned (and would be sent through the normal
         ClarityNLP pipeline):

         define WBC_Step1:
         where (WBC.value > 11.0);

         A tuple definition document would also be generated and returned.
    """

    if _TRACE:
        print('Calling get_tuple_definition...')
    
    # remove repeated whitespace
    statement = re.sub(r'\s+', ' ', nlpql_define_statement)
    
    tuple_string  = None
    define_string = None

    # search for a tuple (not all statements have them)
    match = _regex_non_nested_tuple.search(statement)
    if not match:
        # no tuple, return original statement
        return statement, None
    
    tuple_string = match.group('tuple')
    start = match.start('tuple')
    end   = match.end('tuple')

    # check the syntax of the tuple string - ClarityNLP needs it here
    tuple_def = parse_tuple_definition(tuple_string)
    if tuple_def is None:
        return None, None

    #if _TRACE:
    #    print('\ttuple_processor: found tuple {0}'.format(tuple_string))

    # get the NLPQL feature name in the 'define' string
    match = _regex_define.search(statement)
    if match:
        nlpql_feature = match.group('nlpql_feature')
        if _TRACE:
            print('\tFound a tuple for feature: "{0}"'.format(nlpql_feature))

    if nlpql_feature is None:
        if _TRACE:
            print('\ttuple_processor: failed to capture NLPQL feature ' \
                  'for tuple "{0}"'.format(tuple_string))
        return None, None

    # modify the feature name to be sent through the pipeline
    new_feature = nlpql_feature + _NLPQL_FEATURE_SUFFIX

    # strip the tuple from the statement
    new_statement = statement[:start] + statement[end:]

    # replace the feature name with the modified version
    new_statement = re.sub(nlpql_feature, new_feature, new_statement)

    # remove repeated whitespace
    new_statement = re.sub(r'\s+', ' ', new_statement)
    new_statement = new_statement.strip()

    # Construct the tuple definition doc WITHOUT the job_id.
    # The job_id will be added later.
    tuple_def_doc = {
        'job_id' : None,
        'nlpql_feature' : _NLPQL_FEATURE_TUPLEDEF,
        'define_text' : new_feature,
        'tuple_string' : tuple_string
    }

    if _TRACE:
        print('\nGenerated tuple definition document: ')
        for k,v in tuple_def_doc.items():
            print('\t{0} => {1}'.format(k,v))
        print()
    
    return new_statement, tuple_def_doc
    

###############################################################################
def modify_nlpql(nlpql_text):
    """
    Modify the NLPQL text to strip tuple definitions and write tuple definition
    documents into mongo. Return the modified NLPQL text.
    """

    define_statement_data = []

    # find the tuple-containing "define" statements in the nlpql text    
    iterator = _regex_nlpql_define.finditer(nlpql_text)
    for match in iterator:
        statement = match.group()
        # collapse repeated whitespace for simple search
        txt = re.sub(r'\s+', ' ', statement)
        if -1 != txt.find('Tuple {'):
            start = match.start()
            end   = match.end()
            define_statement_data.append( (start, end, statement))

    # generate the modified NLPQL text
    prev_end = 0
    new_text = []
    tuple_def_docs = []
    for start, end, statement in define_statement_data:
        # remove tuple defs from NLPQL text
        stripped, tuple_def_doc = get_tuple_definition(statement)
        tuple_def_docs.append(tuple_def_doc)
        new_text.append(nlpql_text[prev_end:start])
        new_text.append(stripped)
        prev_end = end
    new_text.append(nlpql_text[prev_end:])
    new_text = ' '.join(new_text)

    return new_text, tuple_def_docs
    

###############################################################################
def insert_tuple_def_docs(mongo_obj, tuple_def_docs, job_id):

    # insert the job_id into each tuple def doc
    for tdd in tuple_def_docs:
        tdd['job_id'] = job_id
    
    if not insert_docs(mongo_obj, tuple_def_docs):
        print('\ttuple processor: failed to insert tuple def docs')
        print('\ttuple def docs: ')
        for tdd in tuple_def_docs:
            for k,v in tdd.items():
                print('\t\t{0} => {1}'.format(k,v))
        return False
    return True


###############################################################################
if __name__ == '__main__':

    # some sample NLPQL "define" statements that include tuples
    TEST_STATEMENTS = [
        # 1
        """
        define ProstateVolumeMeasurement:
            Tuple {
                "QuestionConcept" : "22112145",
                "Question" : "How large was was the prostatic mass?",
                "Answer" : ProstateVolumeMeasurement.dimension_X + " x " + 
                           ProstateVolumeMeasurement.dimension_Y + " x " + 
                           ProstateVolumeMeasurement.dimension_Z + " "   + 
                           ProstateVolumeMeasurement.units
            }
        where ProstateVolumeMeasurement.dimension_X > 0;
        """,

        # 2
        """
        define Example1:
            Tuple {
                "Description": "WBC and temperature data",
                "WBC": WBC.value,
                "Temp": Temperature.value
            }
        where (hasFever AND (hasDyspnea OR hasTachycardia);
        """,

        # """
        # define SickPersonInfo:
        #     Tuple {
        #         Name: 'Patrick',
        #         DOB: GetBirthDate.value,
        #         Address: Tuple { Line1: '41 Spinning Ave', City: 'Dayton', State: 'OH' },
        #         Race: PatientRace.value_normalized
        #     }
        # where (HasChickPox OR Temperature.value >= 100.4)
        # """
    ]
    
    parser = argparse.ArgumentParser(
        description='Test program for tuple generation.'
    )

    parser.add_argument('-v', '--version',
                        action='store_true',
                        help='show the version string and exit')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='print debug information to stdout during the run') 
    parser.add_argument('-j', '--jobid',
                       default=_JOB_ID,
                       help='integer job id of a previous ClarityNLP run')
    parser.add_argument('-m', '--mongohost',
                        default='localhost',
                        help='IP address of MongoDB host ' \
                        '(default is localhost)')
    parser.add_argument('-p', '--mongoport',
                        default=27017,
                        help='port number for MongoDB host ' \
                        '(Default is 27017)')
    parser.add_argument('-c', '--cleanup',
                        action='store_true',
                        help='delete the test data on exit')
    parser.add_argument('--clarity',
                        action='store_true',
                        help='use the ClarityNLP database and collection')
    parser.add_argument('-f', '--file',
                        dest='filepath',
                        help='NLPQL file that generated Mongo results; requires --clarity flag')

    args = parser.parse_args()

    # default values for test database, no NLPQL file
    nlpql_file = None
    use_test_db = True
    db_name = _DB_NAME
    collection_name = _COLLECTION_NAME
    define_statements = TEST_STATEMENTS
    
    if 'version' in args and args.version:
        print(_get_version())
        sys.exit(0)

    if 'debug' in args and args.debug:
        _enable_debug()

    if 'clarity' in args and args.clarity:
        use_test_db = False
        db_name = _DB_NAME_CLARITY
        collection_name = _COLLECTION_NAME_CLARITY

        # the --clarity flag requires an NLPQL file
        if 'filepath' in args and args.filepath:
            nlpql_file = args.filepath
            if not os.path.isfile(nlpql_file):
                print('\n*** File not found: "{0}" ***'.format(nlpql_file))
                sys.exit(-1)
        else:
            print('\n*** Missing required --file argument ***')
            sys.exit(-1)
        
    job_id = int(args.jobid)

    print('Using database "{0}" and collection "{1}"'.format(db_name,
                                                             collection_name))
    
    #
    # connect to MongoDB (must already be running)
    #
    
    mongohost = args.mongohost
    mongoport = int(args.mongoport)

    try:
        mongo_client_obj = MongoClient(mongohost, mongoport)
        mongo_db_obj = mongo_client_obj[db_name]
        mongo_obj = mongo_db_obj[collection_name]
    except ConnectionFailure as e:
        print('*** Mongo exception: ConnectionFailure ***')
        print(e)

    # if using clarity, read NLPQL define statements from an NLPQL file
    if 'clarity' in args and args.clarity:
        use_test_db = False

        # the --clarity flag requires an NLPQL file
        assert nlpql_file is not None

        # remove all tuple def docs, since they will be inserted again when the
        # tuples are stripped out
        delete_result = mongo_obj.delete_many({'job_id':job_id,
                                               'nlpql_feature':_NLPQL_FEATURE_TUPLEDEF})
        print('Deleted {0} tuple def documents'.format(delete_result.deleted_count))

        # generate modified NLPQL text with the tuple definitions removed
        # and the tuple-containing define features altered
        nlpql_text = None
        with open(nlpql_file, 'rt') as infile:
            nlpql_text = infile.read()
            assert nlpql_text is not None

        stripped_nlpql, tuple_def_docs = modify_nlpql(nlpql_text)

        if _TRACE:
            print('stripped NLPQL: ')
            print('------------------------------------')
            print(stripped_nlpql)
            print('------------------------------------')                
            print()

        # insert the tuple definition docs into Mongo
        if not insert_tuple_def_docs(mongo_obj, tuple_def_docs, job_id):
            sys.exit(-1)
        # if not insert_docs(mongo_obj, tuple_def_docs):
        #     print('\ttuple processor: failed to insert tuple def docs')
        #     print('\tjob_id: "{0}"'.format(job_id))
        #     print('\ttuple def docs: ')
        #     for tdd in tuple_def_docs:
        #         for k,v in tdd.items():
        #             print('\t\t{0} => {1}'.format(k,v))
        #     sys.exit(-1)

    # 
    # load test data into Mongo if not using Clarity
    #

    if use_test_db:
        if not _load_test_data(db_name, mongo_obj, mongo_client_obj):
            _cleanup_db(db_name, mongo_obj, mongo_client_obj)
            sys.exit(-1)
        if _TRACE:
            print('Loaded test docs')

        #
        # Scan the NLPQL statements above for tuples, extract tuple definitions,
        # write the tuple definition documents into Mongo, and return modified
        # NLPQL statements to be sent through the ClarityNLP pipeline.
        # 
    
        print()
        for statement in TEST_STATEMENTS:
            new_statement, tuple_def_docs = get_tuple_definition(statement)

            # insert tuple definition docs into Mongo
            if not insert_tuple_def_docs(mongo_obj, tuple_def_docs, job_id):
                sys.exit(-1)
            
            # send 'new_statement' through the normal ClarityNLP pipeline
            if new_statement is not None:
                if _TRACE:
                    print('\tmodified NLPQL statement: "{0}"'.format(new_statement))
                    print()

                # send through ClarityNLP pipeline...

    # the (fake) pipeline has finished, now do tuple processing
    succeeded = process_tuples(mongo_obj, job_id)
    if not succeeded:
        print('*** ERROR: some mongo writes failed. ***')

    if 'cleanup' in args and args.cleanup and use_test_db:
        _cleanup_db(db_name, mongo_obj, mongo_client_obj)
        if _TRACE:
            print('\tDeleted test documents')
