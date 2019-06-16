"""
Use this program to check the ClarityNLP validation results from a bare-bones
run. Assumes that the Mongo database is running on localhost.
"""

import re
import os
import csv
import sys
import argparse

_VERSION_MAJOR = 0
_VERSION_MINOR = 1
_MODULE_NAME   = 'validate_results.py'

_EQ = 'EQUAL'
_MM = 'MILLIMETERS'
_MM3 = 'CUBIC_MILLIMETERS'


###############################################################################
def _fields_exist(field_list, row_dict):

    for f in field_list:
        if f not in row_dict:
            return False
    return True


###############################################################################
def _race_is_valid(row_dict):

    FIELDS = ['value', 'value_normalized']
    if not _fields_exist(FIELDS, row_dict):
        return False

    v = row_dict['value']
    vn = row_dict['value_normalized']

    if v == 'caucasian' and vn == 'white':
        return True
    return False


###############################################################################
def _measurement_is_valid(row_dict):

    FIELDS = ['dimension_X', 'dimension_Y', 'dimension_Z', 'condition', 'units']
    if not _fields_exist(FIELDS, row_dict):
        return False

    x = row_dict['dimension_X']
    y = row_dict['dimension_Y']
    z = row_dict['dimension_Z']
    condition = row_dict['condition']
    units = row_dict['units']
    
    if '13' == x:
        if _EQ == condition and _MM == units:
            return True
    elif '1400' == x:
        if _EQ == condition and _MM3 == units:
            return True
    elif '15' == x:
        if '16' == y and 'RANGE' == condition and _MM == units:
            return True
    elif '17' == x:
        if '18' == y and _EQ == condition and _MM == units:
            return True
    elif '19' == x:
        if '20' == y and _EQ == condition and _MM == units:
            return True
    elif '21' == x:
        if '22' == y and '23' == z and _EQ == condition and _MM == units:
            return True
        
    return False


###############################################################################
def _provider_assertion_is_valid(row_dict):

    FIELDS = ['negation', 'term']
    if not _fields_exist(FIELDS, row_dict):
        return False

    if row_dict['negation'] != 'Affirmed':
        return False
    if row_dict['term'] != 'fever':
        return False
    return True


###############################################################################
def _term_proximity_is_valid(row_dict):

    FIELDS = ['word1', 'word2']
    if not _fields_exist(FIELDS, row_dict):
        return False

    w1 = row_dict['word1']
    w2 = row_dict['word2']

    if (w1 == 'cancer' and w2 == 'prostate') or (w1 == 'prostate' and w2 == 'gleason'):
        return True
    return False


###############################################################################
def _ejection_fraction_is_valid(row_dict):

    FIELDS = ['text', 'value', 'condition']
    if not _fields_exist(FIELDS, row_dict):
        return False

    text  = row_dict['text']
    value = row_dict['value']
    condition = row_dict['condition']
    
    if value == '40':
        if text != 'LVEF' and condition != 'LESS_THAN':
            return False
    elif value == '75':
        if text != 'ejection fraction' and condition != 'EQUAL':
            return False
    else:
        return False            
    
    return True


###############################################################################
def _gleason_is_valid(row_dict):

    FIELDS = ['value', 'value_first', 'value_second']
    if not _fields_exist(FIELDS, row_dict):
        return False

    if row_dict['value'] != '5':
        return False
    if row_dict['value_first'] != '2':
        return False
    if row_dict['value_second'] != '3':
        return False
    return True


###############################################################################
def _tnm_is_valid(row_dict):

    # pT4bpN1bM0 (stage IIIC)
    
    FIELDS = ['t_prefix', 't_code', 't_suffixes',
              'n_prefix', 'n_code', 'n_suffixes',
                          'm_code',
              'stage_number', 'stage_letter']

    if not _fields_exist(FIELDS, row_dict):
        return False

    if row_dict['t_prefix'] != 'p':
        return False
    if row_dict['t_code'] != '4':
        return False
    if row_dict['t_suffixes'] != "['b']":
        return False
    if row_dict['n_prefix'] != 'p':
        return False
    if row_dict['n_code'] != '1':
        return False
    if row_dict['n_suffixes'] != "['b']":
        return False
    if row_dict['m_code'] != '0':
        return False
    if row_dict['stage_number'] != '3':
        return False
    if row_dict['stage_letter'] != 'c':
        return False
    return True


###############################################################################
def _run(csv_file):
    """
    Load the csv file containing the intermediate phenotype validation results
    and check with what is expected.
    """

    print('Validating results...')
    with open(csv_file, 'rt') as infile:
        dict_reader = csv.DictReader(infile)

        ok = True
        for row_dict in dict_reader:
            nlpql_feature = row_dict['nlpql_feature']

            if 'TNMCode' == nlpql_feature:
                if not _tnm_is_valid(row_dict):
                    print('*** TNMCode is invalid ***')
                    ok = False
            elif 'GleasonScore' == nlpql_feature:
                if not _gleason_is_valid(row_dict):
                    print('*** GleasonScore is invalid ***')
                    ok = False
            elif 'EjectionFraction' == nlpql_feature:
                if not _ejection_fraction_is_valid(row_dict):
                    print('*** EjectionFraction is invalid ***')
                    ok = False
            elif 'hasProstateCancer' == nlpql_feature:
                if not _term_proximity_is_valid(row_dict):
                    print('*** TermProximity is invalid ***')
                    ok = False
            elif 'hasFever' == nlpql_feature:
                if not _provider_assertion_is_valid(row_dict):
                    print('*** ProviderAssertion is invalid ***')
                    ok = False
            elif 'Measurement' == nlpql_feature:
                if not _measurement_is_valid(row_dict):
                    print('*** Measurement is invalid ***')
                    ok = False
            elif 'Race' == nlpql_feature:
                if not _race_is_valid(row_dict):
                    print('*** Race is invalid ***')
                    ok = False

    if ok:
        print('All results are valid.')
                

###############################################################################
def _get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Check results from a ClarityNLP validation run.')
    parser.add_argument('-v', '--version', help='show version and exit',
                        action='store_true')
    parser.add_argument('-f', '--file',
                        help='path to intermediate results CSV file')

    args = parser.parse_args()

    if 'version' in args and args.version:
        print(_get_version())
        sys.exit(0)

    if 'file' in args and args.file is None:
        print('A --file argument must be specified')
        sys.exit(-1)
    csv_file = args.file

    if not os.path.exists(csv_file):
        print('File not found: "{0}"'.format(csv_file))
        sys.exit(-1)

    _run(csv_file)
