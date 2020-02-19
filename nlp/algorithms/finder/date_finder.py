#!/usr/bin/env python3
"""

OVERVIEW:


The code in this module recognizes date expressions in a sentence and returns
a JSON result with information on each date expression that it finds. The
supported date formats are listed next, using the abbreviations (see the
reference below):

    dd: one or two-digit day of the month with optional suffix
        (such as 7th, 22nd, etc.)
    DD: two-digit day of the month
     m: name of the month
     M: month abbreviation (jan, feb. etc.)
    mm: one or two-digit month
    MM: two-digit month
     y: two or four-digit year
    yy: two-digit year
  YYYY: four-digit year
     ?: optional

1. ISO 8601 Formats

    iso_8:        YYYYMMDD
    iso_s422:     [-+]?YYYY-MM-DD
    iso_422:      YYYY/MM/DD
    iso_222:      YY-MM-DD
    iso_datetime: YYYY-MM-DDTHH:MM:SS.ffffff

2. Other Formats (illustrated with the date of the first Moon landing):

    mm/dd/YYYY (American convention)    07/20/1969
    YYYY/mm/dd                          1969/7/20, 1969/07/20
    dd-mm-YYYY, dd.mm.YYYY              20-07-1969, 20.7.1969
    y-mm-dd                             1969-7-20, 1969-07-20, 69-7-20
    dd.mm.yy                            20.7.69, 20.07.69
    dd-m-y, ddmy, dd m y                20-JULY-69, 20JULY69, 20 July 1969
    m-dd-y, m.dd.y, mddy, m dd, y       20-July 1969, 20JULY1969, 20 July, 1969
    M-DD-y                              Jul-20-1969, Jul-20-69
    y-M-DD                              69-Jul-20, 1969-Jul-20
    mm/dd                               7/20, 07/20
    m-dd, m.dd, m dd                    July 20, July 20th, July-20
    dd-m, dd.m, dd m                    20-July, 20.July, 20 July
    YYYY-mm                             1969-07, 1969-7
    m-YYYY, m.YYYY, m YYYY              July-1969, July.1969, July 1969
    YYYY-m, YYYY.m, YYYY m              1969-July, 1969.July, 1969 July
    YYYY                                1969
    m                                   July

3. Anonymized formats (MIMIC)

    [**YYYY-mm-dd**]                    [**1969-7-20**]
    [**YYYY**]                          [**1969**]
    [**mm-dd**]                         [**7-20**]

OUTPUT:


The set of JSON fields in the output for each date includes:

        text     matching text
        start    starting character offset of the matching text
        end      final character offset of the matching text + 1
        year     integer year
        month    integer month [1, 12]
        day      integer day   [1, 31]

Any missing fields will have the value EMPTY_FIELD. All JSON results will
contain an identical number of fields.

All date recognition is case-insensitive.

JSON results are written to stdout.


USAGE:


To use this code as an imported module, add the following lines to the
import list in the importing module:

        import json
        import date_finder as df

To find dates in a sentence and capture the JSON result:

        json_string = df.run(sentence)

To unpack the JSON results:

        json_data = json.loads(json_string)
        date_results = [df.DateValue(**m) for m in json_data]

        for d in date_results:
            log(d.text)
            log(d.start)
            log(d.end)
            if df.EMPTY_FIELD != d.day:
                log(d.day)
            etc.

Reference: PHP Date Formats, http://php.net/manual/en/datetime.formats.date.php

"""

import re
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

DATE_VALUE_FIELDS = [
    'text',
    'start',
    'end',
    'year',
    'month',
    'day'
]
DateValue = namedtuple('DateValue', DATE_VALUE_FIELDS)

# set default value of all fields to EMPTY_FIELD
DateValue.__new__.__defaults__ = (EMPTY_FIELD,) * len(DateValue._fields)


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 7
_MODULE_NAME   = 'date_finder.py'

# set to True to enable debug output
_TRACE = False

# day of the month with optional suffix, such as 7th, 22nd,
_str_dd = r'([0-2]?[0-9]|3[01])\s*(st|nd|rd|th)?'

# two-digit numeric day of the month
_str_DD = r'(0[0-9]|[1-2][0-9]|3[01])'

