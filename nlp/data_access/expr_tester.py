#!/usr/bin/env python3
"""
This is a program for testing the ClarityNLP NLPQL expression evaluator.

It assumes that a run of the NLPQL file 'data_gen.nlpql' has already been
performed. You will need to know the job_id from that run to use this code.

"""

import re
import os
import sys
import copy
import string
import optparse
import datetime
from pymongo import MongoClient
from collections import namedtuple

import expr_eval

_VERSION_MAJOR = 0
_VERSION_MINOR = 1
_MODULE_NAME   = 'expr_tester.py'

TEST_ID            = 'EXPR_TEST'
TEST_NLPQL_FEATURE = 'EXPR_TEST'


###############################################################################
def flatten(l, ltypes=(list, tuple)):
    """
    Non-recursive list and tuple flattener from
    http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html,
    based on code from Mike Fletcher's BasicTypes library.
    """
    
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
        
    return ltype(l)


###############################################################################
def flatten_nested_lists(obj):
    """
    Remove nested lists in the given dict and return the flattened 
    equivalent. Does some special handling for empty lists or lists containing
    all identical entries, mainly to simplify the results when viewed in Excel.
    """

    for k,v in obj.items():
        if type(v) == list:
            if 1 == len(v) and '' == v[0]:
                obj[k] = None
            else:
                flattened_list = flatten(v)

                all_none = True
                for item in flattened_list:
                    if item is not None:
                        all_none = False
                        break

                if all_none:
                    obj[k] = None
                else:
                    obj[k] = flattened_list

                    
###############################################################################
def remove_arrays(obj):
    """
    Remove arrays in the result dict by creating numbered fields for
    the array elements.
    """
    to_insert = []
    to_remove = []
    
    for k,v in obj.items():
        if type(v) != list:
            continue

        elt_count = len(v)
        if 1 == elt_count:
            obj[k] = v[0]
        else:
            for i in range(elt_count):
                # use 1-based indexing
                field_name = '{0}_{1}'.format(k, i+1)
                to_insert.append( (field_name, copy.deepcopy(v), i) )
            to_remove.append(k)

    for k in to_remove:
        obj.pop(k, None)
    for k,v,i in to_insert:
        obj[k] = v[i]


