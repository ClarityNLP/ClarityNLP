#!/usr/bin/env python3
"""
This is a program for testing the ClarityNLP NLPQL expression evaluator. It has
three modes of operation:

    1. Load a compressed test data file and run a self-checking suite of
       tests on the expression evaluator.

    2. Connect to a MongoDB instance containing data from a ClarityNLP run
       and interactively evaluate expressions on the data.

    3. Connect to a MongoDB instance containing data from a ClarityNLP run,
       load an NLPQL file, and evaluate the expressions it contains using
       the data stored in MongoDB.

To run option 1:

    Start a local instance of MongoDB
    Launch the self-checking test suite with this command:

        python3 ./expr_tester.py

To run option 2:

    Start a remote instance of MongoDB that contains ClarityNLP results.
    Note the job id for the run you are interested in.
    Run the test program with:

        python3 ./expr_tester.py --jobid <job_id> --mongohost <ip address>
                                --mongoport <port_no> [--debug] 
                                --expr 'my expression here'

To run option 3:

    Start a remote instance of MongoDB that contains ClarityNLP results.
    Note the job id for the run you are interested in.
    Run the test program with:

        python3 ./expr_tester.py --jobid <job_id> --mongohost <ip address>
                                 --port <port number> [--debug]
                                 --file <path to NLPQL file>

Help for the command line interface can be obtained via this command:

    python3 ./expr_tester.py --help

Extensive debugging info can be generated with the --debug option.

"""

import re
import os
import bz2
import sys
import copy
import string
import argparse
import datetime
import tempfile
import subprocess
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from collections import namedtuple, OrderedDict

# modify path for local testing
# (imports need the ClarityNLP logger)
if __name__ == '__main__':
    cur_dir = sys.path[0]
    nlp_dir, tail = os.path.split(cur_dir)
    sys.path.append(nlp_dir)
    sys.path.append(os.path.join(nlp_dir, 'tasks'))
    sys.path.append(os.path.join(nlp_dir, 'data_access'))

#from bson import ObjectId

try:
    import expr_eval
    import expr_result
except:
    from data_access import expr_eval
    from data_access import expr_result

    
_VERSION_MAJOR = 0
_VERSION_MINOR = 9
_MODULE_NAME   = 'expr_tester.py'

_TRACE = False

_TEST_ID            = 'EXPR_TEST'
_TEST_NLPQL_FEATURE = 'EXPR_TEST'


_FILE_DATA_FIELDS = [
    'context',            # value of context variable in NLPQL file
    'names',              # all defined names in the NLPQL file
    'tasks',              # list of ClarityNLP tasks defined in the NLPQL file
    'primitives',         # names actually used in expressions
    'expressions',        # list of (nlpql_feature, string_def) tuples
    'reduced_expressions' # same but with string_def expressed with primitives
]
FileData = namedtuple('FileData', _FILE_DATA_FIELDS)

# names defined in the test data set
_BASIC_FEATURES = [
    'Temperature',
    'Lesion',
    'hasTachycardia',
    'hasRigors',
    'hasShock',
    'hasDyspnea',
    'hasNausea',
    'hasVomiting'
]

# store computed result sets here, to speed things up
_CACHE = {}


###############################################################################
def _enable_debug():

    global _TRACE
    _TRACE = True


###############################################################################
def _evaluate_expressions(expr_obj_list,
                          mongo_collection_obj,
                          job_id,
                          context_field,
                          is_final):
    """
    Nearly identical to
    nlp/luigi_tools/phenotype_helper.mongo_process_operations
    """

    phenotype_id    = _TEST_ID
    phenotype_owner = _TEST_ID
        
    assert 'subject' == context_field or 'report_id' == context_field

    all_output_docs = []
    is_final_save = is_final

    for expr_obj in expr_obj_list:

        # the 'is_final' flag only applies to the last subexpression
        if expr_obj != expr_obj_list[-1]:
            is_final = False
        else:
            is_final = is_final_save
        
        # evaluate the (sub)expression in expr_obj
        eval_result = expr_eval.evaluate_expression(expr_obj,
                                                    job_id,
                                                    context_field,
                                                    mongo_collection_obj)
            
        # query MongoDB to get result docs
        cursor = mongo_collection_obj.find({'_id': {'$in': eval_result.doc_ids}})

        # initialize for MongoDB result document generation
        phenotype_info = expr_result.PhenotypeInfo(
            job_id = job_id,
            phenotype_id = phenotype_id,
            owner = phenotype_owner,
            context_field = context_field,
            is_final = is_final
        )

        # generate result documents
        if expr_eval.EXPR_TYPE_MATH == eval_result.expr_type:

            output_docs = expr_result.to_math_result_docs(eval_result,
                                                          phenotype_info,
                                                          cursor)
        else:
            assert expr_eval.EXPR_TYPE_LOGIC == eval_result.expr_type

            # flatten the result set into a set of Mongo documents
            doc_map, oid_list_of_lists = expr_eval.flatten_logical_result(eval_result,
                                                                          mongo_collection_obj)
            
            output_docs = expr_result.to_logic_result_docs(eval_result,
                                                           phenotype_info,
                                                           doc_map,
                                                           oid_list_of_lists)

        if len(output_docs) > 0:
            mongo_collection_obj.insert_many(output_docs)
        else:
            print('mongo_process_operations ({0}): ' \
                  'no phenotype matches on "{1}".'.format(eval_result.expr_type,
                                                          eval_result.expr_text))

        # save the expr object and the results
        all_output_docs.append( (expr_obj, output_docs))

    return all_output_docs


###############################################################################
def _delete_prev_results(job_id, mongo_collection_obj):
    """
    Remove all results in the Mongo collection that were computed by
    expression evaluation. Also remove all temp results from a previous run
    of this code, if any.
    """

    # delete all assigned results from a previous run of this code
    result = mongo_collection_obj.delete_many(
        {"job_id":job_id, "nlpql_feature":_TEST_NLPQL_FEATURE})
    print('Removed {0} result docs with the test feature.'.
          format(result.deleted_count))

    # delete all temp results from a previous run of this code
    result = mongo_collection_obj.delete_many(
        {"nlpql_feature":expr_eval.regex_temp_nlpql_feature})
    print('Removed {0} docs with temp NLPQL features.'.
          format(result.deleted_count))
    

###############################################################################
def _banner_print(msg):
    """
    Print the message centered in a border of stars.
    """

    MIN_WIDTH = 79

    n = len(msg)
    
    if n < MIN_WIDTH:
        ws = (MIN_WIDTH - 2 - n) // 2
    else:
        ws = 1

    ws_left = ws
    ws_right = ws

    # add extra space on right to balance if even
    if 0 == n % 2:
        ws_right = ws+1

    star_count = 1 + ws_left + n + ws_right + 1
        
    print('{0}'.format('*'*star_count))
    print('{0}{1}{2}'.format('*', ' '*(star_count-2), '*'))
    print('{0}{1}{2}{3}{4}'.format('*', ' '*ws_left, msg, ' '*ws_right, '*'))
    print('{0}{1}{2}'.format('*', ' '*(star_count-2), '*'))
    print('{0}'.format('*'*star_count))
    

