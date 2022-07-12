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
def _validate_race_results(results):

    FIELDS = ['value', 'value_normalized']

    if 1 != len(results):
        return False

    for result in results:
    
        if not _fields_exist(FIELDS, result):
            return False

        v = result['value']
        vn = result['value_normalized']

        if v != 'caucasian' or vn != 'white':
            return False
        
    return True


###############################################################################
def _validate_measurement_results(results):

    FIELDS = ['dimension_X', 'dimension_Y', 'dimension_Z', 'condition', 'units']

    EXPECTED_VALUES = set(['13', '1400', '15', '17', '19', '21'])
    
    if 6 != len(results):
        return False
    
    for result in results:
    
        if not _fields_exist(FIELDS, result):
            return False

        x = result['dimension_X']
        y = result['dimension_Y']
        z = result['dimension_Z']
        condition = result['condition']
        units = result['units']

        if '13' == x:
            if _EQ != condition or _MM != units:
                return False
            if '13' in EXPECTED_VALUES:
                EXPECTED_VALUES.remove('13')
            else:
                return False
        elif '1400' == x:
            if _EQ != condition or _MM3 != units:
                return False
            if '1400' in EXPECTED_VALUES:
                EXPECTED_VALUES.remove('1400')
            else:
                return False
        elif '15' == x:
            if '16' != y or 'RANGE' != condition or _MM != units:
                return False
            if '15' in EXPECTED_VALUES:
                EXPECTED_VALUES.remove('15')
            else:
                return False
        elif '17' == x:
            if '18' != y or _EQ != condition or _MM != units:
                return False
            if '17' in EXPECTED_VALUES:
                EXPECTED_VALUES.remove('17')
            else:
                return False
        elif '19' == x:
            if '20' != y or _EQ != condition or _MM != units:
                return False
            if '19' in EXPECTED_VALUES:
                EXPECTED_VALUES.remove('19')
            else:
                return False
        elif '21' == x:
            if '22' != y or '23' != z or _EQ != condition or _MM != units:
                return False
            if '21' in EXPECTED_VALUES:
                EXPECTED_VALUES.remove('21')
            else:
                return False
        else:
            return False
        
    return True


###############################################################################
def _validate_provider_assertion_results(results):

    FIELDS = ['negation', 'term']

    if 1 != len(results):
        return False

    for result in results:
    
        if not _fields_exist(FIELDS, result):
            return False

        if 'Affirmed' != result['negation']:
            return False
        if 'fever' != result['term']:
            return False

    return True


###############################################################################
def _validate_term_proximity_results(results):

    FIELDS = ['word1', 'word2']

    EV0 = ('cancer', 'prostate')
    EV1 = ('prostate', 'gleason')
    EXPECTED_VALUES = set([EV0, EV1])

    if 2 != len(results):
        return False
    
    for result in results:
    
        if not _fields_exist(FIELDS, result):
            return False

        w1 = result['word1']
        w2 = result['word2']
        t = (w1, w2)
        
        if EV0 == t:
            if EV0 in EXPECTED_VALUES:
                EXPECTED_VALUES.remove(EV0)
            else:
                return False
        elif EV1 == t:
            if EV1 in EXPECTED_VALUES:
                EXPECTED_VALUES.remove(EV1)
            else:
                return False
        else:
            return False
        
    return True


###############################################################################
def _validate_ejection_fraction_results(results):

    FIELDS = ['text', 'value', 'condition']

    EXPECTED_VALUES = set(['40', '75'])

    if 2 != len(results):
        return False
    
    for result in results:
    
        if not _fields_exist(FIELDS, result):
            return False

        text  = result['text']
        value = result['value']
        condition = result['condition']

        if value == '40':
            if text != 'LVEF' and condition != 'LESS_THAN':
                return False
            if '40' in EXPECTED_VALUES:
                EXPECTED_VALUES.remove('40')
            else:
                return False
        elif value == '75':
            if text != 'ejection fraction' and condition != 'EQUAL':
                return False
            if '75' in EXPECTED_VALUES:
                EXPECTED_VALUES.remove('75')
            else:
                return False
        else:
            return False            
    
    return True


