#!/usr/bin/env python3
"""

OVERVIEW:


The code in this module recognizes time expressions in a sentence and returns
a JSON result with information on each time expression that it finds. The
supported time formats are listed next, using the abbreviations:

    h12: 12 hr. clock, hours only, 0-9
    h24: 24 hr. clock, hours only, zero-padded, 00-24
     mm: minutes, zero-padded, 00-59
     ss: seconds, zero-padded 00-60 (60 means leap second)

    The symbol 'am_pm' is OPTIONAL and can be any of these variants:

        'am', 'pm', 'AM', 'PM', 'a.m.', 'p.m.', 'A.M.', 'P.M.', 'am.', 'pm.'

        There can be arbitrary whitespace before the am_pm symbol.
                   
    The symbol 't' is OPTIONAL and can be any of these variants:

         't', 'T'

    The symbol 'f' means fractional seconds (expressed as a decimal number)
    For instance, a value of 23.44506 would have f == 44506.


1.  ISO 8601 Formats

    Any of these formats:

        <time>Z
        <time>+-hh:mm
        <time>+-hhmm
        <time>+-hh
        YYYY-MM-DDTHH:MM:SS.ffffff

    Where <time> means any of these:

        hh
        hh:mm or hhmm
        hh:mm:ss or hhmmss
        hh:mm:ss.\d+  or hhmmss.\d+ (any number of fractional digits)

2.  Any of these formats:

    h12 am_pm    hours with AM/PM designator
                 (4 am, 5PM, 10a.m., 9 pm.)

    h12m am_pm   hours and minutes with AM/PM designator
                 (5:09 am, 9:41 P.M., 10:02 AM.)

    h12ms am_pm  hours, minutes, and seconds with AM/PM designator
                 (06:10:37 am, 10:19:36P.M., 1:02:03AM)

    h12msf am_pm hours, minutes, seconds, fractional seconds with AM/PM
                 (7:11:39:012345 am, 11:41:22.22334 p.m.)

    h12m         hours and minutes
                 (4:08, 10:14, and 11:59)

    th24m        hours and minutes
                 (14:12, 01:27, 10:27, T23:43)

    th24ms       hours, minutes, and seconds
                 (01:03:24, T14:15:16)

    th24msf      hours, minutes, seconds, fractional seconds
                 (04:08:37.81412, 19:20:21.532453, 08:11:40:123456)

    thhmm        hours and minutes
                 (0613, t0613)


    thhmmss      hours, minutes, and seconds
                 (232120, 120000)

    th24ms with timezone   hours, minutes, and seconds with timezone designator
                           (040837CEST, 112345 PST, T093000 Z)

    th24ms with GMT offset hours, minutes, seconds with GMT offset designator
                           (T192021-0700, 14:45:15+03:30)



OUTPUT:



The set of JSON fields in the output for each time expression includes:

    text                matching text
    start               starting character offset of the matching text
    end                 final character offset of the matching text + 1
    hours               integer hours
    minutes             integer minutes
    seconds             integer seconds
    fractional_seconds  string, contains digits after decimal point
                        including any leading zeros
    am_pm               string, either STR_AM or STR_PM (see values below)
    timezone            string
    gmt_delta_sign      sign of the UTC offset, either '+' or '-'
    gmt_delta_hours     integer, UTC hour offset
    gmt_delta_minutes   integer, UTC minute offset

Any missing fields will have the value EMPTY_FIELD. All JSON results will
contain an identical number of fields.

All time expression recognition is case-insensitive.

JSON results are written to stdout.



USAGE:



To use this code as an imported module, add the following lines to the
import list in the importing module:

        import json
        import time_finder as tf

To find time expressions in a sentence and capture the JSON result:

        json_string = tf.run(sentence)

To unpack the JSON results:

        json_data = json.loads(json_string)
        time_results = [df.TimeValue(**m) for m in json_data]

        for t in time_results:
            log(t.text)
            log(t.start)
            log(t.end)
            if tf.EMPTY_FIELD != t.hours:
                log(t.hours)
            etc.

References: 

    PHP Time Formats:
        http://php.net/manual/en/datetime.formats.time.php

    World time zones:
        https://en.wikipedia.org/wiki/List_of_time_zone_abbreviations

    ISO8601 formats:
        https://en.wikipedia.org/wiki/ISO_8601

"""