###############################################################################
def _run_selftest_expression(job_id,
                             context_field,
                             expression_str,
                             mongo_collection_obj):
    """
    Evaluate the NLPQL expression in 'expression_str', then iterate through
    the results and extract the set of unique context variables. A context
    variable is either the doc_id or the patient_id, depending on the NLPQL
    evaluation context. Returns the set of unique context variables.
    """

    global _CACHE

    print('\t{0}'.format(expression_str))
    
    # first check the cache and return result if previously evaluated
    if expression_str in _CACHE:
        return _CACHE[expression_str]
    
    parse_result = expr_eval.parse_expression(expression_str, _BASIC_FEATURES)
    if 0 == len(parse_result):
        return set()

    # generate a list of ExpressionObject primitives
    expression_object_list = expr_eval.generate_expressions(_TEST_NLPQL_FEATURE,
                                                            parse_result)
    if 0 == len(expression_object_list):
        return set()

    # evaluate the ExpressionObjects in the list
    eval_results = _evaluate_expressions(expression_object_list,
                                         mongo_collection_obj,
                                         job_id,
                                         context_field,
                                         is_final=False)

    result_set = set()
    for expr_obj, docs in eval_results:
        for doc in docs:
            if _TEST_NLPQL_FEATURE == doc['nlpql_feature']:
                result_set.add(doc[context_field])

    # insert into cache
    _CACHE[expression_str] = result_set
                
    return result_set


###############################################################################
def _to_context_set(context_field, docs):

    feature_set = set()
    for doc in docs:
        assert context_field in doc
        value = doc[context_field]
        feature_set.add(value)

    return feature_set


###############################################################################
def _get_feature_set(mongo_collection_obj, context_field, nlpql_feature):
    """
    Extract the set of all context variables (either doc or patient IDs)
    having the indicated feature.
    """

    docs = mongo_collection_obj.find({'nlpql_feature':nlpql_feature})
    return _to_context_set(context_field, docs)


###############################################################################
def _test_basic_expressions(job_id,     # integer job id from data file
                            cf,         # context field, 'document' or 'subject'
                            mongo_obj):
    print('Called _test_basic_expressions...')
    
    # rename some precomputed sets
    temp   = _CACHE['Temperature']
    lesion = _CACHE['Lesion']

    for expr in _BASIC_FEATURES:
        computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
        expected = _CACHE[expr]
        if computed != expected:
            return False

    expr = 'Temperature AND Lesion'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = temp & lesion
    if computed != expected:
        return False

    # 'Temperature AND field', 'Lesion AND field'
    for field in _BASIC_FEATURES[2:]:
        expr = 'Temperature AND {0}'.format(field)
        computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
        expected = temp & _CACHE[field]
        if computed != expected:
            return False

        expr = 'Lesion AND {0}'.format(field)
        computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
        expected = lesion & _CACHE[field]
        if computed != expected:
            return False

    # 'Temperature OR field', 'Lesion OR field'
    for field in _BASIC_FEATURES[2:]:
        expr = 'Temperature OR {0}'.format(field)
        computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
        expected = temp | _CACHE[field]
        if computed != expected:
            return False

        expr = 'Lesion OR {0}'.format(field)
        computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
        expected = lesion | _CACHE[field]
        if computed != expected:
            return False

    return True


###############################################################################
def _test_pure_math_expressions(job_id,     # integer job id from data file
                                cf,         # context field, 'document' or 'subject'
                                mongo_obj):

    print('Called _test_pure_math_expressions...')
    
    expr = 'Temperature.value >= 100.4'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            'nlpql_feature':'Temperature',
            'value': {'$gte': 100.4}
        })
    expected = _to_context_set(cf, docs)
    if computed != expected:
        return False

    expr = 'Temperature.value >= 1.004e2'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    if computed != expected:
        return False

    expr = '100.4 <= Temperature.value'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    if computed != expected:
        return False

    expr = '(Temperature.value >= (100.4))'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    if computed != expected:
        return False

    expr = 'Temperature.value == 100.4'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            'nlpql_feature':'Temperature',
            'value':100.4
        })
    expected = _to_context_set(cf, docs)
    if computed != expected:
        return False

    expr = 'Temperature.value + 3 ^ 2 < 109'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            'nlpql_feature':'Temperature',
            'value': {'$lt':100}
        })
    expected = _to_context_set(cf, docs)
    if computed != expected:
        return False

    expr = 'Temperature.value ^ 3 + 2 < 941194'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            'nlpql_feature':'Temperature',
            'value': {'$lt': 98}
        })
    expected = _to_context_set(cf, docs)
    if computed != expected:
        return False

    expr = 'Temperature.value % 3 ^ 2 == 2'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            'nlpql_feature':'Temperature',
            'value':101
        })
    expected = _to_context_set(cf, docs)
    if computed != expected:
        return False

    expr = 'Temperature.value * 4 ^ 2 >= 1616'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            'nlpql_feature':'Temperature',
            'value': {'$gte':101}
        })
    expected = _to_context_set(cf, docs)
    if computed != expected:
        return False

    expr = 'Temperature.value / 98.6 ^ 2 < 0.01'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            'nlpql_feature':'Temperature',
            'value': {'$lt':97.2196}
        })
    expected = _to_context_set(cf, docs)
    if computed != expected:
        return False

    expr = '(Temperature.value / 98.6)^2 < 1.02'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            'nlpql_feature':'Temperature',
            'value':{'$lt':99.581}
        })
    expected = _to_context_set(cf, docs)
    if computed != expected:
        return False

    expr = '0 == Temperature.value % 20'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            'nlpql_feature':'Temperature',
            'value':100
        })
    expected = _to_context_set(cf, docs)
    if computed != expected:
        return False

    expr =' Temperature.value >= 100.4 AND Temperature.value < 102'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            'nlpql_feature':'Temperature',
            '$and':
            [
                {'value':{'$gte':100.4}},
                {'value':{'$lt':102}}
            ]
        })
    expected = _to_context_set(cf, docs)
    if computed != expected:
        return False

    expr = '(Lesion.dimension_X <= 5) OR (Lesion.dimension_X >= 45)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            'nlpql_feature':'Lesion',
            '$or':
            [
                {'dimension_X':{'$lte':5}},
                {'dimension_X':{'$gte':45}}
            ]
        })
    expected = _to_context_set(cf, docs)
    if computed != expected:
        return False

    expr = 'Lesion.dimension_X > 15 AND Lesion.dimension_X < 30'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            'nlpql_feature':'Lesion',
            '$and':
            [
                {'dimension_X':{'$gt':15}},
                {'dimension_X':{'$lt':30}}
            ]
        })
    expected = _to_context_set(cf, docs)
    if computed != expected:
        return False

    expr = '((Lesion.dimension_X) > (15)) AND (((Lesion.dimension_X) < (30)))'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    if computed != expected:
        return False

    # redundant math expressions
    
    expr = 'Lesion.dimension_X > 10 AND Lesion.dimension_X < 30'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Lesion'},
                {'dimension_X':{'$gt':10}},
                {'dimension_X':{'$lt':30}}
            ]
        })
    expected = _to_context_set(cf, docs)
    if computed != expected:
        return False

    expr = 'Lesion.dimension_X > 5 AND Lesion.dimension_X > 10 AND ' \
        'Lesion.dimension_X < 40 AND Lesion.dimension_X < 30'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    if computed != expected:
        return False

    expr = '(Lesion.dimension_X > 8 AND Lesion.dimension_X > 5 AND ' \
        'Lesion.dimension_X > 10) AND (Lesion.dimension_X < 40 AND ' \
        'Lesion.dimension_X < 30 AND Lesion.dimension_X < 45)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    if computed != expected:
        return False

    
    return True