###############################################################################
def _validate_gleason_results(results):

    FIELDS = ['value', 'value_first', 'value_second']

    assert 1 == len(results)
    for result in results:
    
        if not _fields_exist(FIELDS, result):
            return False

        if result['value'] != '5':
            return False
        if result['value_first'] != '2':
            return False
        if result['value_second'] != '3':
            return False
        
    return True


###############################################################################
def _validate_tnm_results(results):

    # pT4bpN1bM0 (stage IIIC)
    
    FIELDS = ['t_prefix', 't_code', 't_suffixes',
              'n_prefix', 'n_code', 'n_suffixes',
                          'm_code',
              'stage_number', 'stage_letter']

    if 1 != len(results):
        return False
    
    for result in results:
    
        if not _fields_exist(FIELDS, result):
            return False

        if result['t_prefix'] != 'p':
            return False
        if result['t_code'] != '4':
            return False
        if result['t_suffixes'] != "['b']":
            return False
        if result['n_prefix'] != 'p':
            return False
        if result['n_code'] != '1':
            return False
        if result['n_suffixes'] != "['b']":
            return False
        if result['m_code'] != '0':
            return False
        if result['stage_number'] != '3':
            return False
        if result['stage_letter'] != 'c':
            return False

    return True


###############################################################################
def _validate_term_finder_results(results):

    # Only check that the expected terms were found. Context makes mistakes
    # with the negation for the simple example sentence used in this test.
    
    FIELDS = ['experiencer', 'negation', 'temporality', 'term']
    TERMS = set(['rales', 'wheezing', 'coughing', 'walking'])
    
    if 4 != len(results):
        return False

    terms_found = []
    for result in results:

        if not _fields_exist(FIELDS, result):
            return False

        term = result['term']
        if not term in TERMS:
            return False
        else:
            terms_found.append(term)

    return set(terms_found) == TERMS
    

###############################################################################
def _validate_ecog_results(results):

    FIELDS = ['criteria_type', 'score_0', 'score_1', 'score_2', 'score_3',
              'score_4', 'score_5', 'score_lo', 'score_hi']

    if 1 != len(results):
        return False

    result = results[0]

    if not _fields_exist(FIELDS, result):
        return False

    score_0 = result['score_0']
    score_1 = result['score_1']
    score_2 = result['score_2']
    score_3 = result['score_3']
    score_4 = result['score_4']
    score_5 = result['score_5']
    score_hi = result['score_hi']
    score_lo = result['score_lo']
    criteria_type = result['criteria_type']

    if 1 != int(score_0):
        return False
    if 1 != int(score_1):
        return False
    if 1 != int(score_2):
        return False
    if 0 != int(score_3):
        return False
    if 0 != int(score_4):
        return False
    if 0 != int(score_5):
        return False
    if 2 != int(score_hi):
        return False
    if 0 != int(score_lo):
        return False
    if 'Inclusion' != criteria_type:
        return false

    return True
    

###############################################################################
def _validate_o2_results(results):

    FIELDS = ['pao2_est', 'fio2_est', 'p_to_f_ratio_est', 'flow_rate',
              'device', 'condition', 'value', 'value2']
    
    if 1 != len(results):
        return False

    result = results[0]

    if not _fields_exist(FIELDS, result):
        return False

    pao2_est = int(result['pao2_est'])
    fio2_est = int(result['fio2_est'])
    p_to_f   = int(result['p_to_f_ratio_est'])
    flow_rate = int(result['flow_rate'])
    device = result['device']
    condition = result['condition']
    value = int(result['value'])
    value2 = int(result['value2'])

    if 62 != pao2_est:
        return False
    if 44 != fio2_est:
        return False
    if 141 != p_to_f:
        return False
    if 6 != flow_rate:
        return False
    if 'nc' != device:
        return False
    if 'RANGE' != condition:
        return False
    if 91 != value:
        return False
    if 92 != value2:
        return False

    return True