import re
import os
import sys
import json
from collections import namedtuple
from claritynlp_logging import log, ERROR, DEBUG


try:
    import finder_overlap as overlap
except:
    from algorithms.finder import finder_overlap as overlap

# default value for all fields
EMPTY_FIELD = None

TIME_VALUE_FIELDS = [
    'text',
    'start',
    'end',
    'hours',
    'minutes',
    'seconds',
    'fractional_seconds',
    'am_pm',
    'timezone',
    'gmt_delta_sign',
    'gmt_delta_hours',
    'gmt_delta_minutes'
]
TimeValue = namedtuple('TimeValue', TIME_VALUE_FIELDS)

# set default value of all fields to EMPTY_FIELD
TimeValue.__new__.__Defaults__ = (EMPTY_FIELD,) * len(TimeValue._fields)

STR_AM = 'am'
STR_PM = 'pm'


###############################################################################


_VERSION_MAJOR = 0
_VERSION_MINOR = 6
_MODULE_NAME = 'time_finder.py'

# set to True to see debug output
_TRACE = False

# fractional seconds
_str_frac = r'[.:][0-9]+'

# hours, 12-hour clock
_str_h12 = r'(0?[1-9]|1[0-2])'

# hours, 24-hour clock
_str_h24 = r'([01][0-9]|2[0-4])'

# am or pm
_str_am_pm = r'[aApP]\.?[mM]\.?'

# minutes
_str_MM = r'[0-5][0-9]'

# world time zones (added 'Z' for Zulu == zero meridian)
_str_time_zone_abbrev = r'(ACDT|ACST|ACT|ACWST|ADT|AEDT|AEST|AFT|AKDT|'      +\
    'AKST|AMST|AMT|ART|AST|AWST|AZOST|AZOT|AZT|BDT|'      +\
    'BIOT|BIT|BOT|BRST|BRT|BST|BTT|CAT|CCT|CDT|CEST|'     +\
    'CET|CHADT|CHAST|CHOT|CHOST|CHST|CHUT|CIST|CIT|'      +\
    'CKT|CLST|CLT|COST|COT|CST|CT|CVT|CWST|CXT|DAVT|'     +\
    'DDUT|DFT|EASST|EAST|EAT|ECT|EDT|EEST|EET|EGST|'      +\
    'EGT|EIT|EST|FET|FJT|FKST|FKT|FNT|GALT|GAMT|GET|'     +\
    'GFT|GILT|GIT|GMT|GST|GYT|HDT|HAEC|HST|HKT|HMT|'      +\
    'HOVST|HOVT|ICT|IDLW|IDT|IOT|IRDT|IRKT|IRST|IST|'     +\
    'JST|KGT|KOST|KRAT|KST|LHST|LINT|MAGT|MART|MAWT|'     +\
    'MDT|MET|MEST|MHT|MIST|MIT|MMT|MSK|MST|MUT|MVT|'      +\
    'MYT|NCT|NDT|NFT|NPT|NST|NT|NUT|NZDT|NZST|OMST|'      +\
    'ORAT|PDT|PET|PETT|PGT|PHOT|PHT|PKT|PMDT|PMST|'       +\
    'PONT|PST|PYST|PYT|RET|ROTT|SAKT|SAMT|SAST|SBT|'      +\
    'SCT|SDT|SGT|SLST|SRET|SRT|SST|SYOT|THAT|THA|TFT|'    +\
    'TJT|TKT|TLT|TMT|TRT|TOT|TVT|ULAST|ULAT|USZ1|UTC|'    +\
    'UYST|UYT|UZT|VET|VLAT|VOLT|VOST|VUT|WAKT|WAST|'      +\
    'WAT|WEST|WET|WIT|WST|YAKT|YEKT|Z)'