###############################################################################
def _test_math_with_multiple_features(job_id,   # integer job id from data file
                                      cf,       # context field
                                      mongo_obj):

    print('Called _test_math_with_multiple_features...')
    
    expr = 'Lesion.dimension_X > 15 AND Lesion.dimension_X < 30 OR ' \
        '(Temperature.value >= 100.4)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            '$or':
            [
                {
                    '$and':
                    [
                        {'nlpql_feature':'Lesion'},
                        {'dimension_X':{'$gt':15}},
                        {'dimension_X':{'$lt':30}}
                    ]
                },
                {
                    '$and':
                    [
                        {'nlpql_feature':'Temperature'},
                        {'value':{'$gte':100.4}}
                    ]
                }
            ]
        })
    expected = _to_context_set(cf, docs)
    if computed != expected:
        return False

    expr = '(Lesion.dimension_X > 15 AND Lesion.dimension_X < 30) AND ' \
        'Temperature.value > 100.4'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs1 = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Lesion'},
                {'dimension_X':{'$gt':15}},
                {'dimension_X':{'$lt':30}}
            ]
        })
    expected1 = _to_context_set(cf, docs1)
    docs2 = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Temperature'},
                {'value':{'$gt':100.4}}
            ]
        })
    expected2 = _to_context_set(cf, docs2)
    expected = set.intersection(expected1, expected2)
    if computed != expected:
        return False

    expr = 'Lesion.dimension_X > 15 AND Lesion.dimension_X < 30 AND ' \
        'Temperature.value > 100.4'    
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    if computed != expected:
        return False

    expr = '(Temperature.value >= 102) AND (Lesion.dimension_X <= 5)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs1 = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Temperature'},
                {'value':{'$gte':102}}
            ]
        })
    expected1 = _to_context_set(cf, docs1)
    docs2 = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Lesion'},
                {'dimension_X':{'$lte':5}}
            ]
        })
    expected2 = _to_context_set(cf, docs2)
    expected = set.intersection(expected1, expected2)
    if computed != expected:
        return False

    expr = '(Temperature.value >= 102) AND (Lesion.dimension_X <= 5) AND ' \
        '(Temperature.value >= 103)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs1 = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Temperature'},
                {'value':{'$gte':102}}
            ]
        })
    expected1 = _to_context_set(cf, docs1)
    docs2 = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Lesion'},
                {'dimension_X':{'$lte':5}}
            ]
        })
    expected2 = _to_context_set(cf, docs2)
    docs3 = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Temperature'},
                {'value':{'$gte':103}}
            ]
        })
    expected3 = _to_context_set(cf, docs3)
    expected = set.intersection(expected1, expected2, expected3)
    if computed != expected:
        return False
    
    return True


###############################################################################
def _test_pure_logic_expressions(job_id, # integer job id
                                 cf,     # context field
                                 mongo_obj):

    print('Called _test_pure_logic_expressions...')
    
    # rename some precomputed sets
    tachy  = _CACHE['hasTachycardia']
    shock  = _CACHE['hasShock']
    rigors = _CACHE['hasRigors']
    dysp   = _CACHE['hasDyspnea']
    nau    = _CACHE['hasNausea']
    vom    = _CACHE['hasVomiting']
    temp   = _CACHE['Temperature']
    lesion = _CACHE['Lesion']
    
    expr = 'hasTachycardia NOT hasShock'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = tachy - shock
    if computed != expected:
        return False

    expr = '(hasTachycardia AND hasDyspnea) NOT hasRigors'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = (tachy & dysp) - rigors
    if computed != expected:
        return False

    expr = '((hasShock) AND (hasDyspnea))'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = shock & dysp
    if computed != expected:
        return False

    expr = '((hasTachycardia) AND (hasRigors OR hasDyspnea OR hasNausea))'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    set1 = _CACHE['hasRigors'] | _CACHE['hasDyspnea'] | _CACHE['hasNausea']
    expected = tachy & (rigors | dysp | nau)
    if computed != expected:
        return False

    expr = '((hasTachycardia)AND(hasRigorsORhasDyspneaORhasNausea))'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    if computed != expected:
        return False

    expr = 'hasTachycardia NOT (hasRigors OR hasDyspnea)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = tachy - (rigors | dysp)
    if computed != expected:
        return False

    expr = 'hasTachycardia NOT (hasRigors OR hasDyspnea OR hasNausea)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = tachy - (rigors | dysp | nau)
    if computed != expected:
        return False

    expr = 'hasTachycardia NOT (hasRigors OR hasDyspnea OR hasNausea OR ' \
        'hasVomiting)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = tachy - (rigors | dysp | nau | vom)
    if computed != expected:
        return False

    expr = 'hasTachycardia NOT (hasRigors OR hasDyspnea OR hasNausea OR ' \
        'hasVomiting OR hasShock)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = tachy - (rigors | dysp | nau | vom | shock)
    if computed != expected:
        return False

    expr = 'hasTachycardia NOT (hasRigors OR hasDyspnea OR hasNausea OR ' \
        'hasVomiting OR hasShock OR Temperature)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = tachy - (rigors | dysp | nau | vom | shock | temp)
    if computed != expected:
        return False
    
    expr = 'hasTachycardia NOT (hasRigors OR hasDyspnea OR hasNausea OR ' \
        'hasVomiting OR hasShock OR Temperature OR Lesion)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = tachy - (rigors | dysp | nau | vom | shock | temp | lesion)
    if computed != expected:
        return False

    expr = 'hasTachycardia NOT (hasRigors AND hasDyspnea)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = tachy - (rigors & dysp)
    if computed != expected:
        return False

    expr = 'hasRigors AND hasTachycardia AND hasDyspnea'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = rigors & tachy & dysp
    if computed != expected:
        return False

    expr = 'hasRigors AND hasDyspnea AND hasTachycardia'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = rigors & dysp & tachy
    if computed != expected:
        return False
    
    expr = 'hasRigors OR hasTachycardia AND hasDyspnea'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = rigors | tachy & dysp
    if computed != expected:
        return False
    
    expr = '(hasRigors OR hasDyspnea) AND hasTachycardia'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = (rigors | dysp) & tachy
    if computed != expected:
        return False
    
    expr = 'hasRigors AND (hasTachycardia AND hasNausea)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = rigors & (tachy & nau)
    if computed != expected:
        return False
    
    expr = '(hasShock OR hasDyspnea) AND (hasTachycardia OR hasNausea)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = (shock | dysp) & (tachy | nau)
    if computed != expected:
        return False
    
    expr = '(hasShock OR hasRigors) NOT (hasTachycardia OR hasNausea)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = (shock | rigors) - (tachy | nau)
    if computed != expected:
        return False
    
    expr = 'Temperature AND (hasDyspnea OR hasTachycardia)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = temp & (dysp | tachy)
    if computed != expected:
        return False
    
    expr = 'Lesion AND (hasDyspnea OR hasTachycardia)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = lesion & (dysp | tachy)
    if computed != expected:
        return False
    
    return True


