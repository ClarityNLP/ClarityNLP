#!/usr/bin/python3
"""
Test program for the time_finder module.

Run from the same folder as time_finder.py.

"""

import re
import os
import sys
import json
from collections import namedtuple

import time_finder as tf

_VERSION_MAJOR = 0
_VERSION_MINOR = 1
_MODULE_NAME = 'test_time_finder.py'

# set to True to enable debug output
_TRACE = False

# namedtuple for expected results; fields default to None
_RESULT_FIELDS = [
    'text', 'hours', 'minutes', 'seconds', 'fractional_seconds', 'am_pm',
    'timezone', 'gmt_delta_sign', 'gmt_delta_hours', 'gmt_delta_minutes'
]
_Result = namedtuple('_Result', _RESULT_FIELDS)
_Result.__new__.__defaults__ = (None,) * len(_Result._fields)


###############################################################################


###############################################################################
def _compare_results(test_data):
    """
    """

    for sentence, expected_list in test_data.items():

        # run time_finder on the next test sentence
        json_result = tf.run(sentence)

        # load the result data and decode as TimeValue namedtuples
        json_data = json.loads(json_result)
        time_values = [tf.TimeValue(**d) for d in json_data]

        # check that len(computed) == len(expected)
        if len(time_values) != len(expected_list):
            print('\tMismatch in computed vs. expected results: ')
            print('\tSentence: {0}'.format(sentence))
            print('\tComputed: ')
            for v in time_values:
                print('\t\t{0}'.format(v))
            print('\tExpected: ')
            for e in expected_list:
                print('\t\t{0}'.format(e))

            print('NAMEDTUPLE: ')
            for k,v in v._asdict().items():
                print('{0} => {1}'.format(k,v))
                
            return

        # check fields for each result
        failures = []
        for i, t in enumerate(time_values):
            # iterate over fields of current result
            for field, value in t._asdict().items():
                expected = expected_list[i]._asdict()
                # compare only those fields in _RESULT_FIELDS
                if field in _RESULT_FIELDS:
                    if value != expected[field]:
                        # append as namedtuples
                        failures.append( (t, expected_list[i]) )

        if len(failures) > 0:
            print(sentence)
            for f in failures:
                # extract fields with values not equal to None
                c = [ (k,v) for k,v in f[0]._asdict().items()
                      if v is not None and k in _RESULT_FIELDS]
                e = [ (k,v) for k,v in f[1]._asdict().items() if v is not None]
                print('\tComputed: {0}'.format(c))
                print('\tExpected: {0}'.format(e))


###############################################################################
def _get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
def _show_help():
    print(_get_version())
    print("""
    USAGE: python3 ./{0}

    FLAGS:

        -h, --help                      Print this information and exit.
        -v, --version                   Print version information and exit.

    """.format(_MODULE_NAME))


###############################################################################
if __name__ == '__main__':

    #'text', 'hours', 'minutes', 'seconds', 'fractional_seconds', 'am_pm',
    #'timezone', 'gmt_delta_sign', 'gmt_delta_hours', 'gmt_delta_minutes'

    
    # h12_am_pm format
    test_data = {
        'The times are 4 am, 5PM, 10a.m, 8 a.m, 9 pm., .':[
            _Result(text='4 am',  hours=4,  am_pm=tf.STR_AM),
            _Result(text='5PM',   hours=5,  am_pm=tf.STR_PM),
            _Result(text='10a.m', hours=10, am_pm=tf.STR_AM),
            _Result(text='8 a.m', hours=8,  am_pm=tf.STR_AM),
            _Result(text='9 pm.', hours=9,  am_pm=tf.STR_PM)
        ]
    }

    # h12m format
    test_data = {
        'The times are 4:08, 10:14, and 12:59':[
            _Result(text='4:08',  hours=4,  minutes=8),
            _Result(text='10:14', hours=10, minutes=14),
            _Result(text='12:59', hours=12, minutes=59)
        ]
    }

    # h12m_am_pm format
    test_data = {
        'The times are 5:09 am, 9:41 P.M., and 10:02 AM.':[
            _Result(text='5:09 am',   hours=5,  minutes=9,  am_pm=tf.STR_AM),
            _Result(text='9:41 P.M.', hours=9,  minutes=41, am_pm=tf.STR_PM),
            _Result(text='10:02 AM.', hours=10, minutes=2,  am_pm=tf.STR_AM)
        ]
    }

    # h12ms_am_pm format
    test_data = {
        'The times are 6:10:37 am, 12:19:36P.M., and 1:02:03AM':[
            _Result(text='6:10:37 am',   hours=6,  minutes=10, seconds=37, am_pm=tf.STR_AM),
            _Result(text='12:19:36P.M.', hours=12, minutes=19, seconds=36, am_pm=tf.STR_PM),
            _Result(text='1:02:03AM',   hours=1,  minutes=2,  seconds=3,  am_pm=tf.STR_AM)
        ]
    }

    # h12msf_am_pm format
    test_data = {
        'The times are 7:11:39:123456 am and 11:41:22.22334p.m..':[
            _Result(text='7:11:39:123456 am', hours=7, minutes=11, seconds=39, fractional_seconds=123456)
        ]
    }

    _compare_results(test_data)
    
    