# months
_str_m = r'(january|february|march|april|may|june|july|august|september|'  +\
    r'october|november|december|jan|feb|mar|apr|jun|jul|aug|sept|sep|'     +\
    r'oct|nov|dec)'

# convert textual months to int
month_dict = {
    'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
    'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7,
    'august': 8, 'aug': 8, 'september': 9, 'sept': 9, 'sep': 9,
    'october': 10, 'oct': 10, 'november': 11, 'nov': 11,
    'december': 12, 'dec': 12
}

# month abbreviations
_str_M = r'(jan|feb|mar|apr|may|jun|jul|aug|sept|sep|oct|nov|dec)'

# numeric month
_str_mm = r'0?[0-9]|1[0-2]'

# two digit month
_str_MM = r'0[0-9]|1[0-2]'

# two or four digit year
_str_y = r'[0-9]{4}|[0-9]{2}'

# two digit year
_str_yy = r'[0-9]{2}'

# four digit year
_str_YY = r'[0-9]{4}'

# American month, day, and year
_str_american_mdy = r'(?<![-\d/.])(?P<month>' + _str_mm + r')' + r'/'   +\
                    r'(?P<day>' + _str_dd + r')' + r'/'                 +\
                    r'(?P<year>' + _str_y + r')\b'
_regex_1 = re.compile(_str_american_mdy, re.IGNORECASE)

# four-digit year, month, day separated by forward slash
_str_ymd_fwd_slash = r'(?<![-\d/.])(?P<year>' + _str_YY + r')' + r'/'   +\
                     r'(?P<month>' + _str_mm + r')' + r'/'              +\
                     r'(?P<day>' + _str_dd + r')\b'
_regex_2 = re.compile(_str_ymd_fwd_slash, re.IGNORECASE)

# day, month, and four-digit year with other separators
_str_dmy4 = r'(?<![-\d/.])(?P<day>' + _str_dd + r')' + r'[-.\t]'        +\
            r'(?P<month>' + _str_mm + r')' + r'[-.\t]'                  +\
            r'(?P<year>' + _str_YY + r')\b'
_regex_3 = re.compile(_str_dmy4, re.IGNORECASE)

# year, month, day with dashes
_str_ymd_dash = r'(?<![-\d/.])(?P<year>' + _str_y + r')' + r'-'         +\
                r'(?P<month>' + _str_mm + r')' + r'-'                   +\
                r'(?P<day>' + _str_dd + r')\b'
_regex_4 = re.compile(_str_ymd_dash, re.IGNORECASE)

# day, month, and two-digit year with dots or tabs
_str_dmy2 = r'(?<![-\d/.])(?P<day>' + _str_dd + r')' + r'[.\t]'         +\
            r'(?P<month>' + _str_mm + r')' + r'[.]'                     +\
            r'(?P<year>' + _str_yy + r')\b'
_regex_5 = re.compile(_str_dmy2, re.IGNORECASE)

# day, textual month and year (space char is a valid separator)
_str_dtmy = r'(?<![-\d/.])(?P<day>' + _str_dd + r')' + r'[-.\t ]*'      +\
            r'(?P<month>' + _str_m + r')' + r'[-.\t ]*'                 +\
            r'(?P<year>' + _str_y + r')\b'
_regex_6 = re.compile(_str_dtmy, re.IGNORECASE)

# textual month, day, and year
_str_tmdy = r'(?<![-\d/.])(?P<month>' + _str_m + r')' + r'[-.\t ]*'     +\
            r'(?P<day>' + _str_dd + r')' + r'(st|nd|rd|th|[-,.\t ])+'   +\
            r'(?P<year>' + _str_y + r')\b'
_regex_7 = re.compile(_str_tmdy, re.IGNORECASE)

# abbreviated month, day, and year
_str_mdy = r'(?<![-\d/.])(?P<month>' + _str_M + r')' + r'-'             +\
           r'(?P<day>' + _str_DD + r')' + r'-'                          +\
           r'(?P<year>' + _str_y + r')\b'
_regex_8 = re.compile(_str_mdy, re.IGNORECASE)

# year, abbreviated month, day
_str_ymd = r'(?<![-\d/.])(?P<year>' + _str_y + r')' + r'-'              +\
           r'(?P<month>' + _str_M + r')' + r'-'                         +\
           r'(?P<day>' + _str_DD + r')\b'