###############################################################################
def _test_mixed_math_and_logic_expressions(job_id, # integer job id
                                           cf,     # context field
                                           mongo_obj):

    print('Called _test_mixed_math_and_logic_expressions...')
    
    # rename some precomputed sets
    tachy  = _CACHE['hasTachycardia']
    shock  = _CACHE['hasShock']
    rigors = _CACHE['hasRigors']
    dysp   = _CACHE['hasDyspnea']
    nau    = _CACHE['hasNausea']
    vom    = _CACHE['hasVomiting']
    temp   = _CACHE['Temperature']
    lesion = _CACHE['Lesion']

    expr = 'hasNausea AND Temperature.value >= 100.4'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Temperature'},
                {'value':{'$gte':100.4}}
            ]
        })
    set1 = _to_context_set(cf, docs)
    expected = nau & set1
    if computed != expected:
        return False

    expr = 'Lesion.dimension_X < 10 AND hasRigors'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Lesion'},
                {'dimension_X':{'$lt':10}}
            ]
        })
    set1 = _to_context_set(cf, docs)
    expected = set1 & rigors
    if computed != expected:
        return False
    
    expr = 'Lesion.dimension_X < 10 OR hasRigors'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Lesion'},
                {'dimension_X':{'$lt':10}}
            ]
        })
    set1 = _to_context_set(cf, docs)
    expected = set1 | rigors
    if computed != expected:
        return False

    expr = '(hasRigors OR hasTachycardia OR hasNausea OR hasVomiting OR ' \
        'hasShock) AND '                                                  \
        '(Temperature.value >= 100.4 AND Temperature.value < 102)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Temperature'},
                {'value':{'$gte':100.4}},
                {'value':{'$lt':102}}
            ]
        })
    set1 = _to_context_set(cf, docs)
    expected = (rigors | tachy | nau | vom | shock) & set1
    if computed != expected:
        return False

    expr = 'Lesion.dimension_X > 10 AND Lesion.dimension_X < 30 OR ' \
        '(hasRigors OR hasTachycardia AND hasDyspnea)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Lesion'},
                {'dimension_X':{'$gt':10}},
                {'dimension_X':{'$lt':30}}
            ]
        })
    set1 = _to_context_set(cf, docs)
    expected = set1 | (rigors | tachy & dysp)
    if computed != expected:
        return False

    expr = 'Lesion.dimension_X > 10 AND Lesion.dimension_X < 30 OR ' \
        'hasRigors OR hasTachycardia OR hasDyspnea'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = set1 | rigors | tachy | dysp
    if computed != expected:
        return False

    expr = '(Lesion.dimension_X > 10 AND Lesion.dimension_X < 30) NOT ' \
        '(hasRigors OR hasTachycardia OR hasDyspnea)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = set1 - (rigors | tachy | dysp)
    if computed != expected:
        return False

    expr = '(Temperature.value >= 100.4) AND ' \
        'hasDyspnea AND hasNausea AND hasVomiting'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Temperature'},
                {'value':{'$gt':100.4}}
            ]
        })
    set1 = _to_context_set(cf, docs)
    expected = set1 & dysp & nau & vom
    if computed != expected:
        return False

    expr = 'hasRigors OR (hasTachycardia AND hasDyspnea) AND ' \
        'Temperature.value >= 100.4'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = rigors | (tachy & dysp) & set1
    if computed != expected:
        return False

    expr = '(hasRigors OR hasTachycardia OR hasDyspnea OR hasNausea) AND ' \
        'Temperature.value >= 100.4'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = (rigors | tachy | dysp | nau) & set1
    if computed != expected:
        return False

    expr = 'Lesion.dimension_X < 10 OR hasRigors AND Lesion.dimension_X > 30'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs1 = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Lesion'},
                {'dimension_X':{'$lt':10}}
            ]
        })
    set1 = _to_context_set(cf, docs1)
    docs2 = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Lesion'},
                {'dimension_X':{'$gt':30}}
            ]
        })
    set2 = _to_context_set(cf, docs2)
    expected = set1 | rigors & set2
    if computed != expected:
        return False
    
    # redundant math expressions

    expr = 'Lesion.dimension_X > 50'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Lesion'},
                {'dimension_X':{'$gt':50}}
            ]
        })
    set1 = _to_context_set(cf, docs)
    if computed != set1:
        return False

    expr = 'Lesion.dimension_X > 30 AND Lesion.dimension_X > 50'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    if computed != set1:
        return False

    expr = 'Lesion.dimension_X > 12 AND Lesion.dimension_X > 30 AND ' \
        'Lesion.dimension_X > 50'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    if computed != set1:
        return False

    expr = '(Lesion.dimension_X > 50) OR (hasNausea AND hasDyspnea)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected = set1 | (nau & dysp)
    if computed != expected:
        return False

    expr = '(Lesion.dimension_X > 30 AND Lesion.dimension_X > 50) OR ' \
        '(hasNausea AND hasDyspnea)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    if computed != expected:
        return False

    expr = '(Lesion.dimension_X > 12 AND Lesion.dimension_X > 50) OR ' \
        '(hasNausea AND hasDyspnea)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    if computed != expected:
        return False

    expr = '(Lesion.dimension_X > 12 AND Lesion.dimension_X > 30 AND ' \
        'Lesion.dimension_X > 50) OR (hasNausea AND hasDyspnea)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    if computed != expected:
        return False
    
    return True


###############################################################################
def _test_not_with_positive_logic(job_id, # integer job id
                                  cf,     # context field
                                  mongo_obj):

    print('Called _test_not_with_positive_logic...')
    
    # rename some precomputed sets
    tachy  = _CACHE['hasTachycardia']
    rigors = _CACHE['hasRigors']
    dysp   = _CACHE['hasDyspnea']

    # expression without using NOT
    expr = '(hasRigors OR hasDyspnea OR hasTachycardia) AND ' \
        '(Temperature.value < 100.4)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Temperature'},
                {'value':{'$lt':100.4}}
            ]
        })
    set1 = _to_context_set(cf, docs)
    expected = (rigors | dysp | tachy) & set1
    if computed != expected:
        return False

    # equivalent using NOT
    expr = '(hasRigors OR hasDyspnea OR hasTachycardia) NOT ' \
        '(Temperature.value >= 100.4)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    if computed != expected:
        return False

    # expression 2 without using NOT
    expr = '(hasRigors OR hasDyspnea) AND ' \
        '(Temperature.value >= 99.5 AND Temperature.value <= 101.5)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Temperature'},
                {'value':{'$gte':99.5}},
                {'value':{'$lte':101.5}}
            ]
        })
    set1 = _to_context_set(cf, docs)
    expected = (rigors | dysp) & set1
    if computed != expected:
        return False

    # equivalent using NOT
    expr = '(hasRigors OR hasDyspnea) NOT ' \
        '(Temperature.value < 99.5 OR Temperature.value > 101.5)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    if computed != expected:
        return False
    
    return True


