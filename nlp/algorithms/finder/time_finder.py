#!/usr/bin/env python3
"""

TODO: add relative time expressions

    check python dateutil

    unknowns:      ??-Aug-2013
    date range:    4/2-5/13, 4/2-5/3/2013
    abbreviations: 2 wks, 1 1/2 wk, 1 wk
    age:           3 days old
    duration:      for 6 months, a year, over 2 hours, q. 6-8 hrs
                   duration words: for, over, last, lasting, lasted, within
    frequency:     every three days
    relative time: three days after 02APR13
                   two hours after

                   relative time words: before, after, prior, later,
                                        earlier, post, ago, next, following

    2 and 5 dec 2019

References: 

PHP Time Formats:
    http://php.net/manual/en/datetime.formats.time.php

World time zones:
    https://en.wikipedia.org/wiki/List_of_time_zone_abbreviations

ISO8601 formats:
    https://en.wikipedia.org/wiki/ISO_8601

Maybe check Stanford's SUTime.

"""

import re
import os
import sys
import json
from collections import namedtuple

# 'TimeValue' is the JSON-serializable result object from this module
EMPTY_FIELD = None
TIME_VALUE_FIELDS = ['text', 'start', 'end', 'hours', 'minutes', 'seconds',
                     'fractional_seconds', 'am_pm', 'timezone',
                     'gmt_delta_sign', 'gmt_delta_hours', 'gmt_delta_minutes']
TimeValue = namedtuple('TimeValue', TIME_VALUE_FIELDS)
STR_AM = 'am'
STR_PM = 'pm'

_VERSION_MAJOR = 0
_VERSION_MINOR = 1
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
_str_time_zone_abbrev = r'(ACDT|ACST|ACT|ACWST|ADT|AEDT|AEST|AFT|AKDT|'       +\
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
_str_h12m = r'\b(?P<hours>' + _str_h12 + r')'+ _str_sep                       +\
            r'(?P<minutes>' + _str_MM  + r')'
_regex_h12m = re.compile(_str_h12m)

# hour and minutes, with am_pm:
#    5:09 am, 9:41 P.M., 10:02 AM
_str_h12m_am_pm = r'\b(?P<hours>' + _str_h12   + r')' + _str_sep              +\
                  r'(?P<minutes>' + _str_MM    + r')' + r'\s*'                +\
                  r'(?P<am_pm>'   + _str_am_pm + r')'
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
_str_h24m = _str_t                                        +\
           r'(?P<hours>'   + _str_h24 + r')' + _str_sep   +\
           r'(?P<minutes>' + _str_MM  + r')'
_regex_h24m = re.compile(_str_h24m)

# hour and minutes, no colon
# _str_h24m_no_colon = _str_t                               +\
#                     r'(?P<hours>'   + _str_h24 + r')'    +\
#                     r'(?P<minutes>' + _str_MM  + r')'
# _regex_h24m_no_colon = re.compile(_str_h24m_no_colon)

# hour, minutes, and seconds
#    01:03:24, t14:15:16
_str_h24ms = _str_t                                       +\
            r'(?P<hours>'   + _str_h24 + r')' + _str_sep  +\
            r'(?P<minutes>' + _str_MM  + r')' + _str_sep  +\
            r'(?P<seconds>' + _str_MM  + r')'
_regex_h24ms = re.compile(_str_h24ms)

# hour, minutes, and seconds, no colon
# _str_h24ms_no_colon = _str_t                              +\
#                      r'(?P<hours>'   + _str_h24 + r')'   +\
#                      r'(?P<minutes>' + _str_MM  + r')'   +\
#                      r'(?P<seconds>' + _str_MM  + r')'
# _regex_h24ms_no_colon = re.compile(_str_h24ms_no_colon)

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