# separator, colon only (not supporting '.' as a separator)
_str_sep = r'[:]'

# t or T, to indicate time
_str_t = r'\b[tT]?'


# 12 hour notation


# hour only, with am_pm:
#    4 am, 5PM, 10a.m., 9 pm.
_str_h12_am_pm = r'\b(?P<hours>' + _str_h12    + r')' + r'\s*'                +\
                 r'(?P<am_pm>'   + _str_am_pm  + r')'
_regex_h12_am_pm = re.compile(_str_h12_am_pm)

# hour and minutes:
#    4:08, 10:14
_str_h12m = r'\b(?<![:])(?P<hours>' + _str_h12 + r')'+ _str_sep               +\
            r'(?P<minutes>' + _str_MM  + r'(?![\d:]))'
_regex_h12m = re.compile(_str_h12m)

# hour and minutes, with am_pm:
#    5:09 am, 9:41 P.M., 10:02 AM
_str_h12m_am_pm = r'\b(?P<hours>' + _str_h12   + r')' + _str_sep              +\
                  r'(?P<minutes>' + _str_MM    + r')' + r'\s*'                +\
                  r'(?P<am_pm>'   + _str_am_pm + r'(?!\d))'
_regex_h12m_am_pm = re.compile(_str_h12m_am_pm)

# hour, minutes, and seconds, with am_pm:
#    6:10:37 am, 7:19:19P.M.
_str_h12ms_am_pm = r'\b(?P<hours>' + _str_h12   + r')' + _str_sep             +\
                   r'(?P<minutes>' + _str_MM    + r')' + _str_sep             +\
                   r'(?P<seconds>' + _str_MM    + r')' + r'\s*'               +\
                   r'(?P<am_pm>'   + _str_am_pm + r')'
_regex_h12ms_am_pm = re.compile(_str_h12ms_am_pm)

# hour, minutes, seconds, and fraction, with am_pm:
#    7:11:39:123123 am and 9:41:22.22334p.m.
_str_h12msf_am_pm = r'\b(?P<hours>' + _str_h12   + r')' + r':'                +\
                    r'(?P<minutes>' + _str_MM    + r')' + r':'                +\
                    r'(?P<seconds>' + _str_MM    + r')'                       +\
                    r'(?P<frac>'    + _str_frac  + r')' + r'\s*'              +\
                    r'(?P<am_pm>'   + _str_am_pm + r')'
_regex_h12msf_am_pm = re.compile(_str_h12msf_am_pm)


# 24 hour notation


# hour and minutes:
#    08:12, T23:43
_str_h24m = _str_t                                                   +\
           r'(?<![:])(?P<hours>'   + _str_h24 + r')' + _str_sep      +\
           r'(?P<minutes>' + _str_MM  + r'(?![\d:]))'
_regex_h24m = re.compile(_str_h24m)

# hour and minutes, no colon
_str_h24m_no_colon = _str_t                                          +\
                    r'(?<![-+\.:])(?P<hours>'   + _str_h24 + r')'    +\
                    r'(?P<minutes>' + _str_MM  + r'(?![-\d:]))'
_regex_h24m_no_colon = re.compile(_str_h24m_no_colon)

# hour, minutes, and seconds
#    01:03:24, t14:15:16
_str_h24ms = _str_t                                       +\
            r'(?P<hours>'   + _str_h24 + r')' + _str_sep  +\
            r'(?P<minutes>' + _str_MM  + r')' + _str_sep  +\
            r'(?P<seconds>' + _str_MM  + r'(?!\d))'
_regex_h24ms = re.compile(_str_h24ms)