###############################################################################
def _test_two_component_or(job_id, # integer job id
                           cf,     # context field
                           mongo_obj):
    """
    Compute 'feature1 OR feature2' and check the cardinality against the
    equivalent expression using NOT.  The relation below holds, letting f1 and
    f2 denote two different features such as 'hasTachycardia', 'hasDyspnea',
    etc.

        |f1 OR f2| == |f1| + |f2| - |f1 AND f2|

    (Think of a Venn diagram. The number of elements in the union of two sets
    equals the sum of the cardinalities of both sets minus the overlap,
    if any.)

    In NLPQL, we can get the unique number of elements in the union by
    evaluating this expression:

        (f1 OR f2) NOT (f1 AND f2)

    Then, this relation must also hold:

        (union with overlap) == (union excluding overlap) + (overlap)

        |f1 OR f2| == |(f1 OR f2) NOT (f1 AND f2)| + |f1 AND f2|

    The code below evaluates these expressions for all pairs of features
    in _BASIC_FEATURES.

    """

    print('Called _test_two_component_or...')
    
    for i, feature1 in enumerate(_BASIC_FEATURES):
        if feature1 == _BASIC_FEATURES[-1]:
            break

        # expr == 'feature1'
        computed_f1 = _run_selftest_expression(job_id, cf, feature1, mongo_obj)
        expected_f1 = _CACHE[feature1]
        if computed_f1 != expected_f1:
            print('*** 1 ***')
            return False

        # set of all context variable values for feature1
        set1 = _CACHE[feature1]
        
        for j in range(i+1, len(_BASIC_FEATURES)):
            feature2 = _BASIC_FEATURES[j]
            print('\t{0} OR {1}'.format(feature1, feature2))

            # expr == 'feature2'
            computed_f2 = _run_selftest_expression(job_id, cf, feature2, mongo_obj)
            expected_f2 = _CACHE[feature2]
            if computed_f2 != expected_f2:
                print('*** 3 ***')
                return False

            # set of all context variable values for feature2
            set2 = _CACHE[feature2]

            # expr == 'feature1 OR feature2'
            expr = '{0} OR {1}'.format(feature1, feature2)
            computed_or = _run_selftest_expression(job_id, cf, expr, mongo_obj)
            expected_or = set1 | set2
            if computed_or != expected_or:
                print('*** 2 ***')
                return False

            # expr == 'feature1 AND feature2'
            expr = '{0} AND {1}'.format(feature1, feature2)
            computed_and = _run_selftest_expression(job_id, cf, expr, mongo_obj)
            expected_and = set1 & set2
            if computed_and != expected_and:
                print('*** 4 ***')
                return False

            # expr == '(feature1 OR feature2) NOT (feature1 AND feature2)'
            expr = '({0} OR {1}) NOT ({0} AND {1})'.format(feature1, feature2)
            computed_not = _run_selftest_expression(job_id, cf, expr, mongo_obj)
            expected_not = (set1 | set2) - (set1 & set2)
            if computed_not != expected_not:
                return False

            # vertical bars to denote set cardinality

            # first check:
            #     |f1 OR f2| == |f1| + |f2| - |f1 AND f2|
            lhs = len(computed_or)
            rhs = len(computed_f1) + len(computed_f2) - len(computed_and)
            if lhs != rhs:
                print('*** 6 ***')
                return False
            if lhs != len(expected_or):
                print('*** 7 ***')
                return False

            # second check:
            #    |f1 OR f2| == |(f1 OR f2) NOT (f1 AND f2)| + |f1 AND f2|
            lhs = len(computed_or)
            rhs = len(computed_not) + len(computed_and)
            if lhs != rhs:
                print('*** 8 ***')
                return False
            if lhs != len(expected_or):
                print('*** 9 ***')
                return False
    
    return True


###############################################################################
def _test_three_component_or(feature_A,  # feature or expr in _CACHE
                             feature_B,
                             feature_C,
                             job_id,     # ClarityNLP job id
                             cf,         # context field
                             mongo_obj):
    """
    Compute 'feature1 OR feature2 OR feature3' and check the cardinality
    against the equivalent expression using NOT.  The relation below holds,
    letting A, B, and C denote different features such as 'hasTachycardia',
    'hasDyspnea', etc.

        |A OR B OR C| == |A| + |B| + |C|
                         - (|A AND B| + |A AND C| + |B AND C|)
                         + |A AND B AND C|   

    This is essentially a statement about a three-set Venn diagram. The
    number of elements in the union of the three sets equals the sum of
    the elements in the individual sets, minus the pairwise overlap. But
    removing the pairwise overlap subtracts out any simultaneous overlap
    among the three sets TWICE, so it gets added back in.

    In NLPQL, we can get the unique number of elements in the union with
    this expression:

        (A OR B OR C) NOT ( (A AND B) OR (A AND C) OR (B AND C) ) OR (A AND B AND C)

    This needs to be rearranged into this equivalent form, so that the NOT
    applies to ALL the available documents or patients:

        ((A OR B OR C) OR (A AND B AND C)) NOT ( (A AND B) OR (A AND C) OR (B AND C) )

    One further consideration applies. The OR operation using the parenthesized
    operands prior to the NOT actually includes any overlap between those two
    operands. This overlap needs to be subtracted, as was done in the function
    _test_two_component_or.

    With these considerations, this relation must hold between the
    cardinalities of both sides:

        |A OR B OR C| == |((A OR B OR C) OR (A AND B AND C)) NOT ( (A AND B) OR (A AND C) OR (B AND C) )|
                        +|A AND B| + |A AND C| + |B AND C|
                        -|A AND B AND C|
                        -|(A OR B OR C) AND (A AND B AND C)|
 
    """

    print('Called _test_three_component_or...')
    
    A = _CACHE[feature_A]
    B = _CACHE[feature_B]
    C = _CACHE[feature_C]

    # A  OR  B  OR  C
    expr = '{0} OR {1} OR {2}'.format(feature_A, feature_B, feature_C)
    
    computed_or = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected_or = A | B | C
    if computed_or != expected_or:
        print('*** 1 ***')
        return False

    len_A = len(A)
    len_B = len(B)
    len_C = len(C)
    len_A_or_B_or_C = len(computed_or)

    # A AND B
    expr = '{0} AND {1}'.format(feature_A, feature_B)
    computed_AB = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected_AB = A & B
    if computed_AB != expected_AB:
        print('*** 2 ***')
        return False

    len_AB = len(computed_AB)

    # A AND C
    expr = '{0} AND {1}'.format(feature_A, feature_C)
    computed_AC = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected_AC = A & C
    if computed_AC != expected_AC:
        print('*** 3 ***')
        return False

    len_AC = len(computed_AC)

    # B AND C
    expr = '{0} AND {1}'.format(feature_B, feature_C)
    computed_BC = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected_BC = B & C
    if computed_BC != expected_BC:
        print('*** 4 ***')
        return False

    len_BC = len(computed_BC)

    # A AND B AND C
    expr = '{0} AND {1} AND {2}'.format(feature_A, feature_B, feature_C)
    computed_ABC = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected_ABC = A & B & C
    if computed_ABC != expected_ABC:
        print('*** 5 ***')
        return False

    len_ABC = len(computed_ABC)
    
    # complex expression involving NOT
    expr = '(({0} OR {1} OR {2}) OR ({0} AND {1} AND {2})) NOT ' \
        '( ({0} AND {1}) OR ({0} AND {2}) OR ({1} AND {2}) )'.format(
            feature_A, feature_B, feature_C)
    computed_not = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    set1 = (A | B | C) | (A & B & C)
    set2 = (A & B) | (A & C) | (B & C)
    expected_not = set1 - set2
    if computed_not != expected_not:
        print('*** 6 ***')
        return False

    len_not = len(computed_not)

    # extra overlap
    expr = '({0} OR {1} OR {2}) AND ({0} AND {1} AND {2})'.format(
        feature_A, feature_B, feature_C)
    computed_extra = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    expected_extra = (A | B | C) & (A & B & C)
    if computed_extra != expected_extra:
        print('*** 7 ***')
        return False

    len_extra = len(computed_extra)
    
    # first check
    rhs = len_A + len_B + len_C - (len_AB + len_AC + len_BC) + len_ABC
    if len_A_or_B_or_C != rhs:
        print('*** 8 ***')
        return False

    # second check
    rhs = len_not + len_AB + len_AC + len_BC - len_ABC - len_extra
    if len_A_or_B_or_C != rhs:
        return False
    
    return True


