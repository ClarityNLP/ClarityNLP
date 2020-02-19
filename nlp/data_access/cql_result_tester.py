#!/usr/bin/env python3
"""
"""

import re
import os
import sys
import json
import optparse
import cql_result_parser as crp
from collections import namedtuple
from claritynlp_logging import log, ERROR, DEBUG

_VERSION_MAJOR = 0
_VERSION_MINOR = 1
_MODULE_NAME   = 'cibmtr_tester.py'


###############################################################################
def _enable_debug():

    crp.enable_debug()

        
###############################################################################
def _run(json_obj):

    results = []
    
    # assumes we either have a list of objects or a single obj
    obj_type = type(json_obj)
    if list == obj_type:
        #log('**** SAW A LIST ****')
        for e in json_obj:
            result_obj = crp.decode_top_level_obj(e)
            if result_obj is None:
                continue
            if list is not type(result_obj):
                results.append(result_obj)
            else:
                results.extend(result_obj)
    elif dict == obj_type:
        #log('**** SAW A DICT ****')
        result_obj = crp.decode_top_level_obj(json_obj)
        if result_obj is not None:
            if list is not type(result_obj):
                results.append(result_obj)
            else:
                results.extend(result_obj)

    #log('found {0} results'.format(len(results)))

    counter = 0
    for obj in results:
        log('Result {0}: {1}'.format(counter, obj))
        counter += 1
        
        
###############################################################################
def _get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
def _show_help():
    log(_get_version())
    log("""
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

    optparser = optparse.OptionParser(add_help_option=False)
    optparser.add_option('-f', '--file', action='store',
                         dest='filepath')
    optparser.add_option('-v', '--version', action='store_true',
                         dest='get_version')
    optparser.add_option('-d', '--debug', action='store_true',
                         dest='debug', default=False)
    optparser.add_option('-h', '--help', action='store_true',
                         dest='show_help', default=False)
    #optparser.add_option('-z', '--selftest', action='store_true',
    #                     dest='selftest', default=False)

    opts, other = optparser.parse_args(sys.argv)

    if 1 == len(sys.argv) or opts.show_help:
        _show_help()
        sys.exit(0)

    if opts.get_version:
        log(get_version())
        sys.exit(0)

    if opts.debug:
       _enable_debug()

    json_file = opts.filepath
    if not os.path.isfile(json_file):
        log("File not found: '{0}'".format(json_file))
        sys.exit(-1)

    try:
        infile = open(json_file, 'rt')
        file_data = json.load(infile)
    except Exception as e:
        log("Could not load file contents{0}.".format(json_file))
        log(e)
        sys.exit(-1)

    infile.close()

    #log(json.dumps(file_data, indent=4))
    _run(file_data)
