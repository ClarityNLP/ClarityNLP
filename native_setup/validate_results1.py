"""
Use this program to check the ClarityNLP results using the data in data_validation1.{txt, json}
and the NLPQL file validation1.nlpql.

Assumes that the Mongo database is running on localhost.
"""

import re
import os
import csv
import sys
import argparse

_VERSION_MAJOR = 0
_VERSION_MINOR = 1
_MODULE_NAME   = 'validate_results.py'


###############################################################################
def _fields_exist(field_list, row_dict):

    for f in field_list:
        if f not in row_dict:
            return False
    return True


###############################################################################
def _validate_age_results(results):

    FIELDS = ['value']

    if 41 != len(results):
        return False

    # should have values of 20-60 inclusive
    expected_ages = set([i for i in range(20, 61)])

    for r in results:
        age = int(r['value'])
        if age in expected_ages:
            expected_ages.remove(age)

    # should have no items left
    return 0 == len(expected_ages)


###############################################################################
def _run(csv_file):
    """
    Load the csv file containing the intermediate phenotype validation results
    and check with what is expected.
    """

    age_results = []
    
    print('Validating results...')
    with open(csv_file, 'rt') as infile:
        dict_reader = csv.DictReader(infile)
        for result in dict_reader:

            nlpql_feature = result['nlpql_feature']

            if 'AgeResult' == nlpql_feature:
                age_results.append(result)

    all_valid = True

    if not _validate_age_results(age_results):
        print('*** Age results are invalid. ***')
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
        