###############################################################################
def evaluate_expressions(expr_obj_list,
                         mongo_collection_obj,
                         job_id,
                         context_field,
                         debug=False):
    """
    Nearly identical to
    nlp/luigi_tools/phenotype_helper.mongo_process_operations
    """

    print('process_expressions expr_object_list: ')
    for expr_obj in expr_obj_list:
        print(expr_obj)

    phenotype_id    = TEST_ID
    phenotype_owner = TEST_ID
    is_final        = False
        
    assert 'subject' == context_field or 'report_id' == context_field

    # these fields are not copied from source doc to result doc
    NO_COPY_FIELDS = [
        '_id', 'job_id', 'phenotype_id', 'owner',
        'job_date', 'context_type', 'raw_definition_text',
        'nlpql_feature', 'phenotype_final', 'history'
    ]

    for expr_obj in expr_obj_list:

        # evaluate the (sub)expression in expr_obj
        result = expr_eval.evaluate_expression(expr_obj,
                                               job_id,
                                               context_field,
                                               mongo_collection_obj,
                                               debug)
            
        # query MongoDB to get result docs
        cursor = mongo_collection_obj.find({'_id': {'$in': result.doc_ids}})

        # generate output docs
        output_docs = []

        if expr_eval.EXPR_TYPE_MATH == result.expr_type:

            expression = expr_obj.expr_text
            
            # no document groups for math results
            for doc in cursor:

                # output doc
                ret = {}
                
                # add doc fields to the output doc as lists
                field_map = {}
                fields = doc.keys()
                fields_to_copy = [f for f in fields if f not in NO_COPY_FIELDS]
                for f in fields_to_copy:
                    if f not in field_map:
                        field_map[f] = [doc[f]]
                    else:
                        field_map[f].append(doc[f])

                for k,v in field_map.items():
                    ret[k] = copy.deepcopy(v)

                # set the context field explicitly
                ret[context_field] = doc[context_field]

                # store the expression text explicitly
                # ret['nlpql_expr'] = expr_obj.expr_text
                
                ret['job_id'] = job_id
                ret['phenotype_id'] = phenotype_id
                ret['owner'] = phenotype_owner
                ret['job_date'] = datetime.datetime.now()
                ret['context_type'] = context_field
                ret['raw_definition_text'] = result.expr_text
                ret['nlpql_feature'] = result.nlpql_feature
                ret['phenotype_final'] = is_final

                # add source _id and nlpql_feature
                if is_final:
                    ret['_ids_1'] = copy.deepcopy(doc['_id'])
                    ret['nlpql_features_1'] = copy.deepcopy(doc['nlpql_feature'])
                else:
                    # use same field names as for logic ops
                    ret['_ids'] = copy.deepcopy(doc['_id'])
                    ret['nlpql_features'] = copy.deepcopy(doc['nlpql_feature'])

                flatten_nested_lists(ret)

                if is_final:
                    remove_arrays(ret)

                output_docs.append(ret)

            if len(output_docs) > 0:
                mongo_collection_obj.insert_many(output_docs)
            else:
                print('mongo_process_operations (math): No phenotype matches on %s.' % expression)

        else:

            assert expr_eval.EXPR_TYPE_LOGIC == result.expr_type

            expression = expr_obj.expr_text
            
            doc_map, oid_list_of_lists = expr_eval.expand_logical_result(result,
                                                                         mongo_collection_obj)

            # an 'ntuple' is a list of _id values
            for ntuples in oid_list_of_lists:
                for ntuple in ntuples:
                    assert isinstance(ntuple, list)
                    if 0 == len(ntuple):
                        continue

                    # each ntuple supplies the data for a result doc
                    ret = {}
                    history = {
                        'source_ids'  : [],
                        'source_features' : []
                    }

                    # get the shared context field value for this ntuple
                    oid = ntuple[0]
                    doc = doc_map[oid]
                    context_field_value = doc[context_field]
                    
                    # accumulate the source _id and nlpql_feature fields
                    for oid in ntuple:
                        # get the doc associated with this _id
                        doc = doc_map[oid]
                        history['source_ids'].append(str(oid))
                        history['source_features'].append(doc['nlpql_feature'])
                        assert context_field_value == doc[context_field]
                        
                    # add ntuple doc fields to the output doc as lists
                    field_map = {}
                    for oid in ntuple:
                        doc = doc_map[oid]
                        fields = doc.keys()
                        fields_to_copy = [f for f in fields if f not in NO_COPY_FIELDS]
                        for f in fields_to_copy:
                            if f not in field_map:
                                field_map[f] = [doc[f]]
                            else:
                                field_map[f].append(doc[f])

                    for k,v in field_map.items():
                        ret[k] = copy.deepcopy(v)

                    # set the context field value; same value for all ntuple entries
                    ret[context_field] = context_field_value

                    # store the expression text explicitly
                    # ret['nlpql_expr'] = expr_obj.expr_text
                    
                    # update fields common to AND/OR
                    ret['job_id'] = job_id
                    ret['phenotype_id'] = phenotype_id
                    ret['owner'] = phenotype_owner
                    ret['job_date'] = datetime.datetime.now()
                    ret['context_type'] = context_field
                    ret['raw_definition_text'] = result.expr_text
                    ret['nlpql_feature'] = result.nlpql_feature
                    ret['phenotype_final'] = is_final

                    # add source _ids and nlpql_features (1-based indexing)
                    source_count = len(history['source_ids'])
                    if is_final:
                        for i in range(len(history['source_ids'])):
                            field_name = '_ids_{0}'.format(i+1)
                            ret[field_name] = history['source_ids'][i]
                        for i in range(len(history['source_features'])):
                            field_name = 'nlpql_features_{0}'.format(i+1)
                            ret[field_name] = history['source_features'][i]

                        # remove intermediate array fields
                        ret.pop('_ids', None)
                        ret.pop('nlpql_features', None)
                    else:
                        # add intermediate array fields
                        ret['_ids'] = copy.deepcopy(history['source_ids'])
                        ret['nlpql_features'] = copy.deepcopy(history['source_features'])

                    flatten_nested_lists(ret)

                    if is_final:
                        remove_arrays(ret)

                    output_docs.append(ret)

            if len(output_docs) > 0:
                mongo_collection_obj.insert_many(output_docs)
            else:
                print('mongo_process_operations (logic): no phenotype matches on {0}.'.
                      format(expression))
                    

