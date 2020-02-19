#!/usr/bin/env python3
"""
Parse a time command string used as an argument for a custom task.
The supported formats are:

    # absolute timestamps
    # leading zeroes are allowed for each component

    LATEST()                           - the earliest data point
    EARLIEST()                         - the latest data point
    DATE(YYYY, MM, DD)                 - absolute date
    DATETIME(YYYY, MM, DD, HH, mm, ss) - absolute datetime

    # can also add or subtract an offset in days to these, to 
    # create a time window

    LATEST() - 30d
    EARLIEST + 7d
    DATE(2019, 1, 23) + 20d
    DATETIME(2019, 2, 2) - 4d

"""

import os
import re
import sys
from dateutil.tz import tzutc
from datetime import datetime, timedelta

if __name__ == '__main__':
    # modify path for local testing
    cur_dir = sys.path[0]
    nlp_dir, tail = os.path.split(cur_dir)
    sys.path.append(nlp_dir)
    sys.path.append(os.path.join(nlp_dir, 'algorithms', 'finder'))

from claritynlp_logging import log, ERROR, DEBUG

# set to True to enable debug output
_TRACE = False

# DATETIME(YYYY, MM, DD, hh, mm, ss)
_str_datetime = r'DATETIME\('           +\
    r'\s*(?P<year>\d\d\d\d)\s*,'        +\
    r'\s*(?P<month>[0-1]?[0-9])\s*,'    +\
    r'\s*(?P<day>[0-3]?[0-9])\s*,'      +\
    r'\s*(?P<hour>[0-5]?[0-9])\s*,'     +\
    r'\s*(?P<minute>[0-5]?[0-9])\s*,'  +\
    r'\s*(?P<second>[0-5]?[0-9])\s*\)'

_regex_datetime = re.compile(_str_datetime, re.IGNORECASE)

# DATE(YYYY, MM, DD)
_str_date = r'DATE\('                +\
    r'\s*(?P<year>\d\d\d\d)\s*,'     +\
    r'\s*(?P<month>[0-1]?[0-9])\s*,' +\
    r'\s*(?P<day>[0-3]?[0-9])\s*\)'

_regex_date = re.compile(_str_date, re.IGNORECASE)

# EARLIEST()
_str_earliest = r'EARLIEST\(\s*\)'
_regex_earliest = re.compile(_str_earliest, re.IGNORECASE)

# LATEST()
_str_latest = r'LATEST\(\s*\)'
_regex_latest = re.compile(_str_latest, re.IGNORECASE)

# offset in days (+30d, - 7d, for instance)
_regex_operator = re.compile(r'[-+]')
_regex_offset = re.compile(r'(?P<num>\d+)(?P<units>[d])', re.IGNORECASE)

_STR_MINUS = 'minus'
_STR_PLUS  = 'plus'


###############################################################################
def _to_date(match):
    """
    Extract date components from a regex match and return datetime object.
    """
    year = int(match.group('year'))
    month = int(match.group('month'))
    day = int(match.group('day'))

    obj = datetime(year, month, day, tzinfo=tzutc())
    return obj

    
###############################################################################
def _to_datetime(match):
    """
    Extract datetime components from a _regex_datetime match and return
    a datetime object.
    """

    year = int(match.group('year'))
    month = int(match.group('month'))
    day = int(match.group('day'))
    hour = int(match.group('hour'))
    minute = int(match.group('minute'))
    second = int(match.group('second'))

    obj = datetime(year, month, day, hour, minute, second, tzinfo=tzutc())
    return obj
    