# hour, minutes, and seconds, no colon
_str_h24ms_no_colon = _str_t                             +\
                     r'(?P<hours>'   + _str_h24 + r')'   +\
                     r'(?P<minutes>' + _str_MM  + r')'   +\
                     r'(?P<seconds>' + _str_MM  + r'(?![-\d:]))'
_regex_h24ms_no_colon = re.compile(_str_h24ms_no_colon)

# hour, minutes, seconds, and timezone
#    040837EST, 112345 HOVST, T093000 Z
_str_h24ms_with_timezone = _str_t                                             +\
                          r'(?P<hours>'    + _str_h24 + r')'                  +\
                          r'(?P<minutes>'  + _str_MM  + r')'                  +\
                          r'(?P<seconds>'  + _str_MM  + r')'       + r'\s*'   +\
                          r'(?P<timezone>' + _str_time_zone_abbrev + r')'
_regex_h24ms_with_timezone = re.compile(_str_h24ms_with_timezone, re.IGNORECASE)

# hour, minutes, seconds with GMT delta
_str_gmt_delta = r'(GMT|UTC)?[-+]' + _str_h24 + r':?' + r'(' + _str_MM + r')?'
_str_h24ms_with_gmt_delta = _str_t                                            +\
                           r'(?P<hours>'   + _str_h24 + r')'                  +\
                           r'(?P<minutes>' + _str_MM  + r')'                  +\
                           r'(?P<seconds>' + _str_MM  + r')'  + r'\s*'        +\
                           r'(?P<gmt_delta>' + _str_gmt_delta + r')'

# decipher the gmt_delta components
_str_gmt = r'(GMT|UTC)?(?P<gmt_sign>'+ r'[-+]' + r')'          +\
           r'(?P<gmt_hours>' + _str_h24 + r')'  + r':?'        +\
           r'(' + r'(?P<gmt_minutes>' + _str_MM + r')' + r')?'
_regex_gmt = re.compile(_str_gmt)

_regex_h24ms_with_gmt_delta = re.compile(_str_h24ms_with_gmt_delta, re.IGNORECASE)

# hour, minutes, seconds, and fraction
_str_h24msf = _str_t                                           +\
             r'(?P<hours>'   + _str_h24  + r')' + _str_sep     +\
             r'(?P<minutes>' + _str_MM   + r')' + _str_sep     +\
             r'(?P<seconds>' + _str_MM   + r')'                +\
             r'(?P<frac>'    + _str_frac + r')'
_regex_h24msf = re.compile(_str_h24msf)


# ISO8601 formats:
#
# hh is zero-padded 00-24
# mm is zero-padded 00-59
# ss is zero-padded 00-60 (60 means leap second)

# <time>
#     hh
#     hh:mm or hhmm
#     hh:mm:ss or hhmmss
#     hh:mm:ss.\d+  or hhmmss.\d+ (any number of fractional digits)

# time zone designators
# <time>Z
# <time>+-hh:mm
# <time>+-hhmm
# <time>+-hh

_str_iso_hh = r'([01][0-9]|2[0-4])'
_str_iso_mm = r'[0-5][0-9]'
_str_iso_ss = r'([0-5][0-9]|60)'

_str_iso_zone_hm = r'(?P<gmt_hours>' + _str_iso_hh + r'(?![-+]))'            +\
                   r'(:?' + r'(?P<gmt_minutes>' + _str_iso_mm + r'))?'

_str_iso_zone = r'((?P<timezone>Z)|'                                         +\
                r'(?P<gmt_sign>[-+])' + _str_iso_zone_hm + r')'

# note the essential negative lookahead in these, prevents matching of
# portions of floating point numbers
_str_iso_hh_only = r'(?<![-+\d:])(?P<hours>' + _str_iso_hh + r'(?![\d\.:]))' +\
                   r'((?P<gmt_delta>' + _str_iso_zone + r'))?'