_regex_9 = re.compile(_str_ymd, re.IGNORECASE)

# American month and day, e.g. 5/12, 10/27
_str_american_md = r'(?<![-\d/.])(?P<month>' + _str_mm + r')' + r'/'    +\
                   r'(?P<day>' + _str_dd + r')\b'
_regex_10 = re.compile(_str_american_md, re.IGNORECASE)

# textual month and day
_str_tmd = r'(?<!\[-\d/.])(?P<month>' + _str_m + r')' + r'[-.\t ]*'     +\
           r'(?P<day>' + _str_dd + r')' + r'(st|nd|rd|th|[-.\t ])*\b'
_regex_11 = re.compile(_str_tmd, re.IGNORECASE)

# day and textual month
_str_dtm = r'(?<![-\d/.])(?P<day>' + _str_dd + r')' + r'[-.\t ]*'       +\
           r'(?P<month>' + _str_m + r')\b'
_regex_12 = re.compile(_str_dtm, re.IGNORECASE)

# GNU four-digit year and month
_str_gnu_ym = r'(?<![-\d/.])(?P<year>' + _str_YY + r')' + r'-'          +\
              r'(?P<month>' + _str_mm + r')(?![-])\b'
_regex_13 = re.compile(_str_gnu_ym, re.IGNORECASE)

# textual month and four-digit year
_str_tmy4 = r'(?<![-\d/.])(?P<month>' + _str_m + r')' + r'[-.\t ]*'     +\
            r'(?P<year>' + _str_YY + r')\b'
_regex_14 = re.compile(_str_tmy4, re.IGNORECASE)

# four-digit year and textual month
_str_y4tm = r'(?<![-\d/.])(?P<year>' + _str_YY + r')' + r'[-.\t ]*'     +\
            r'(?P<month>' + _str_m + r')\b'
_regex_15 = re.compile(_str_y4tm, re.IGNORECASE)

# year only
_str_year = r'(?<![-+\d/.])(?P<year>' + _str_YY + r'(?![-]))\b'
_regex_16 = re.compile(_str_year, re.IGNORECASE)

# textual month only
_str_month = r'(?<![-\d/.])(?P<month>' + _str_m + r')\.?\b'
_regex_17 = re.compile(_str_month, re.IGNORECASE)

######   ISO 8601 formats  #####

# eight-digit year, month, day
_str_iso_8 = r'(?<![-\d/.])(?P<year>' + _str_YY + r')'                  +\
             r'(?P<month>' + _str_MM + r')'                             +\
             r'(?P<day>' + _str_DD + r')\b'
_regex_iso_1 = re.compile(_str_iso_8)

# optional sign, four-digit year, two-digit month, two-digit day, dashes
_str_iso_s4y2m2d = r'(?P<sign>[-+]?)'                                   +\
                   r'(?<![\d/.])(?P<year>' + _str_YY + r')' + r'-'      +\
                   r'(?P<month>' + _str_MM + r')' + r'-'                +\
                   r'(?P<day>' + _str_DD + r'(?!\d))'
_regex_iso_2 = re.compile(_str_iso_s4y2m2d)

# four-digit year, two-digit month, two-digit day, fwd slashes
_str_iso_4y2m2d = r'(?<![-\d/.])(?P<year>' + _str_YY + r')' + r'/'      +\
                  r'(?P<month>' + _str_MM + r')' + r'/'                 +\
                  r'(?P<day>' + _str_DD + r'(?!\d))'
_regex_iso_3 = re.compile(_str_iso_4y2m2d)

# two-digit year, two-digit month, two-digit day, dashes
_str_iso_2y2m2d = r'(?<![-\d/.])(?P<year>' + _str_yy + r')' + r'-'      +\
                  r'(?P<month>' + _str_MM + r')' + r'-'                 +\
                  r'(?P<day>' + _str_DD + r'(?!\d))'
_regex_iso_4 = re.compile(_str_iso_2y2m2d)

# ISO datetime format: YYYY-MM-DDTHH:MM:SS.ffffff
# fractional seconds are optional
_str_iso_datetime = _str_iso_s4y2m2d + r'T\d\d:\d\d:\d\d(\.\d+)?'
_regex_iso_datetime = re.compile(_str_iso_datetime)

###### Anonymized formats such as [**2984-12-15**] ######

