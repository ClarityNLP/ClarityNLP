#!/usr/bin/env python3
"""
Interactive test program for the cql_result_parser.
"""

import re
import os
import sys
import json
import argparse
import cql_result_parser as crp
from collections import namedtuple

_VERSION_MAJOR = 0
_VERSION_MINOR = 2
_MODULE_NAME   = 'cql_result_tester.py'

# set to True to enable debug output
_TRACE = True


###############################################################################
def _enable_debug():

    crp.enable_debug()


###############################################################################
def _get_maxlen(obj):

    return max([len(k) for k,v in obj.items()])
    
###############################################################################
def _print_results(obj, maxlen=None):

    if obj is None:
        return

    obj_type = type(obj)

    # find the max key length - do it once
    if maxlen is None:
        if dict == obj_type:
            maxlen = _get_maxlen(obj)
        elif list == obj_type:
            maxlen = 0
            for item in obj:
                l = _get_maxlen(item)
                if l > maxlen:
                    maxlen = l
    
    if dict == obj_type:
        for k,v in obj.items():
            # replace any embedded tabs and newlines with single space
            if str == type(v):
                v = re.sub(r'[\t\n]', ' ', v)
                v = re.sub(r'\s+', ' ', v)
            print('{0:>{1}}: {2}'.format(k, maxlen, v))
        print()
    elif list == obj_type:
        for item in obj:
            # recursive call
            _print_results(item, maxlen)
    else:
        print('cql_result_tester: Unexpected object type: {0}'.format(obj_type))
        print(obj)
        assert False

    
###############################################################################
def _run(json_obj):

    if _TRACE:
        print('Decoding JSON response from CQL engine...\n')
    
    KEY_RESULT_TYPE = 'resultType'

    # this code should mimic that in CQLExecutionTask::_json_to_objs
    
    results = []

    obj_count = len(json_obj)
    
    # assumes we either have a list of objects or a single obj
    obj_type = type(json_obj)

    if list == obj_type:
        if _TRACE:
            print('Found list of length {0}:'.format(obj_count))
        for e in json_obj:
            # skip if no resultType key
            if KEY_RESULT_TYPE not in e:
                continue
            if _TRACE:
                print('\tDecoding resource type {0}'.format(e['resultType']))
            result_obj = crp.decode_top_level_obj(e)
            if result_obj is None:
                continue
            if list is not type(result_obj):
                results.append(result_obj)
            else:
                results.extend(result_obj)
    elif dict == obj_type:
        if _TRACE:
            print('Found dict of size {0}'.format(obj_count))
        result_obj = crp.decode_top_level_obj(json_obj)
        if result_obj is not None:
            if list is not type(result_obj):
                results.append(result_obj)
            else:
                results.extend(result_obj)
    
    print('\ncql_result_tester: Fully decoded {0} of {1} objects.\n'.
          format(len(results), obj_count))

    _print_results(results)
        
        
###############################################################################
def _get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
def _show_help():
    print(_get_version())
    print("""
    USAGE: python3 ./{0} -f <json_file> [-hvd]

    REQUIRED:

        -f, --file          Json file containing FHIR result.

    FLAGS:

        -h, --help         Print this information and exit.
        -v, --version      Print version information and exit.
        -d, --debug        Print debug information.

    """.format(_MODULE_NAME))

###############################################################################
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Decode the CQL Engine JSON result file.'
    )

    parser.add_argument('-v', '--version',
                        action='store_true',
                        help='show the version string and exit')
    parser.add_argument('-f', '--file',
                        dest='filepath',
                        help='path to JSON file containing CQL Engine results')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='pint debug info to stdout')

    args = parser.parse_args()

    if 'version' in args and args.version:
        print(_get_version())
        sys.exit(0)
    
    if 'debug' in args and args.debug:
       _enable_debug()

    json_file = None
    if 'filepath' in args and args.filepath:
        json_file = args.filepath
        if not os.path.isfile(json_file):
            print("File not found: '{0}'".format(json_file))
            sys.exit(-1)
    else:
        print('Required "--file" argument not found.')
        sys.exit(-1)

    try:
        infile = open(json_file, 'rt')
        file_data = json.load(infile)
    except Exception as e:
        print("Could not load file contents{0}.".format(json_file))
        print(e)
        sys.exit(-1)

    infile.close()
    _run(file_data)