###############################################################################
def _delete_prev_results(job_id, mongo_collection_obj):
    """
    Remove all docs generated by this module.
    """

    # delete all assigned results from a previous run of this code
    result = mongo_collection_obj.delete_many({"job_id":job_id,
                                               "nlpql_feature":TEST_NLPQL_FEATURE})
    print('Removed {0} result docs from a previous run.'.
          format(result.deleted_count))

    # delete all temp results from a previous run of this code
    result = mongo_collection_obj.delete_many({"nlpql_feature":expr_eval.regex_temp_nlpql_feature})
    print('Removed {0} docs with temp NLPQL features from a previous run.'.
          format(result.deleted_count))
    
                
###############################################################################
def _run_tests(job_id, context_var, mongohost, port, debug=False):
    """
    Include all NLPQL names from data_gen.nlpql in the following list.
    """

    NAME_LIST = [
        'hasRigors', 'hasDyspnea', 'hasNausea', 'hasVomiting', 'hasShock',
        'hasTachycardia', 'hasLesion', 'Temperature', 'Lesion',
        'hasFever', 'hasSepsisSymptoms', 'hasSepsis',
        'hasLesionAndSepsisSymptoms', 'hasLesionAndTemperature',
        'hasAllThree'
    ]

    EXPRESSIONS = [

        # # pure math expressions
        'Temperature.value >= 100.4',
        # 'Temperature.value >= 1.004e2',
        # '100.4 <= Temperature.value',
        # '(Temperature.value >= 100.4)',
        # 'Temperature.value == 100.4', # 28 results
        # 'Temperature.value + 3 ^ 2 < 109',      # temp < 100, 659 results
        # 'Temperature.value ^ 3 + 2 < 941194',   # temp < 98, 218 results
        # 'Temperature.value % 3 ^ 2 == 2',       # temp == 101, 169 results
        # 'Temperature.value * 4 ^ 2 >= 1616',    # temp >= 101, 1128 results
        # 'Temperature.value / 98.6 ^ 2 < 0.01',  # temp < 97.2196, 114 results
        # '(Temperature.value / 98.6)^2 < 1.02',  # temp < 99.581, 590 results
        # '0 == Temperature.value % 20',          # temp == 100, 145 results
        # '(Lesion.dimension_X <= 5) OR (Lesion.dimension_X >= 45)',
        # 'Lesion.dimension_X > 15 AND Lesion.dimension_X < 30',             # 1174 results
        # '((Lesion.dimension_X) > (15)) AND (((Lesion.dimension_X) < (30)))', # 1174 results

        # # math involving multiple NLPQL features
        # 'Lesion.dimension_X > 15 AND Lesion.dimension_X < 30 OR (Temperature.value >= 100.4)',
        # '(Lesion.dimension_X > 15 AND Lesion.dimension_X < 30) OR (Temperature.value >= 100.4)',
        # 'Lesion.dimension_X > 15 AND Lesion.dimension_X < 30 AND Temperature.value > 100.4',
        # # #### not legal, since each math expression must produce a Boolean result:
        # # # '(Temp.value/98.6) * (HR.value/60.0) * (BP.systolic/110) < 1.1',

        # # pure logic expressions
        # 'hasTachycardia',
        # 'hasTachycardia AND hasShock', # subjects 14894, 20417
        # 'hasTachycardia OR hasShock',
        # 'hasTachycardia AND hasDyspnea', # subjects 22059, 24996, 
        # '((hasShock) AND (hasDyspnea))',
        # '((hasTachycardia) AND (hasRigors OR hasDyspnea OR hasNausea))', # 313
        # '((hasTachycardia)AND(hasRigorsORhasDyspneaORhasNausea))',
        # 'hasRigors AND hasTachycardia AND hasDyspnea', # 13732, 16182, 24799, 5701
        # 'hasRigors OR hasTachycardia AND hasDyspnea', # 2662
        # 'hasRigors AND hasDyspnea AND hasTachycardia', # 13732, 16182, 24799, 7480, 5701,
        # '(hasRigors OR hasDyspnea) AND hasTachycardia', #286
        # 'hasRigors AND (hasTachycardia AND hasNausea)',
        # '(hasShock OR hasDyspnea) AND (hasTachycardia OR hasNausea)',
        # 'hasFever AND (hasDyspnea OR hasTachycardia)',

        # # logical NOT is TBD; requires NLPQL feature dependencies
        # # 'hasRigors NOT hasNausea',
        # # 'hasRigors NOT (hasNausea OR hasTachycardia)',
        # # 'hasSepsis NOT hasRigors' # how to do this properly

        # mixed math and logic (cannot fully evaluate with this test code)
        # 'hasNausea AND Temperature.value >= 100.4',
        # '(hasRigors OR hasTachycardia OR hasNausea OR hasVomiting or hasShock) AND (Temperature.value >= 100.4)',
        # 'Lesion.dimension_X > 10 AND Lesion.dimension_X < 30 AND (hasRigors OR hasTachycardia or hasDyspnea)',
        # 'Lesion.dimension_X > 10 OR Lesion.dimension_X < 30 OR hasRigors OR hasTachycardia or hasDyspnea',
        # '((Temperature.value >= 100.4) AND (hasRigors AND hasTachycardia AND hasNausea))',
        # 'Temperature.value >= 100.4 OR hasRigors OR hasTachycardia OR hasDyspnea OR hasNausea',
        # 'hasRigors AND hasTachycardia AND hasDyspnea AND hasNausea AND Temperature.value >= 100.4',
        # 'hasRigors OR (hasTachycardia AND hasDyspnea) AND Temperature.value >= 100.4',
        # 'hasRigors OR hasTachycardia OR hasDyspnea OR hasNausea AND Temperature.value >= 100.4',
        # 'Lesion.dimension_X < 10 OR hasRigors AND Lesion.dimension_X > 30',
        # 'Lesion.dimension_X > 12 AND Lesion.dimension_X > 20 AND Lesion.dimension_X > 35 OR hasNausea and hasDyspnea',
        # 'M.x > 12 AND M.x > 15 OR M.x < 25 AND M.x < 32 OR hasNausea and hasDyspnea',
        # 'M.x > 12 AND M.x > 15 OR M.x < 25 AND M.x < 32 AND hasNausea OR hasDyspnea',

        # problem (dimension_X and dimension_Y)
        # 'Temperature.value >= 100.4 OR hasRigors AND hasDyspnea OR Lesion.dimension_X > 10 OR Lesion.dimension_Y < 30',

        # # error
        #'This is junk and should cause a parser exception',
    ]

    # connect to ClarityNLP mongo collection nlp.phenotype_results
    mongo_client_obj = MongoClient(mongohost, port)
    mongo_db_obj = mongo_client_obj['nlp']
    mongo_collection_obj = mongo_db_obj['phenotype_results']
    
    final_nlpql_feature = TEST_NLPQL_FEATURE

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
        
    counter = 1
    for e in EXPRESSIONS:
        print('[{0:3}]: "{1}"'.format(counter, e))

        parse_result = expr_eval.parse_expression(e, NAME_LIST)
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
        evaluate_expressions(expression_object_list,
                             mongo_collection_obj,
                             job_id,
                             context_field,
                             debug)

        print('[{0:3}]: "{1}"'.format(counter, e))
        for eo in expression_object_list:
            print('\t{0}'.format(eo))
        
        counter += 1
        print()

    return True


###############################################################################
def _get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
def _show_help():
    print(_get_version())
    print("""
    USAGE: python3 ./{0} --jobid <integer> [-cdhvmp]

    OPTIONS:

        -j, --jobid    <integer>   job_id of data in MongoDB
        -c, --context  <string>    either 'patient' or 'document'
                                   (default is patient)
        -m, --mongohost            IP address of remote MongoDB host
        -p, --port                 port number for remote MongoDB host

    FLAGS:

        -h, --help           Print this information and exit.
        -d, --debug          Enable debug output.
        -v, --version        Print version information and exit.

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
    optparser.add_option('-m', '--mongohost', action='store', dest='mongohost')
    optparser.add_option('-p', '--port', action='store', dest='port')

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

    if opts.job_id is None:
        print('The job_id (-j command line option) must be provided.')
        sys.exit(-1)

    mongohost = 'localhost'
    if opts.mongohost is not None:
        mongohost = opts.mongohost

    port = 27017
    if opts.port is not None:
        port = int(opts.port)
        
    job_id = int(opts.job_id)

    context = 'patient'
    if opts.context is not None:
        context = opts.context
        
    _run_tests(job_id, context, mongohost, port, debug)