###############################################################################
def _test_three_component_or_with_math(job_id,      # ClarityNLP job id
                                       cf,          # context field
                                       mongo_obj):
    """
    Evaluate some math expressions to load into _CACHE, then test the
    cardinality of the result.
    """

    print('Called _test_three_component_or_with_math...')

    _run_selftest_expression(job_id, cf, 'hasDyspnea', mongo_obj)
    _run_selftest_expression(job_id, cf, 'hasNausea', mongo_obj)
    
    expr = '(Temperature.value >= 100.4 AND Temperature.value < 102)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Temperature'},
                {'value':{'$gte':100.4}},
                {'value':{'$lt':102}}
            ]
        })
    expected = _to_context_set(cf, docs)
    if computed != expected:
        print('*** 1 ***')
        return False
    
    if not _test_three_component_or('hasDyspnea',
                                    'hasNausea',
                                    expr,
                                    job_id, cf, mongo_obj):
        print('*** 2 ***')
        return False

    expr = '(Lesion.dimension_X >= 5 AND Lesion.dimension_Y < 30)'
    computed = _run_selftest_expression(job_id, cf, expr, mongo_obj)
    docs = mongo_obj.find(
        {
            '$and':
            [
                {'nlpql_feature':'Lesion'},
                {'dimension_X':{'$gte':5}},
                {'dimension_Y':{'$lt':30}}
            ]
        })
    expected = _to_context_set(cf, docs)
    if computed != expected:
        print('*** 3 ***')
        return False

    if not _test_three_component_or('hasDyspnea',
                                    expr,
                                    'hasNausea',
                                    job_id, cf, mongo_obj):
        print('*** 3 ***')
        return False
    
    return True


###############################################################################
def _selftest(job_id,      # integer job ID from a ClarityNLP run
              cf,          # context field
              mongo_obj):  # connected MongoDB collection object

    # compute some basic expressions and load cache
    _CACHE['Temperature']    = _get_feature_set(mongo_obj, cf, 'Temperature')
    _CACHE['Lesion']         = _get_feature_set(mongo_obj, cf, 'Lesion')
    _CACHE['hasRigors']      = _get_feature_set(mongo_obj, cf, 'hasRigors')
    _CACHE['hasDyspnea']     = _get_feature_set(mongo_obj, cf, 'hasDyspnea')
    _CACHE['hasNausea']      = _get_feature_set(mongo_obj, cf, 'hasNausea')
    _CACHE['hasVomiting']    = _get_feature_set(mongo_obj, cf, 'hasVomiting')
    _CACHE['hasShock']       = _get_feature_set(mongo_obj, cf, 'hasShock')
    _CACHE['hasTachycardia'] = _get_feature_set(mongo_obj, cf, 'hasTachycardia')

    
    if not _test_basic_expressions(job_id, cf, mongo_obj):
        return False
    if not _test_pure_math_expressions(job_id, cf, mongo_obj):
        return False
    if not _test_math_with_multiple_features(job_id, cf, mongo_obj):
        return False
    if not _test_pure_logic_expressions(job_id, cf, mongo_obj):
        return False
    if not _test_mixed_math_and_logic_expressions(job_id, cf, mongo_obj):
        return False
    if not _test_not_with_positive_logic(job_id, cf, mongo_obj):
        return False
    if not _test_two_component_or(job_id, cf, mongo_obj):
        return False

    if not _test_three_component_or('hasShock',
                                    'hasDyspnea',
                                    'hasTachycardia',
                                    job_id, cf, mongo_obj):
        return False

    if not _test_three_component_or('hasRigors',
                                    'hasDyspnea',
                                    'hasNausea',
                                    job_id, cf, mongo_obj):
        return False

    if not _test_three_component_or_with_math(job_id, cf, mongo_obj):
        return False

    return True


###############################################################################
def _run_self_tests(job_id      = 11222,
                    context_var = 'patient',
                    mongohost   = 'localhost',
                    mongoport   = 27017,
                    debug       = False):
    """
    Run test expressions and verify results.
    """

    if debug:
        _enable_debug()
        expr_eval.enable_debug()
    
    DB_NAME         = 'claritynlp_eval_test'
    COLLECTION_NAME = 'eval_test_data'
    TEST_FILE_NAME  = 'expr_test_data.json.bz2'

    # decompress, read, and decode the data file
    test_data = None
    with bz2.open(TEST_FILE_NAME, 'rb') as infile:
        test_data = infile.read().decode('utf-8')

    if test_data is None:
        print('*** Error decompressing test data file ***')
        print('\tFilename: {0}'.format(TEST_FILE_NAME))
        return False

    # write data to temp file, then load into Mongo via mongoimport
    with tempfile.TemporaryDirectory() as dirname:
        json_file = os.path.join(dirname, 'expr_test_data.json')
        with open(json_file, 'wt') as outfile:
            outfile.write(test_data)

        # use mongoimport to load JSON file containing test data
        command = []
        command.append('mongoimport')
        command.append('--host')
        command.append(str(mongohost))
        command.append('--port')
        command.append(str(mongoport))
        command.append('--db')
        command.append(DB_NAME)
        command.append('--collection')
        command.append(COLLECTION_NAME)
        command.append('--file')
        command.append(json_file)
        command.append('--stopOnError')
        command.append('--drop')

        cp = subprocess.run(command,
                            stdout=subprocess.PIPE,
                            universal_newlines=True)
        if 0 != len(cp.stdout):
            # an error occurred
            print(cp.stdout)
            return False

    # must either be a patient or document context
    context_var = context_var.lower()
    assert 'patient' == context_var or 'document' == context_var

    # determine context field from the context varialbe
    if 'patient' == context_var:
        cf = 'subject'
    else:
        cf = 'report_id'

    all_ok = False
    
    try:
        mongo_client_obj = MongoClient(mongohost, mongoport)
        mongo_db_obj = mongo_client_obj[DB_NAME]
        mongo_obj = mongo_db_obj[COLLECTION_NAME]

        # run the test suite
        all_ok = _selftest(job_id, cf, mongo_obj)
        
    except ConnectionFailure as e:
        print('*** Mongo exception: ConnectionFailure ***')
        print(e)
        
    # drop the collection and database
    if mongo_obj is not None:
        mongo_obj.drop()
    if mongo_client_obj is not None:
        mongo_client_obj.drop_database(DB_NAME)

    if all_ok:
        print('\nAll tests passed.')
    else:
        print('\nOne or more tests failed.')
        
    return all_ok

    
