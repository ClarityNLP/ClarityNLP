#!/usr/bin/env python3
"""
This is a program for testing the ClarityNLP NLPQL expression evaluator.

It assumes that a run of the NLPQL file 'data_gen.nlpql' has already been
performed. You will need to know the job_id from that run to use this code.

Add your desired expression to the list in _run_tests, then evaluate it using
the data from your ClarityNLP run.
Use this command:

    python3 ./expr_tester.py --jobid <job_id> --mongohost <ip address>
                             --port <port number> --num <number> [--debug]


Help for the command line interface can be obtained via this command:

    python3 ./expr_tester.py --help

Extensive debugging info can be generated with the --debug option.

"""

import re
import os
import sys
import copy
import string
import optparse
import datetime
from pymongo import MongoClient
from collections import namedtuple, OrderedDict
#from bson import ObjectId

import expr_eval
import expr_result
from expr_result import HISTORY_FIELD

_VERSION_MAJOR = 0
_VERSION_MINOR = 4
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
    result = mongo_collection_obj.delete_many({"job_id":job_id,
                                               "nlpql_feature":_TEST_NLPQL_FEATURE})
    print('Removed {0} result docs with the test feature.'.
          format(result.deleted_count))

    # delete all temp results from a previous run of this code
    result = mongo_collection_obj.delete_many({"nlpql_feature":expr_eval.regex_temp_nlpql_feature})
    print('Removed {0} docs with temp NLPQL features.'.
          format(result.deleted_count))
    

