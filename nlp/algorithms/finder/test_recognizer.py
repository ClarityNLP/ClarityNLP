#!/usr/bin/python3
"""
    Test program for the recognizer modules.
"""

import re
import os
import sys
import json
import argparse
from collections import namedtuple

try:
    import lab_value_recognizer as lvr
except:
    from algorithms.finder import lab_value_recognizer as lvr
    
_VERSION_MAJOR = 0
_VERSION_MINOR = 1
_MODULE_NAME = 'test_recognizer.py'

_RESULT_FIELDS = ['match_text']
_Result = namedtuple('_Result', _RESULT_FIELDS)
_Result.__new__.__defaults__ = (None,) * len(_Result._fields)


###############################################################################
def _compare_results(
        computed_values,
        expected_values,
        sentence,
        field_list):

    # check that len(computed) == len(expected)
    if len(computed_values) != len(expected_values):
        print('\tMismatch in computed vs. expected results: ')
        print('\tSentence: {0}'.format(sentence))
        print('\tComputed: ')
        for v in computed_values:
            print('\t\t{0}'.format(v))
        print('\tExpected: ')
        for v in expected_values:
            print('\t\t{0}'.format(v))

        print('NAMEDTUPLE: ')
        for k,v in v._asdict().items():
            print('\t{0} => {1}'.format(k,v))

        return False

    # check fields for each result
    failures = []
    for i, t in enumerate(computed_values):
        # iterate over fields of current result
        for field, value in t._asdict().items():
            # remove trailing whitespace, if any, from computed value
            if str == type(value):
                value = value.strip()
            expected = expected_values[i]._asdict()
            # compare only those fields in _RESULT_FIELDS
            if field in field_list:
                if value != expected[field]:
                    # append as namedtuples
                    failures.append( (t, expected_values[i]) )

    if len(failures) > 0:
        print(sentence)
        for f in failures:
            # extract fields with values not equal to None
            c = [ (k,v) for k,v in f[0]._asdict().items()
                  if v is not None and k in field_list]
            e = [ (k,v) for k,v in f[1]._asdict().items() if v is not None]
            print('\tComputed: {0}'.format(c))
            print('\tExpected: {0}'.format(e))
            
        return False

    return True
    

###############################################################################
def _run_tests(test_data):

    for sentence, expected_values in test_data.items():

        # computed values are finder_overlap.Candidate namedtuples
        # relevant field is 'match_text'
        computed_values = lvr.run(sentence)
        
        ok = _compare_results(
            computed_values,
            expected_values,
            sentence,
            _RESULT_FIELDS)

        return ok


###############################################################################
def test_lab_value_recognizer():

    test_data = {
        'VS: T 95.6 HR 45 BP 75/30 RR 17 98% RA.':[
            _Result(match_text='T 95.6'),
            _Result(match_text='HR 45'),
            _Result(match_text='BP 75/30'),
            _Result(match_text='RR 17'),
            _Result(match_text='98% RA')
        ],
        'VS T97.3 P84 BP120/56 RR16 O2Sat98 2LNC':[
            _Result(match_text='T97.3'),
            _Result(match_text='P84'),
            _Result(match_text='BP120/56'),
            _Result(match_text='RR16'),
            _Result(match_text='O2Sat98 2LNC')
        ],
        'Height: (in) 74 Weight (lb): 199 BSA (m2): 2.17 m2 ' +\
        'BP (mm Hg): 140/91 HR (bpm): 53':[
            _Result(match_text='Height: (in) 74'),
            _Result(match_text='Weight (lb): 199'),
            _Result(match_text='BSA (m2): 2.17 m2'),
            _Result(match_text='BP (mm Hg): 140/91'),
            _Result(match_text='HR (bpm): 53')
        ],
        'Vitals: T: 99 BP: 115/68 P: 79 R:21 O2: 97':[
            _Result(match_text='T: 99'),
            _Result(match_text='BP: 115/68'),
            _Result(match_text='P: 79'),
            _Result(match_text='R:21'),
            _Result(match_text='O2: 97')
        ],
        'Vitals - T 95.5 BP 132/65 HR 78 RR 20 SpO2 98%/3L':[
            _Result(match_text='T: 95.5'),
            _Result(match_text='BP: 132/65'),
            _Result(match_text='P: 78'),
            _Result(match_text='R:20'),
            _Result(match_text='SpO2: 98%/3L')            
        ],
        'VS: T=98 BP= 122/58  HR= 7 RR= 20  O2 sat= 100% 2L NC':[
            _Result(match_text='T=98'),
            _Result(match_text='BP= 122/58'),
            _Result(match_text='HR= 7'),
            _Result(match_text='RR= 20'),
            _Result(match_text='O2 sat= 100% 2L NC')            
        ],
        'VS:  T-100.6, HR-105, BP-93/46, RR-16, Sats-98% 3L/NC':[
            _Result(match_text='T-100.6'),
            _Result(match_text='HR-105'),
            _Result(match_text='BP-93/46'),
            _Result(match_text='RR-16'),
            _Result(match_text='Sats-98% 3L/NC')            
        ],
        
    }

    if not _run_tests(test_data):
        return False

    return True


###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Run validation tests on the recognizer modules.'
    )
    
    parser.add_argument('-v', '--version',
                        help='show version and exit',
                        action='store_true')
    parser.add_argument('-d', '--debug',
                        help='print debug information to stdout',
                        action='store_true')

    args = parser.parse_args()

    if 'version' in args and args.version:
        print(_get_version())
        sys.exit(0)

    if 'debug' in args and args.debug:
        lvr.enable_debug()

    lvr.init()
    assert test_lab_value_recognizer()