###############################################################################
def _validate_pregnancy_results(results):

    # date_conception and date_delivery are not checked, since they are
    # referenced from the date at which the pregnancy finder runs

    FIELDS = ['weeks_pregnant', 'weeks_remaining', 'trimester']

    if 1 != len(results):
        return False

    result = results[0]

    if not _fields_exist(FIELDS, result):
        return False

    weeks_pregnant = float(result['weeks_pregnant'])
    weeks_remaining = float(result['weeks_remaining'])
    trimester = int(result['trimester'])

    if 5.3 != weeks_pregnant:
        return False
    if 34.7 != weeks_remaining:
        return False
    if 1 != trimester:
        return False

    return True

    
###############################################################################
def _run(csv_file):
    """
    Load the csv file containing the intermediate phenotype validation results
    and check with what is expected.
    """

    tnm_results         = []
    gleason_results     = []
    ef_results          = []
    tp_results          = []
    pa_results          = []
    meas_results        = []
    race_results        = []
    term_finder_results = []
    ecog_results        = []
    o2_results          = []
    pregnancy_results   = []
    
    print('Validating results...')
    with open(csv_file, 'rt') as infile:
        dict_reader = csv.DictReader(infile)
        for result in dict_reader:

            nlpql_feature = result['nlpql_feature']
            
            if 'TNMCode' == nlpql_feature:
                tnm_results.append(result)
            elif 'GleasonScore' == nlpql_feature:
                gleason_results.append(result)
            elif 'EjectionFraction' == nlpql_feature:
                ef_results.append(result)
            elif 'hasProstateCancer' == nlpql_feature:
                tp_results.append(result)
            elif 'hasFever' == nlpql_feature:
                pa_results.append(result)
            elif 'Measurement' == nlpql_feature:
                meas_results.append(result)
            elif 'Race' == nlpql_feature:
                race_results.append(result)
            elif 'TermFinderResult' == nlpql_feature:
                term_finder_results.append(result)
            elif 'EcogStatusResult' == nlpql_feature:
                ecog_results.append(result)
            elif 'O2TaskResult' == nlpql_feature:
                o2_results.append(result)
            elif 'PregnancyTaskResult' == nlpql_feature:
                pregnancy_results.append(result)

    all_valid = True
    
    if not _validate_tnm_results(tnm_results):
        print('*** TNM results are invalid. ***')
        all_valid = False
    if not _validate_gleason_results(gleason_results):
        print('*** Gleason results are invalid. ***')
        all_valid = False
    if not _validate_ejection_fraction_results(ef_results):
        print('*** Ejection fraction results are invalid. ***')
        all_valid = False
    if not _validate_term_proximity_results(tp_results):
        print('*** Prostate cancer results are invalid. ***')
        all_valid = False
    if not _validate_provider_assertion_results(pa_results):
        print('*** Fever results are invalid. ***')
        all_valid = False
    if not _validate_measurement_results(meas_results):
        print('*** Measurement results are invalid. ***')
        all_valid = False
    if not _validate_race_results(race_results):
        print('*** Race results are invalid. ***')
        all_valid = False
    if not _validate_term_finder_results(term_finder_results):
        print('*** TermFinder results are invalid. ***')
        all_valid = False
    if not _validate_ecog_results(ecog_results):
        print('*** EcogStatus results are invalid. ***')
        all_valid = False
    if not _validate_o2_results(o2_results):
        print('*** O2SaturationTask results are invalid. ***')
        all_valid = False
    if not _validate_pregnancy_results(pregnancy_results):
        print('*** PregnancyTask results are invalid. ***')
        all_valid = False
        
    if all_valid:
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