###############################################################################
def banner_print(msg):
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
def _run_tests(job_id,
               final_nlpql_feature,
               command_line_expression,
               context_var,
               mongo_collection_obj,
               num,
               is_final,
               name_list=None,
               debug=False):

    global _TRACE

    # names define in data_gen.nlpql; used if expressions are entered on the
    # command line or uncommented in the EXPRESSIONS list below
    NAME_LIST = [
        'hasRigors', 'hasDyspnea', 'hasNausea', 'hasVomiting', 'hasShock',
        'hasTachycardia', 'hasLesion', 'Temperature', 'Lesion',
        'hasFever', 'hasSepsisSymptoms', 'hasTempAndSepsisSymptoms',
        'hasSepsis', 'hasLesionAndSepsisSymptoms', 'hasLesionAndTemp',
        'hasLesionTempAndSepsisSymptoms'
    ]

    EXPRESSIONS = [

        # counts are for job 11222
        
        # all temperature measurements
        # 'Temperature', # 945 results

        # all lesion measurements
        # 'Lesion',      # 2425 results

        # all instances of a temp measurement AND a lesion measurement
        # 'Temperature AND Lesion', # 17 results

        # all instances of the given symptoms
        # 'hasTachycardia', # 1996 results
        # 'hasRigors',      # 683 results
        # 'hasShock',       # 2117 results
        # 'hasDyspnea',     # 3277 results
        # 'hasNausea',      # 2261 results
        # 'hasVomiting',    # 2303 results

        # all instances of a temp measurement and another symptom
        # 'Temperature AND hasTachycardia', # 55 results
        # 'Temperature AND hasRigors',      # 11 results
        # 'Temperature AND hasShock',       # 50 results
        # 'Temperature AND hasDyspnea',     # 64 results
        # 'Temperature AND hasNausea',      # 91 results
        # 'Temperature AND hasVomiting',    # 74 results

        # all instances of a lesion measurement and another symptom
        # 'Lesion AND hasTachycardia', # 131 results
        # 'Lesion AND hasRigors',      # 50 results
        # 'Lesion AND hasShock',       # 43 results
        # 'Lesion AND hasDyspnea',     # 103 results
        # 'Lesion AND hasNausea',      # 136 results
        # 'Lesion AND hasVomiting',    # 150 results
        
        # # pure math expressions
        # 'Temperature.value >= 100.4',    # 488 results
        # 'Temperature.value >= 1.004e2',  # 488 results
        # '100.4 <= Temperature.value',    # 488 results
        # '(Temperature.value >= 100.4)',  # 488 results
        # 'Temperature.value == 100.4',    # 14 results
        # 'Temperature.value + 3 ^ 2 < 109',      # temp < 100,     374 results
        # 'Temperature.value ^ 3 + 2 < 941194',   # temp < 98,      118 results
        # 'Temperature.value % 3 ^ 2 == 2',       # temp == 101,    68 results
        # 'Temperature.value * 4 ^ 2 >= 1616',    # temp >= 101,    417 results
        # 'Temperature.value / 98.6 ^ 2 < 0.01',  # temp < 97.2196, 66 results
        # '(Temperature.value / 98.6)^2 < 1.02',  # temp < 99.581,  325 results
        # '0 == Temperature.value % 20',          # temp == 100,    40 results
        # '(Lesion.dimension_X <= 5) OR (Lesion.dimension_X >= 45)',           # 746 results
        # 'Lesion.dimension_X > 15 AND Lesion.dimension_X < 30',               # 528 results
        # '((Lesion.dimension_X) > (15)) AND (((Lesion.dimension_X) < (30)))', # 528 results

        # math involving multiple NLPQL features
        # 'Lesion.dimension_X > 15 AND Lesion.dimension_X < 30 OR (Temperature.value >= 100.4)', # 1016 results
        # '(Lesion.dimension_X > 15 AND Lesion.dimension_X < 30) AND Temperature.value > 100.4', # 2 results
        # 'Lesion.dimension_X > 15 AND Lesion.dimension_X < 30 AND Temperature.value > 100.4', # 2 results
        
        # 'hasTachycardia AND hasShock',                  # 191 results
        # 'hasTachycardia OR hasShock',                   # 4113 results
        # 'hasTachycardia NOT hasShock',                  # 1891 results
        # '(hasTachycardia AND hasDyspnea) NOT hasRigors' # 229 results
        # 'hasTachycardia AND hasDyspnea',                # 240 results
        # '((hasShock) AND (hasDyspnea))',                # 155 results
        # '((hasTachycardia) AND (hasRigors OR hasDyspnea OR hasNausea))', # 546 results
        # '((hasTachycardia)AND(hasRigorsORhasDyspneaORhasNausea))',       # 546 results
        # 'hasTachycardia NOT (hasRigors OR hasDyspnea)',   # 1800 results
        # 'hasTachycardia NOT (hasRigors OR hasDyspnea OR hasNausea)',     # 1702 results
        # 'hasTachycardia NOT (hasRigors OR hasDyspnea OR hasNausea or hasVomiting)', # 1622 results
        # 'hasTachycardia NOT (hasRigors OR hasDyspnea OR hasNausea OR hasVomiting OR hasShock)', 1528 results
        # 'hasTachycardia NOT (hasRigors OR hasDyspnea OR hasNausea OR hasVomiting OR hasShock ' \
        # 'OR Temperature)', # 1491 results
        # 'hasTachycardia NOT (hasRigors OR hasDyspnea OR hasNausea OR hasVomiting OR hasShock ' \
        # 'OR Temperature OR Lesion)', # 1448 results

        # 'hasTachycardia NOT (hasRigors AND hasDyspnea)',  # 1987 results
        # 'hasRigors AND hasTachycardia AND hasDyspnea',    # 11 results
        # 'hasRigors AND hasDyspnea AND hasTachycardia',    # 11 results
        # 'hasRigors OR hasTachycardia AND hasDyspnea',     # 923 results
        # '(hasRigors OR hasDyspnea) AND hasTachycardia',   # 340 results
        # 'hasRigors AND (hasTachycardia AND hasNausea)',   # 22 results
        # '(hasShock OR hasDyspnea) AND (hasTachycardia OR hasNausea)', # 743 results
        # '(hasShock OR hasDyspnea) NOT (hasTachycardia OR hasNausea)', 
        
        # 'Temperature AND (hasDyspnea OR hasTachycardia)',  # 106 results
        # 'Lesion AND (hasDyspnea OR hasTachycardia)',       # 234 results

        # mixed math and logic 
        # 'hasNausea AND Temperature.value >= 100.4', # 73 results
        # 'Lesion.dimension < 10 OR hasRigors',       # 683 results
        # '(hasRigors OR hasTachycardia OR hasNausea OR hasVomiting or hasShock) AND ' \
        # '(Temperature.value >= 100.4)', # 180 results
        # 'Lesion.dimension_X > 10 AND Lesion.dimension_X < 30 OR (hasRigors OR hasTachycardia AND hasDyspnea)',
        # 'Lesion.dimension_X > 10 OR Lesion.dimension_X < 30 OR hasRigors OR hasTachycardia OR hasDyspnea',
        # 'hasRigors AND hasTachycardia AND hasNausea',
        
        # 'Temperature AND hasDyspnea AND hasNausea AND hasVomiting', # 22 results
        # '(Temperature.value > 100.4) AND hasDyspnea AND hasNausea AND hasVomiting', # 20 results
        # 'Temperature.value >= 100.4 OR hasRigors OR hasTachycardia OR hasDyspnea OR hasNausea',
        # 'hasRigors OR (hasTachycardia AND hasDyspnea) AND Temperature.value >= 100.4',
        # 'hasRigors OR hasTachycardia OR hasDyspnea OR hasNausea AND Temperature.value >= 100.4',
        # 'Lesion.dimension_X < 10 OR hasRigors AND Lesion.dimension_X > 30',
        # 'Lesion.dimension_X > 12 AND Lesion.dimension_X > 20 AND Lesion.dimension_X > 35 ' \
        # 'OR hasNausea and hasDyspnea',
        # 'Lesion.dimension_X > 12 AND Lesion.dimension_X > 15 OR ' \
        # 'Lesion.dimension_X < 25 AND Lesion.dimension_X < 32 OR hasNausea and hasDyspnea',
        # 'Lesion.dimension_X > 12 AND Lesion.dimension_X > 15 OR '   \
        # 'Lesion.dimension_X < 25 AND Lesion.dimension_X < 32 AND hasNausea OR hasDyspnea',

        #  of this group of four, the final two expressions are identical
        # '(hasRigors OR hasDyspnea OR hasTachycardia) AND Temperature', # 117 results, 25 groups
        # '(hasRigors OR hasDyspnea OR hasTachycardia) AND (Temperature.value >= 100.4)', # 82 results, 20 groups
        # '(hasRigors OR hasDyspnea OR hasTachycardia) AND (Temperature.value < 100.4)',  # 53 results, 10 groups
        # '(hasRigors OR hasDyspnea OR hasTachycardia) NOT (Temperature.value >= 100.4)', # 53 results, 10 groups

        # '(hasRigors OR hasDyspnea) AND Temperature', # 75 results, 14 groups
        # '(hasRigors OR hasDyspnea) AND (Temperature.value >= 99.5 AND Temperature.value <= 101.5)', # 34d, 7g
        '(hasRigors OR hasDyspnea) NOT (Temperature.value < 99.5 OR Temperature.value > 101.5)',

        # need to do this:
        # '(hasRigors OR hasDyspnea) AND Lesion'
        # '(hasRigors OR hasDyspnea) AND (Lesion.dimension_X >= 10 AND Lesion.dimension_Y < 10)'
        # '(hasRigors OR hasDyspnea) NOT (Lesion.dimension_X < 10 OR Lesion.dimension_Y > 10)'

        # then with (Lesion.dimension_X >= 10 AND Temperature.value < 100.4) as the math part
        
        # dimension_X and dimension_Y
        # 'Temperature.value >= 100.4 OR hasRigors AND hasDyspnea OR ' \
        # 'Lesion.dimension_X > 10 OR Lesion.dimension_Y < 30',

        # # error
        #'This is junk and should cause a parser exception',

        # expansion theorem: p(a OR b OR c) = (a) OR (b) OR (c) NOT
        #                                     ( (a AND b) OR (a AND c) OR (b AND c) ) OR
        #                                     (a AND b AND c)

        # # #### not legal, since each math expression must produce a Boolean result:
        # # # '(Temp.value/98.6) * (HR.value/60.0) * (BP.systolic/110) < 1.1',

    ]

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
        expr_eval.enable_debug()
        _TRACE = True

    # get all defined names, helps resolve tokens if bad expression formatting
    the_name_list = NAME_LIST
    if name_list is not None:
        the_name_list = name_list

    if command_line_expression is None:
        expressions = EXPRESSIONS
    else:
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

        banner_print(e)
        for expr_obj, output_docs in results:
            print()
            print('Subexpression text: {0}'.format(expr_obj.expr_text))
            print('Subexpression type: {0}'.format(expr_obj.expr_type))
            print('      Result count: {0}'.format(len(output_docs)))
            print('     NLPQL feature: {0}'.format(expr_obj.nlpql_feature))
            print('Results: ')

            n = len(output_docs)
            if 0 == n:
                print('\tNone.')
                continue

            if expr_eval.EXPR_TYPE_MATH == expr_obj.expr_type:
                for k in range(n):
                    if k < num or k > n-num:
                        doc = output_docs[k]
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
                        print('[{0:6}]: Document {1}, NLPQL feature {2}:'.
                              format(k, str(doc['_id']),
                                     expr_obj.nlpql_feature))

                        if is_final:
                            print(doc)
                        else:
                            history = doc[HISTORY_FIELD]
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

                                print('\t_id: {0} operation: {1:20} '  \
                                      'nlpql_feature: {2:16} {3} ' \
                                      'data: {4} '.
                                      format(tup.oid, tup.pipeline_type,
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
    str_context_statement = r'context\s(?P<context>[^;]+);'
    regex_context_statement = re.compile(str_context_statement)

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
        print('\t  context:  {0}'.format(file_data.context))
        print('\ttask_names: {0}'.format(file_data.tasks))
        print('\t     names: {0}'.format(file_data.names))
        print('\tprimitives: {0}'.format(file_data.primitives))
        print('\texpressions: ')
        for i in range(len(file_data.expressions)):
            expr_name, expr_def = file_data.expressions[i]
            expr_name, expr_reduced = file_data.reduced_expressions[i]
            print('{0}'.format(expr_name))
            print('\toriginal: {0}'.format(expr_def))
            print('\t reduced: {0}'.format(expr_reduced))

    sys.exit(0)
    return file_data
        

###############################################################################
def _get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
def _show_help():
    print(_get_version())
    print("""
    USAGE: python3 ./{0} --jobid <integer> [-cdhvmpnef]

    OPTIONS:

        -j, --jobid    <integer>   job_id of data in MongoDB
        -c, --context  <string>    either 'patient' or 'document'
                                   (default is patient)
        -m, --mongohost            IP address of remote MongoDB host
                                   (default is localhost)
        -p, --port                 port number for remote MongoDB host
                                   (default is 27017)

        -n, --num                  Number of results to display at start and
                                   end of results array (the number of results
                                   displayed is 2 * n). Default is n == 16.

        -f, --file                 NLPQL file to process. Must contain only 
                                   define statements. If this option is present
                                   the -e option cannot be used.

        -e, --expr                 NLPQL expression to evaluate.
                                   (default is to use a test expression from this file)
                                   If this option is present the -f option
                                   cannot be used.
    FLAGS:

        -h, --help           Print this information and exit.
        -d, --debug          Enable debug output.
        -v, --version        Print version information and exit.
        -i, --isfinal        Generate NLPQL 'final' result. Default is to
                             generate an 'intermediate' result.

    """.format(_MODULE_NAME))


###############################################################################
if __name__ == '__main__':

    optparser = optparse.OptionParser(add_help_option=False)
    optparser.add_option('-c', '--context', action='store', dest='context')
    optparser.add_option('-j', '--jobid', action='store', dest='job_id')
    optparser.add_option('-d', '--debug', action='store_true',
                         dest='debug', default=False)
    optparser.add_option('-v', '--version',
                         action='store_true', dest='get_version')
    optparser.add_option('-h', '--help',
                         action='store_true', dest='show_help', default=False)
    optparser.add_option('-i', '--isfinal',
                         action='store_true', dest='isfinal', default=False)
    optparser.add_option('-m', '--mongohost', action='store', dest='mongohost')
    optparser.add_option('-p', '--port', action='store', dest='port')
    optparser.add_option('-n', '--num', action='store', dest='num')
    optparser.add_option('-e', '--expr', action='store', dest='expr')
    optparser.add_option('-f', '--file', action='store', dest='filepath')

    opts, other = optparser.parse_args(sys.argv)

    if opts.show_help or 1 == len(sys.argv):
        _show_help()
        sys.exit(0)

    if opts.get_version:
        print(_get_version())
        sys.exit(0)

    debug = False
    if opts.debug:
        debug = True
        _enable_debug()

    if opts.job_id is None:
        print('The job_id (-j command line option) must be provided.')
        sys.exit(-1)
    job_id = int(opts.job_id)

    mongohost = 'localhost'
    if opts.mongohost is not None:
        mongohost = opts.mongohost

    port = 27017
    if opts.port is not None:
        port = int(opts.port)

    is_final = opts.isfinal

    context = 'patient'
    if opts.context is not None:
        context = opts.context

    num = 16
    if opts.num is not None:
        num = int(opts.num)

    expr = None
    if opts.expr is not None:
        if opts.filepath is not None:
            print('Options -e and -f are mutually exclusive.')
            sys.exit(-1)
        else:
            expr = opts.expr

    filepath = None
    name_list = None
    if opts.filepath is not None:
        if opts.expr is not None:
            print('Options -e and -f are mutually exclusive.')
            sys.exit(-1)
        else:
            filepath = opts.filepath
            if not os.path.exists(filepath):
                print('File not found: "{0}"'.format(filepath))
                sys.exit(-1)
            file_data = _parse_file(filepath)
            name_list = file_data.names

    # connect to ClarityNLP mongo collection nlp.phenotype_results
    mongo_client_obj = MongoClient(mongohost, port)
    mongo_db_obj = mongo_client_obj['nlp']
    mongo_collection_obj = mongo_db_obj['phenotype_results']

    # delete any data computed from NLPQL expressions, will recompute
    # the task data is preserved
    if filepath is not None:
        for nlpql_feature, expression in file_data.expressions:

            result = mongo_collection_obj.delete_many({"job_id":job_id,
                                                       "nlpql_feature":nlpql_feature})
            print('Removed {0} docs with NLPQL feature {1}.'.
                  format(result.deleted_count, nlpql_feature))

    if filepath is None:
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
            