_str_iso_hms = r'\b(?P<hours>'  + _str_iso_hh + r'):?'                        +\
               r'((?P<minutes>' +  _str_iso_mm + r'))?:?'                     +\
               r'((?P<seconds>' + _str_iso_ss + r'))?'                        +\
               r'((?P<frac>'    + r'\.\d+'   + r'))?'

_str_iso_zone_hm = r'(?P<gmt_hours>' + _str_iso_hh + r')'                     +\
                   r'(:?' + r'(?P<gmt_minutes>' + _str_iso_mm + r'))?'

_str_iso_zone = r'((?P<timezone>Z)|'                                          +\
                r'(?P<gmt_sign>[-+])' + _str_iso_zone_hm + r')'

_str_iso_time = _str_iso_hms + r'((?P<gmt_delta>' + _str_iso_zone + r'))?'
_regex_iso_time = re.compile(_str_iso_time)

_regexes = [_regex_iso_time,             # 0
            _regex_h24ms_with_gmt_delta, # 1
            _regex_h24ms_with_timezone,  # 2
            _regex_h12msf_am_pm,         # 3
            _regex_h12ms_am_pm,          # 4
            _regex_h12m_am_pm,           # 5
            _regex_h12_am_pm,            # 6
            _regex_h24msf,               # 7
            _regex_h24ms,                # 8
            _regex_h24m,                 # 9
            _regex_h12m,                 # 10
            #_regex_h24m_no_colon
            #_regex_h24ms_no_colon,
]

# match (), {}, and []
_str_brackets = r'[(){}\[\]]'
_regex_brackets = re.compile(_str_brackets)

_CANDIDATE_FIELDS = ['start', 'end', 'match_text', 'regex']
_Candidate = namedtuple('_Candidate', _CANDIDATE_FIELDS)


###############################################################################
def _has_overlap(a1, b1, a2, b2):
    """
    Determine if intervals [a1, b1) and [a2, b2) overlap at all.
    """

    assert a1 <= b1
    assert a2 <= b2
    
    if b2 <= a1:
        return False
    elif a2 >= b1:
        return False
    else:
        return True