###############################################################################
def _run_tests(job_id,
               final_nlpql_feature,
               command_line_expression,
               context_var,
               mongo_collection_obj,
               num,
               is_final,
               name_list=None,
               debug=False):

    assert command_line_expression is not None    
    
    # must either be a patient or document context
    context_var = context_var.lower()
    assert 'patient' == context_var or 'document' == context_var

    if 'patient' == context_var:
        context_field = 'subject'
    else:
        context_field = 'report_id'

    # cleanup so that database only contains data generated by data_gen.nlpql
    # not from previous runs of this test code
    _delete_prev_results(job_id, mongo_collection_obj)

    if debug:
        _enable_debug()
        expr_eval.enable_debug()

    # get all defined names, helps resolve tokens if bad expression formatting
    the_name_list = _BASIC_FEATURES
    if name_list is not None:
        the_name_list = name_list
        
    expressions = [command_line_expression]
        
    counter = 1
    for e in expressions:

        print('[{0:3}]: "{1}"'.format(counter, e))

        parse_result = expr_eval.parse_expression(e, the_name_list)
        if 0 == len(parse_result):
            print('\n*** parse_expression failed ***\n')
            break
        
        # generate a list of ExpressionObject primitives
        expression_object_list = expr_eval.generate_expressions(final_nlpql_feature,
                                                                parse_result)
        if 0 == len(expression_object_list):
            print('\n*** generate_expressions failed ***\n')
            break
        
        # evaluate the ExpressionObjects in the list
        results = _evaluate_expressions(expression_object_list,
                                        mongo_collection_obj,
                                        job_id,
                                        context_field,
                                        is_final)

        _banner_print(e)
        for expr_obj, output_docs in results:
            print()
            print('Subexpression text: {0}'.format(expr_obj.expr_text))
            print('Subexpression type: {0}'.format(expr_obj.expr_type))
            print('      Result count: {0}'.format(len(output_docs)))
            print('     NLPQL feature: {0}'.format(expr_obj.nlpql_feature))
            print('\nResults: ')

            n = len(output_docs)
            if 0 == n:
                print('\tNone.')
                continue

            if expr_eval.EXPR_TYPE_MATH == expr_obj.expr_type:
                for k in range(n):
                    if k < num or k > n-num:
                        doc = output_docs[k]
                        print(doc)
                        print('[{0:6}]: Document ...{1}, NLPQL feature {2}:'.
                              format(k, str(doc['_id'])[-6:],
                                     expr_obj.nlpql_feature))
                        
                        if 'history' in doc:
                            assert 1 == len(doc['history'])
                            data_field = doc['history'][0].data
                        else:
                            data_field = doc['value']

                        if 'subject' == context_field:
                            context_str = 'subject: {0:8}'.format(doc['subject'])
                        else:
                            context_str = 'report_id: {0:8}'.format(doc['report_id'])
                            
                        print('\t[{0:6}]: _id: {1} nlpql_feature: {2:16} ' \
                              '{3} data: {4}'.
                              format(k, doc['_id'], doc['nlpql_feature'],
                                     context_str, data_field))
                    elif k == num:
                        print('\t...')

            else:
                for k in range(n):
                    if k < num or k > n-num:
                        doc = output_docs[k]
                        print('[{0:6}]: Document ...{1}, NLPQL feature {2}:'.
                              format(k, str(doc['_id'])[-6:],
                                     expr_obj.nlpql_feature))

                        history = doc[expr_result.HISTORY_FIELD]
                        for tup in history:
                            if isinstance(tup.data, float):

                            # format data depending on whether float or string
                                data_string = '{0:<10}'.format(tup.data)
                            else:
                                data_string = '{0}'.format(tup.data)

                            if 'subject' == context_field:
                                context_str = 'subject: {0:8}'.format(tup.subject)
                            else:
                                context_str = 'report_id: {0:8}'.format(tup.report_id)

                            print('\t\t_id: ...{0} operation: {1:20} '  \
                                  'nlpql_feature: {2:16} {3} ' \
                                  'data: {4} '.
                                  format(str(tup.oid)[-6:], tup.pipeline_type,
                                         tup.nlpql_feature, context_str,
                                         data_string))
                    elif k == num:
                        print('\t...')
                
        counter += 1
        print()

        # exit if user provided an expression on the command line
        if command_line_expression is not None:
            break

    return True


###############################################################################
def _reduce_expressions(file_data):

    # this needs to be done after token resolution with the name_list
    # also need whitespace between all tokens
    # (expr_eval.is_valid)

    if _TRACE:
        print('called _reduce_expressions...')
    
    task_names = set(file_data.tasks)
    defined_names = set(file_data.names)
    
    expr_dict = OrderedDict()
    for expr_name, expr_def in file_data.expressions:
        expr_dict[expr_name] = expr_def

    all_primitive = False
    while not all_primitive:
        all_primitive = True
        for expr_name, expr_def in expr_dict.items():
            tokens = expr_def.split()
            is_composite = False
            for index, token in enumerate(tokens):
                # only want NLPQL-defined names
                if token not in defined_names:
                    #print('not in defined_names: {0}'.format(token))
                    continue
                elif token in task_names:
                    # cannot reduce further
                    #print('Expression "{0}": primitive name "{1}"'.
                    #      format(expr_name, token))
                    continue
                elif token != expr_name and token in expr_dict:
                    is_composite = True
                    #print('Expression "{0}": composite name "{1}"'.
                    #      format(expr_name, token))
                    # expand and surround with space-separated parens
                    new_token = '( ' + expr_dict[token] + r' )'
                    tokens[index] = new_token
            if is_composite:
                expr_dict[expr_name] = ' '.join(tokens)
                all_primitive = False

    # scan RHS of each expression and ensure expressed entirely in primitives
    primitives = set()
    for expr_name, expr_def in expr_dict.items():
        tokens = expr_def.split()
        for token in tokens:
            if -1 != token.find('.'):
                nlpql_feature, field = token.split('.')
            else:
                nlpql_feature = token
            if token not in defined_names:
                continue
            assert nlpql_feature in task_names
            primitives.add(nlpql_feature)

    assert 0 == len(file_data.reduced_expressions)
    for expr_name, reduced_expr in expr_dict.items():
        file_data.reduced_expressions.append( (expr_name, reduced_expr) )
    assert len(file_data.reduced_expressions) == len(file_data.expressions)
    
    assert 0 == len(file_data.primitives)
    for p in primitives:
        file_data.primitives.append(p)
        
    return file_data