_str_anon_1 = r'\[\*\*(?P<year>\d\d\d\d)\-(?P<month>\d\d?)\-(?P<day>\d\d?)\*\*\]'
_regex_anon_1 = re.compile(_str_anon_1)

_str_anon_2 = r'\[\*\*(?P<year>\d\d\d\d)\*\*\]'
_regex_anon_2 = re.compile(_str_anon_2)

_str_anon_3 = r'\[\*\*(?P<month>\d\d?)\-(?P<day>\d\d?)\*\*\]'
_regex_anon_3 = re.compile(_str_anon_3)

# all date regexes
_regexes = [
    _regex_iso_datetime, # 0
    _regex_iso_1,        # 1
    _regex_iso_2,        # 2
    _regex_iso_3,        # 3
    _regex_iso_4,        # 4
    _regex_1,            # 5
    _regex_2,            # 6
    _regex_3,            # 7
    _regex_4,            # 8
    _regex_5,            # 9
    _regex_6,            # 10
    _regex_7,            # 11
    _regex_8,            # 12
    _regex_9,            # 13
    _regex_10,           # 14
    _regex_11,           # 15
    _regex_12,           # 16
    _regex_13,           # 17
    _regex_14,           # 18
    _regex_15,           # 19
    _regex_16,           # 20
    _regex_17,           # 21
    _regex_anon_1,       # 22
    _regex_anon_2,       # 23
    _regex_anon_3        # 24
]

# index of the ISO datetime regex in the _regexes array
_ISO_DATETIME_REGEX_INDEX = 0

# match () and {} (not [] since those are used in anonymized dates)
_str_brackets = r'[(){}]'
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

    Find dates in the sentence by attempting to match all regexes. Avoid
    matching sub-expressions of already-matched strings. Returns a JSON
    array containing info on each date found.

    """

    results = []     # DateValue namedtuple results
    candidates = []  # potential matches, need overlap resolution to confirm

    original_sentence = sentence
    sentence = _clean_sentence(sentence)

    if _TRACE:
        log('(DF) original: {0}'.format(original_sentence))
        log('(DF)  cleaned: {0}'.format(sentence))
    
    for regex_index, regex in enumerate(_regexes):
        iterator = regex.finditer(sentence)
        for match in iterator:
            match_text = match.group().strip()
            if _ISO_DATETIME_REGEX_INDEX == regex_index:
                # extract only the date portion
                t_pos = match_text.find('T')
                assert -1 != t_pos
                match_text = match_text[:t_pos]
            start = match.start()
            end = start + len(match_text)
            candidates.append(overlap.Candidate(start, end, match_text, regex))

            if _TRACE:
                log('\t[{0:2}]: MATCH TEXT: ->{1}<-'.
                      format(regex_index, match_text))

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
                
        # use the saved regex to match the saved text again
        if _regex_iso_datetime == pc.regex:
            # match only the date portion
            match = _regex_iso_2.match(pc.match_text)
        else:
            match = pc.regex.match(pc.match_text)
        assert match
        
        int_year  = EMPTY_FIELD
        int_month = EMPTY_FIELD
        int_day   = EMPTY_FIELD

        if _TRACE:
            log('\t     matched: "{0}"'.format(match.group()))
            log('\t\t groupdict: {0}'.format(match.groupdict()))
            log('\t\tmatch_text: "{0}"'.format(pc.match_text))
            
        for k,v in match.groupdict().items():
            if v is None:
                continue
            if 'year' == k:
                int_year = int(v)
            elif 'month' == k:
                # convert textual months to int
                if re.search('\D', v):
                    int_month = month_dict[v.strip().lower()]
                else:
                    int_month = int(v)
            elif 'day' == k:
                # strip text from 1st, 3rd, etc.
                if re.search('\D', v):
                    int_day = int(re.search('\d+', v).group())
                else:
                    int_day = int(v)

        meas = DateValue(
            text = pc.match_text,
            start = pc.start,
            end = pc.end,
            year = int_year,
            month = int_month,
            day = int_day)

        results.append(meas)

    # sort results to match order in sentence
    results = sorted(results, key=lambda x: x.start)

    # convert to list of dicts to preserve field names in JSON output
    return json.dumps([r._asdict() for r in results], indent=4)


###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)