###############################################################################
def parse_time_command(time_string, data_earliest, data_latest):
    """
    Parse a time command string and return an absolute datetime or None if
    there is a syntax error present.
    """

    s = time_string.strip()
    
    dt = None
    op_string = None
    dt_result = None
    
    while len(s) > 0:
        match = _regex_datetime.search(s)
        if match:
            dt = _to_datetime(match)
            if _TRACE: log('\tDATETIME: {0}'.format(dt))
            s = s[match.end():]
        match = _regex_date.search(s)
        if match:
            dt = _to_date(match)
            if _TRACE: log('\tDATE: {0}'.format(dt))
            s = s[match.end():]
        match = _regex_earliest.search(s)
        if match:
            dt = data_earliest
            if _TRACE: log('\tEARLIEST: {0}'.format(data_earliest))
            s = s[match.end():]
        match = _regex_latest.search(s)
        if match:
            dt = data_latest
            if _TRACE: log('\tLATEST: {0}'.format(data_latest))
            s = s[match.end():]
        match = _regex_operator.search(s)
        if match:
            if '-' == match.group():
                op_string = _STR_MINUS                
            else:
                op_string = _STR_PLUS
            if _TRACE: log('\tOPERATOR: {0}'.format(op_string))
            s = s[match.end():]
            continue
        match = _regex_offset.search(s)
        if match:
            num = int(match.group('num'))
            units = match.group('units').lower()
            assert op_string is not None
            assert dt is not None
            if _STR_MINUS == op_string:
                dt_result = dt - timedelta(days=num)
            else:
                dt_result = dt + timedelta(days=num)
            if _TRACE: log('\tOFFSET: num: {0}, units: {1}, op_string: {2}, result: {3}'.
                  format(num, units, op_string, dt_result))
            s = s[match.end():]
            continue

        if 0 == len(s) and dt_result is None:
            # absolute timestamp
            dt_result = dt
        else:
            # syntax error
            return None
    
    return dt_result
        

###############################################################################
if __name__ == '__main__':

    # interactive testing from command line
    
    DATETIME_STRINGS = [
        "DATETIME(2019, 5, 17, 1, 2, 3)",
        "DATETIME(2019, 05, 01, 01, 02, 03)",
        "DATETIME(2019, 0, 0, 0, 0, 0)",
        "DATETIME(2019, 00, 00, 00, 00, 00)",
        "DATETIME(2019, 12, 31, 59, 59, 59)",
    ]

    DATE_STRINGS = [
        "DATE(2019, 5, 17)",
        "DATE(2019, 05, 01)",
        "DATE(2019, 0, 0)",
        "DATE(2019, 00, 00)",
        "DATE(2019, 12, 31)",
    ]

    COMMAND_STRINGS = [
        "LATEST()",
        "EARLIEST()",
        "DATE(2017, 05, 10)",
        "DATETIME(2017, 05, 24, 03, 04, 05)",

        # LATEST() - offset
        "LATEST() - 30d",
        "LATEST()-07d",

        # EARLIEST() + offset
        "EARLIEST() +4d",
        "EARLIEST()+   10d",

        # DATE +- offset
        "DATE(2019, 05, 15) + 2d",
        "DATE(2019, 05, 08) -07d",

        # DATETIME +- offset
        "DATETIME(2019, 05, 28, 01, 02, 03) - 20d",
        "DATETIME(2019, 05, 5, 10, 11, 12) + 1d",

        # syntax errors
        "DATETM(2019, 05, 6)",
        "DATE(2019, 05, 01) + ",
        "DATETIME(2019, 05, 06, 1, 2, 3) - 40m",
    ]
    
    print('\ntesting DATETIME...')
    for s in DATETIME_STRINGS:
        match = _regex_datetime.search(s)
        if match:
            year = int(match.group('year'))
            month = int(match.group('month'))
            day = int(match.group('day'))
            hour = int(match.group('hour'))
            minutes = int(match.group('minute'))
            seconds = int(match.group('second'))
            print('\t{0}/{1}/{2}:{3}:{4}:{5}'.format(year, month, day, hour, minutes, seconds))

    print('\ntesting DATE...')
    for s in DATE_STRINGS:
        match = _regex_date.search(s)
        if match:
            year = int(match.group('year'))
            month = int(match.group('month'))
            day = int(match.group('day'))
            print('\t{0}/{1}/{2}'.format(year, month, day))

    print('\ntesting command strings...')
    # to mimic earliest/latest from data
    data_earliest = datetime(2019, 5, 1)
    data_latest   = datetime(2019, 8, 1)
    for s in COMMAND_STRINGS:
        print('->{0}<-'.format(s))
        dt_result = parse_time_command(s, data_earliest, data_latest)
        if dt_result is None:
            print('\tSyntax error')
        else:
            print('\t{0}'.format(dt_result))

