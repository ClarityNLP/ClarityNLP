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

    _compare_results(test_data)

    # h12m format
    test_data = {
        'The times are 4:08, 10:14, and 12:59':[
            _Result(text='4:08',  hours=4,  minutes=8),
            _Result(text='10:14', hours=10, minutes=14),
            _Result(text='12:59', hours=12, minutes=59)
        ]
    }

    _compare_results(test_data)

    # h12m_am_pm format
    test_data = {
        'The times are 5:09 am, 9:41 P.M., and 10:02 AM.':[
            _Result(text='5:09 am',   hours=5,  minutes=9,  am_pm=tf.STR_AM),
            _Result(text='9:41 P.M.', hours=9,  minutes=41, am_pm=tf.STR_PM),
            _Result(text='10:02 AM.', hours=10, minutes=2,  am_pm=tf.STR_AM)
        ]
    }

    _compare_results(test_data)

    # h12ms_am_pm format
    test_data = {
        'The times are 6:10:37 am, 12:19:36P.M., and 1:02:03AM':[
            _Result(text='6:10:37 am',   hours=6,  minutes=10, seconds=37, am_pm=tf.STR_AM),
            _Result(text='12:19:36P.M.', hours=12, minutes=19, seconds=36, am_pm=tf.STR_PM),
            _Result(text='1:02:03AM',    hours=1,  minutes=2,  seconds=3,  am_pm=tf.STR_AM)
        ]
    }

    _compare_results(test_data)

    # h12msf_am_pm format
    test_data = {
        'The times are 7:11:39:012345 am and 11:41:22.22334p.m..':[
            _Result(text='7:11:39:012345 am', hours=7, minutes=11, seconds=39,
                    fractional_seconds='012345', am_pm=tf.STR_AM),
            _Result(text='11:41:22.22334p.m.', hours=11, minutes=41, seconds=22,
                    fractional_seconds='22334', am_pm=tf.STR_PM)
        ]
    }

    _compare_results(test_data)

    # h24m format
    test_data = {
        'The times are 14:12, 1:27, 01:27, and T23:43.':[
            _Result(text='14:12',  hours=14, minutes=12),
            _Result(text='1:27',   hours=1,  minutes=27),
            _Result(text='01:27',  hours=1,  minutes=27),
            _Result(text='T23:43', hours=23, minutes=43)
        ]
    }

    _compare_results(test_data)
    
    # h24ms format
    test_data = {
        'The times are 01:03:24 and t14:15:16.':[
            _Result(text='01:03:24',  hours=1,  minutes=3,  seconds=24),
            _Result(text='t14:15:16', hours=14, minutes=15, seconds=16)
        ]
    }

    _compare_results(test_data)

    # h24ms_with_timezone format
    test_data = {
        'The times are 040837CEST, 112345 PST, and T093000 Z':[
            _Result(text='040837CEST',  hours=4,  minutes=8,  seconds=37,
                    timezone='CEST'),
            _Result(text='112345 PST',  hours=11, minutes=23, seconds=45,
                    timezone='PST'),
            _Result(text='T093000 Z',  hours=9,  minutes=30, seconds=0,
                    timezone='UTC')
        ]
    }

    _compare_results(test_data)

    # h24ms with GMT delta
    test_data = {
        'The times are T192021-0700 and 14:45:15+03:30':[
            _Result(text='T192021-0700',   hours=19, minutes=20, seconds=21,
                    gmt_delta_sign='-', gmt_delta_hours=7, gmt_delta_minutes=0),
            _Result(text='14:45:15+03:30', hours=14, minutes=45, seconds=15,
                    gmt_delta_sign='+', gmt_delta_hours=3, gmt_delta_minutes=30)
        ]
    }

    _compare_results(test_data)

    # h24msf format
    test_data = {
        'The times are 04:08:37.81412 and 19:20:21.532453.':[
            _Result(text='04:08:37.81412',  hours=4,  minutes=8,  seconds=37,
                    fractional_seconds='81412'),
            _Result(text='19:20:21.532453', hours=19, minutes=20, seconds=21,
                    fractional_seconds='532453')
        ]
    }

    _compare_results(test_data)

    # ISO 8601 format
    test_data = {
        'The times are 08:23:32Z, 09:24:33+12, 10:25:34-04:30, and 11:26:35.012345+0600':[
            _Result(text='08:23:32Z', hours=8, minutes=23, seconds=32,
                    timezone='UTC'),
            _Result(text='09:24:33+12', hours=9, minutes=24, seconds=33,
                    gmt_delta_sign='+', gmt_delta_hours=12),
            _Result(text='10:25:34-04:30', hours=10, minutes=25, seconds=34,
                    gmt_delta_sign='-', gmt_delta_hours=4, gmt_delta_minutes=30),
            _Result(text='11:26:35.012345+0600', hours=11, minutes=26, seconds=35,
                    fractional_seconds='012345', gmt_delta_sign='+',
                    gmt_delta_hours=6, gmt_delta_minutes=0)
        ]
    }

    _compare_results(test_data)
    