_str_iso_hhmm_only_1 = r'(?<![-+\d:])(?P<hours>' + _str_iso_hh + r')'        +\
                       r'(?P<minutes>' + _str_iso_mm + r')'                  +\
                       r'((?P<gmt_delta>' + _str_iso_zone + r'))'

_str_iso_hhmm_only_2 = r'(?<![-+\d:])(?P<hours>' + _str_iso_hh + r')'        +\
                       r'(?P<minutes>' + _str_iso_mm + r'(?![-+\d\.]))'


_str_iso_hms = r'(?<![-+\d:])(?P<hours>'  + _str_iso_hh + r'):?'             +\
               r'((?P<minutes>' + _str_iso_mm + r')):?'                      +\
               r'((?P<seconds>' + _str_iso_ss + r'))'                        +\
               r'((?P<frac>'    + r'\.\d+'   + r'))?'

_str_iso_time = _str_iso_hms + r'((?P<gmt_delta>' + _str_iso_zone + r'))?'

_regex_iso_hh   = re.compile(_str_iso_hh_only)
_regex_iso_hhmm1 = re.compile(_str_iso_hhmm_only_1)
_regex_iso_hhmm2 = re.compile(_str_iso_hhmm_only_2)
_regex_iso_time = re.compile(_str_iso_time)

# ISO datetime format: YYYY-MM-DDTHH:MM:SS.ffffff
# fractional seconds are optional
# negative lookahead prevents extraction of a subset of a larger expression
_str_iso_datetime = r'(?<!\d-)\d{4}\-\d\d\-\d\dT' + _str_iso_hms + r'(?![-+\d\.])'
_regex_iso_datetime = re.compile(_str_iso_datetime)

_regexes = [
    _regex_iso_datetime,         # 0
    _regex_iso_hhmm1,            # 1
    _regex_iso_hhmm2,            # 2
    _regex_iso_hh,               # 3
    _regex_iso_time,             # 4
    _regex_h24ms_with_gmt_delta, # 5
    _regex_h24ms_with_timezone,  # 6
    _regex_h24ms_no_colon,       # 7
    _regex_h24m_no_colon,        # 8
    _regex_h12msf_am_pm,         # 9
    _regex_h12ms_am_pm,          # 10
    _regex_h12m_am_pm,           # 11
    _regex_h12_am_pm,            # 12
    _regex_h24msf,               # 13
    _regex_h24ms,                # 14
    _regex_h24m,                 # 15
    _regex_h12m,                 # 16
]

# index of the ISO datetime regex in the _regexes array
_ISO_DATETIME_REGEX_INDEX = 0

# match (), {}, and []
_str_brackets = r'[(){}\[\]]'
_regex_brackets = re.compile(_str_brackets)


###############################################################################
def enable_debug():

    global _TRACE
    _TRACE = True


###############################################################################
def _clean_sentence(sentence):
    """
    Do some preliminary processing on the sentence.
    """

    # erase [], {}, or () from the sentence
    sentence = _regex_brackets.sub(' ', sentence)

    return sentence