###############################################################################
def _parse_file(filepath):
    """
    Read the NLPQL file and extract the context, nlpql_features, and 
    associated expressions. Returns a FileData namedtuple.
    """

    # repeated whitespace replaced with single space below, so can use just \s
    str_context_statement = r'context\s(?P<context>(patient|document));'
    regex_context_statement = re.compile(str_context_statement, re.IGNORECASE)

    str_expr_statement = r'\bdefine\s(final\s)?(?P<feature>[^:]+):\s'  +\
                         r'where\s(?P<expr>[^;]+);'
    regex_expr_statement = re.compile(str_expr_statement, re.IGNORECASE)

    # ClarityNLP task statements have no 'where' clause
    str_task_statement = r'\bdefine\s(final\s)?(?P<feature>[^:]+):\s(?!where)'
    regex_task_statement = re.compile(str_task_statement, re.IGNORECASE)
    
    with open(filepath, 'rt') as infile:
        text = infile.read()

    # strip comments
    text = re.sub(r'//[^\n]+\n', ' ', text)

    # replace newlines with spaces for regex simplicity
    text = re.sub(r'\n', ' ', text)

    # replace repeated spaces with a single space
    text = re.sub(r'\s+', ' ', text)

    # extract the context
    match = regex_context_statement.search(text)
    if match:
        context = match.group('context').strip()
    else:
        print('*** parse_file: context statement not found ***')
        sys.exit(-1)

    # extract expression definitions
    expression_dict = OrderedDict()
    iterator = regex_expr_statement.finditer(text)
    for match in iterator:
        feature = match.group('feature').strip()
        expression = match.group('expr').strip()
        if feature in expression_dict:
            print('*** parse_file: multiple definitions for "{0}" ***'.
                  format(feature))
            sys.exit(-1)
        expression_dict[feature] = expression

    # extract task definitions
    task_list = []
    iterator = regex_task_statement.finditer(text)
    for match in iterator:
        task = match.group('feature').strip()
        if task in task_list:
            print('*** parse_file: multiple definitions for "{0}" ***'.
                  format(task))
            sys.exit(-1)
        task_list.append(task)

    # check task names to ensure not also an expression name
    for t in task_list:
        if t in expression_dict:
            print('*** parse_file: multiple definitions for "{0}" ***'.
                  format(t))
            sys.exit(-1)

    # build list of all names
    name_list = []
    for task_name in task_list:
        name_list.append(task_name)
    for expression_name in expression_dict.keys():
        name_list.append(expression_name)

    file_data = FileData(
        context = context,
        names = name_list,
        primitives = [],   # computed later
        tasks = task_list,
        reduced_expressions = [],
        expressions = [ (expr_name, expr_def) for
                        expr_name,expr_def in expression_dict.items()]
    )

    # reduce the expressions to their most primitive form
    file_data = _reduce_expressions(file_data)

    if _TRACE:
        print('FILE DATA AFTER EXPRESSION REDUCTION: ')
        print('\t    context: {0}'.format(file_data.context))
        print('\t task_names: {0}'.format(file_data.tasks))
        print('\t      names: {0}'.format(file_data.names))
        print('\t primitives: {0}'.format(file_data.primitives))
        expression_count = len(file_data.expressions)
        if 0 == expression_count:
            print('\texpressions: None found')
        else:
            print('\texpressions: ')
            for i in range(len(file_data.expressions)):
                expr_name, expr_def = file_data.expressions[i]
                expr_name, expr_reduced = file_data.reduced_expressions[i]
                print('{0}'.format(expr_name))
                print('\toriginal: {0}'.format(expr_def))
                print('\t reduced: {0}'.format(expr_reduced))

    return file_data
        

###############################################################################
def _get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Run validation tests on the expression evaluator.'
    )

    parser.add_argument('-v', '--version',
                        action='store_true',
                        help='show the version string and exit')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='print debug information to stdout during the run')
    parser.add_argument('-c', '--context',
                        default='patient',
                        help='expression evaluation context, either ' \
                        '"patient" or "document", default is "patient"')
    parser.add_argument('-j', '--jobid',
                        default=11222,
                        help='integer job id of a previous ClarityNLP run')
    parser.add_argument('-i', '--isfinal',
                        action='store_true',
                        default=False,
                        help='generate an NLPQL "final" result. Default is to ' \
                        'generate an "intermediate" result.')
    parser.add_argument('-m', '--mongohost',
                        default='localhost',
                        help='IP address of MongoDB host ' \
                        '(default is localhost)')
    parser.add_argument('-p', '--mongoport',
                        default=27017,
                        help='port number for MongoDB host ' \
                        '(default is 27017)')
    parser.add_argument('-n', '--num',
                        default=16,
                        help='number of results to display at start and ' \
                        'end of results array (default is 16)')
    parser.add_argument('-e', '--expr',
                        help='NLPQL expression to evaluate. If this option ' \
                        'is present the -f option cannot be used.')
    parser.add_argument('-f', '--filename',
                        help='NLPQL file to process. If this option is ' \
                        'present the -e option cannot be used.')

    args = parser.parse_args()

    if 'version' in args and args.version:
        print(_get_version())
        sys.exit(0)

    debug = False
    if 'debug' in args and args.debug:
        debug = True
        _enable_debug()
        
    job_id = int(args.jobid)
        
    mongohost = args.mongohost
    mongoport = int(args.mongoport)
    is_final  = args.isfinal
    context   = args.context
    num       = int(args.num)

    expr = None
    if 'expr' in args and args.expr:
        expr = args.expr

    filename = None
    if 'filename' in args and args.filename:
        filename = args.filename

    if expr is not None and filename is not None:
        print('Options -e and -f are mutually exclusive.')
        sys.exit(-1)

    name_list = None
    if filename is not None:
        if not os.path.exists(filename):
            print('File not found: "{0}"'.format(filename))
            sys.exit(-1)

        file_data = _parse_file(filename)
        name_list = file_data.names
        
    if filename is not None or expr is not None:
        # live test, connect to ClarityNLP mongo collection nlp.phenotype_results
        mongo_client_obj = MongoClient(mongohost, mongoport)
        mongo_db_obj = mongo_client_obj['nlp']
        mongo_collection_obj = mongo_db_obj['phenotype_results']
        
    # delete any data computed from NLPQL expressions, will recompute
    # the task data is preserved
    if filename is not None:
        for nlpql_feature, expression in file_data.expressions:

            result = mongo_collection_obj.delete_many({"job_id":job_id,
                                                       "nlpql_feature":nlpql_feature})
            print('Removed {0} docs with NLPQL feature {1}.'.
                  format(result.deleted_count, nlpql_feature))

    if filename is not None:
        # compute all expressions defined in the NLPQL file
        context = file_data.context
        for nlpql_feature, expression in file_data.expressions:
            _run_tests(job_id,
                       nlpql_feature,
                       expression,
                       context,
                       mongo_collection_obj,
                       num,
                       is_final,
                       name_list,
                       debug)
    elif expr is not None:
        # command-line expression uses the test feature
        final_nlpql_feature = _TEST_NLPQL_FEATURE
    
        _run_tests(job_id,
                   final_nlpql_feature,
                   expr,
                   context,
                   mongo_collection_obj,
                   num,
                   is_final,
                   name_list,
                   debug)        
    else:
        _run_self_tests(job_id,
                        context,
                        mongohost,
                        mongoport,
                        debug)
        