###############################################################################
def _remove_overlap(candidates):
    """
    Given a set of match candidates, resolve into nonoverlapping matches.
    Take the longest match at any given position.

    ASSUMES that the candidate list has been sorted by matching text length,
    from longest to shortest.
    """

    if _TRACE:
        print('called _remove_overlap...')
    
    results = []
    overlaps = []
    indices = [i for i in range(len(candidates))]

    i = 0
    while i < len(indices):

        if _TRACE:
            print('\tstarting indices: {0}'.format(indices))

        index_i = indices[i]
        start_i = candidates[index_i].start
        end_i   = candidates[index_i].end
        len_i   = end_i - start_i

        overlaps.append(i)
        candidate_index = index_i

        j = i+1
        while j < len(indices):
            index_j = indices[j]
            start_j = candidates[index_j].start
            end_j   = candidates[index_j].end
            len_j   = end_j - start_j

            # does candidate[j] overlap candidate[i] at all
            if _has_overlap(start_i, end_i, start_j, end_j):
                if _TRACE:
                    print('\t\t{0} OVERLAPS {1}, lengths {2}, {3}'.
                          format(candidates[index_i].match_text,
                                 candidates[index_j].match_text,
                                 len_i, len_j))
                overlaps.append(j)
                # keep the longest match at any overlap region
                if len_j > len_i:
                    start_i = start_j
                    end_i   = end_j
                    len_i   = len_j
                    candidate_index = index_j
            j += 1

        if _TRACE:
            print('\t\t\twinner: {0}'.
                  format(candidates[candidate_index].match_text))
            print('\t\t\tappending {0} to results'.
                  format(candidates[candidate_index].match_text))
            
        results.append(candidates[candidate_index])

        if _TRACE:
            print('\t\toverlaps: {0}'.format(overlaps))
        
        # remove all overlaps
        new_indices = []
        for k in range(len(indices)):
            if k not in overlaps:
                new_indices.append(indices[k])
        indices = new_indices

        if _TRACE:
            print('\t\tindices after removing overlaps: {0}'.format(indices))
        
        if 0 == len(indices):
            break

        # start over
        i = 0
        overlaps = []

    return results


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

    for regex_index, regex in enumerate(_regexes):
        iterator = regex.finditer(sentence)
        for match in iterator:
            match_text = match.group()
            if _TRACE:
                print('[{0:2}]: MATCH TEXT: ->{1}<-'.
                      format(regex_index, match_text))
            start = match.start()
            end   = match.end()
            candidates.append( _Candidate(start, end, match_text, regex))

    # sort the candidates in descending order of length, which is needed for
    # one-pass overlap resolution later on
    candidates = sorted(candidates, key=lambda x: x.end-x.start, reverse=True)

    if _TRACE:
        print('\tCandidate matches: ')
        index = 0
        for c in candidates:
            print('\t[{0:2}]\t[{1},{2}): {3}'.
                  format(index, c.start, c.end, c.match_text, c.regex))
            index += 1
        print()

    pruned_candidates = _remove_overlap(candidates)

    if _TRACE:
        print('\tcandidates count after overlap removal: {0}'.
              format(len(pruned_candidates)))
        print('Result matches: ')
        for c in pruned_candidates:
            print('\t\t[{0},{1}): {2}'.format(c.start, c.end, c.match_text))
        print()

    for pc in pruned_candidates:

        # used the saved regex to match the saved text again
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
        
        try:
            if match.group('hours') is not None:
                int_hours = int(match.group('hours'))
        except IndexError:
            pass

        try:
            if match.group('minutes') is not None:
                int_minutes = int(match.group('minutes'))
        except IndexError:
            pass

        try:
            if match.group('seconds') is not None:
                int_seconds = int(match.group('seconds'))
        except IndexError:
            pass
    
        try:
            if match.group('frac') is not None:
                # leave as a string; conversion needs to handle leading zeros
                frac_seconds = match.group('frac')[1:]
        except IndexError:
            pass

        try:
            if match.group('am_pm') is not None:
                am_pm = match.group('am_pm')
                if -1 != am_pm.find('a') or -1 != am_pm.find('A'):
                    am_pm = STR_AM
                else:
                    am_pm = STR_PM
        except IndexError:
            pass

        try:
            if match.group('timezone') is not None:
                timezone = match.group('timezone')
                if 'Z' == timezone:
                    timezone = 'UTC'
        except IndexError:
            pass

        try:
            if match.group('gmt_delta') is not None:
                gmt_delta = match.group('gmt_delta')
        except IndexError:
            pass

        if EMPTY_FIELD != gmt_delta:
            match_gmt = _regex_gmt.search(match.group('gmt_delta'))
            if match_gmt:

                try:
                    if match_gmt.group('gmt_sign') is not None:
                        gmt_delta_sign = match_gmt.group('gmt_sign')
                except:
                    pass

                try:
                    if match_gmt.group('gmt_hours') is not None:
                        gmt_delta_hours = int(match_gmt.group('gmt_hours'))
                except:
                    pass

                try:
                    if match_gmt.group('gmt_minutes') is not None:
                        gmt_delta_minutes = int(match_gmt.group('gmt_minutes'))
                except:
                    pass
                    
        meas = TimeValue(pc.match_text, pc.start, pc.end,
                         int_hours, int_minutes, int_seconds,
                         frac_seconds, am_pm, timezone,
                         gmt_delta_sign, gmt_delta_hours,
                         gmt_delta_minutes)
        results.append(meas)

    # sort results to match order of occurrence in sentence
    results = sorted(results, key=lambda x: x.start)
    
    # convert to list of dicts to preserve field names in JSON output
    return json.dumps([r._asdict() for r in results], indent=4)


###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)