###############################################################################
def run(sentence):
    """

    Find time expressions in the sentence by attempting to match all regexes.
    Avoid matching sub-expressions of already-matched strings. Returns a JSON
    array containing info on each date found.
    
    """    

    results    = [] # TimeValue namedtuple results
    candidates = [] # potential matches, need overlap resolution to confirm

    original_sentence = sentence
    sentence = _clean_sentence(sentence)

    if _TRACE:
        log('original: {0}'.format(original_sentence))
        log(' cleaned: {0}'.format(sentence))
        
    for regex_index, regex in enumerate(_regexes):
        iterator = regex.finditer(sentence)
        for match in iterator:
            match_text = match.group().strip()
            t_adjustment = 0
            if _ISO_DATETIME_REGEX_INDEX == regex_index:
                # extract only the time portion
                t_pos = match_text.find('T')
                assert -1 != t_pos
                match_text = match_text[t_pos+1:]
                t_adjustment = t_pos+1
            start = match.start() + t_adjustment
            end = start + len(match_text)
            candidates.append(overlap.Candidate(start, end, match_text, regex))
            if _TRACE:
                log('[{0:2}]: [{1:3}, {2:3})\tMATCH TEXT: ->{3}<-'.
                      format(regex_index, start, end, match_text))

            
    # sort the candidates in descending order of length, which is needed for
    # one-pass overlap resolution later on
    candidates = sorted(candidates, key=lambda x: x.end-x.start, reverse=True)

    if _TRACE:
        log('\tCandidate matches: ')
        index = 0
        for c in candidates:
            log('\t[{0:2}]\t[{1},{2}): {3}'.
                  format(index, c.start, c.end, c.match_text, c.regex))
            index += 1
        log()

    pruned_candidates = overlap.remove_overlap(candidates, _TRACE)

    if _TRACE:
        log('\tcandidates count after overlap removal: {0}'.
              format(len(pruned_candidates)))
        log('\tPruned candidates: ')
        for c in pruned_candidates:
            log('\t\t[{0},{1}): {2}'.format(c.start, c.end, c.match_text))
        log()

    if _TRACE:
        log('Extracting data from pruned candidates...')
        
    for pc in pruned_candidates:

        # used the saved regex to match the saved text again
        if _regex_iso_datetime == pc.regex:
            # match only time portion
            match = _regex_iso_time.match(pc.match_text)
        else:
            match = pc.regex.match(pc.match_text)
        assert match

        int_hours         = EMPTY_FIELD
        int_minutes       = EMPTY_FIELD
        int_seconds       = EMPTY_FIELD
        frac_seconds      = EMPTY_FIELD
        am_pm             = EMPTY_FIELD
        timezone          = EMPTY_FIELD
        gmt_delta         = EMPTY_FIELD
        gmt_delta_sign    = EMPTY_FIELD
        gmt_delta_hours   = EMPTY_FIELD
        gmt_delta_minutes = EMPTY_FIELD

        for k,v in match.groupdict().items():
            if v is None:
                continue
            if 'hours' == k:
                int_hours = int(v)
            elif 'minutes' == k:
                int_minutes = int(v)
            elif 'seconds' == k:
                int_seconds = int(v)
            elif 'frac' == k:
                # leave as a string; conversion needs to handle leading zeros
                frac_seconds = v[1:]
            elif 'am_pm' == k:
                if -1 != v.find('a') or -1 != v.find('A'):
                    am_pm = STR_AM
                else:
                    am_pm = STR_PM
            elif 'timezone' == k:
                timezone = v
                if 'Z' == timezone:
                    timezone = 'UTC'
            elif 'gmt_delta' == k:
                gmt_delta = v    
                match_gmt = _regex_gmt.search(v)
                if match_gmt:
                    for k2,v2 in match_gmt.groupdict().items():
                        if v2 is None:
                            continue
                        if 'gmt_sign' == k2:
                            gmt_delta_sign = v2
                        elif 'gmt_hours' == k2:
                            gmt_delta_hours = int(v2)
                        elif 'gmt_minutes' == k2:
                            gmt_delta_minutes = int(v2)

        meas = TimeValue(
            text = pc.match_text,
            start = pc.start,
            end = pc.end,
            hours = int_hours,
            minutes = int_minutes,
            seconds = int_seconds,
            fractional_seconds = frac_seconds,
            am_pm = am_pm,
            timezone = timezone,
            gmt_delta_sign = gmt_delta_sign,
            gmt_delta_hours = gmt_delta_hours,
            gmt_delta_minutes = gmt_delta_minutes
        )
        results.append(meas)

    # sort results to match order of occurrence in sentence
    results = sorted(results, key=lambda x: x.start)
    
    # convert to list of dicts to preserve field names in JSON output
    return json.dumps([r._asdict() for r in results], indent=4)


###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)

