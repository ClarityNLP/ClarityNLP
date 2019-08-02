#!/usr/bin/env python3
"""

OVERVIEW:


The code in this module recognizes dates in a sentence and returns a JSON
result with information on each date found. Various date formats are
supported - see the reference below for examples of the different formats.
This code supports all the listed formats excluding those with roman numerals
for the month.


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
            print(d.text)
            print(d.start)
            print(d.end)
            if df.EMPTY_FIELD != d.day:
                print(d.day)
            etc.

Reference: PHP Date Formats, http://php.net/manual/en/datetime.formats.date.php

"""

import re
import sys
import json
from collections import namedtuple

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
_VERSION_MINOR = 3
_MODULE_NAME   = 'date_finder.py'

# day of the month with optional suffix, such as 7th, 22nd,
_str_dd = r'([0-2]?[0-9]|3[01])\s*(st|nd|rd|th)?'

# two-digit numeric day of the month
_str_DD = r'(0[0-9]|[1-2][0-9]|3[01])'

# months
_str_m = r'(january|february|march|april|may|june|july|august|september|'    +\
         r'october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|'   +\
         r'sept|oct|nov|dec)'

# convert textual months to int
month_dict = {
    'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
    'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7,
    'august': 8, 'aug': 8, 'september': 9, 'sept': 9, 'sep': 9,
    'october': 10, 'oct': 10, 'november': 11, 'nov': 11,
    'december': 12, 'dec': 12
}

# month abbreviations
_str_M = r'(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)'

# numeric month
_str_mm = r'0?[0-9]|1[0-2]'

# two digit month
_str_MM = r'0[0-9]|1[0-2]'

# one and four digit year (3 is invalid)
_str_y = r'[0-9]{1,4}'

# two digit year
_str_yy = r'[0-9]{2}'

# four digit year
_str_YY = r'[0-9]{4}'

# American month, day, and year
_str_american_mdy = r'\b(?P<month>' + _str_mm + r')' + r'/' +\
                    r'(?P<day>' + _str_dd + r')' + r'/'     +\
                    r'(?P<year>' + _str_y + r')\b'
_regex_1 = re.compile(_str_american_mdy, re.IGNORECASE)

# four-digit year, month, day separated by forward slash
_str_ymd_fwd_slash = r'\b(?P<year>' + _str_YY + r')' + r'/' +\
                     r'(?P<month>' + _str_mm + r')' + r'/'  +\
                    r'(?P<day>' + _str_dd + r')\b'
_regex_2 = re.compile(_str_ymd_fwd_slash, re.IGNORECASE)

# day, month, and four-digit year with other separators
_str_dmy4 = r'\b(?P<day>' + _str_dd + r')' + r'[-.\t]'      +\
            r'(?P<month>' + _str_mm + r')' + r'[-.\t]'      +\
            r'(?P<year>' + _str_YY + r')\b'
_regex_3 = re.compile(_str_dmy4, re.IGNORECASE)

# year, month, day with dashes
_str_ymd_dash = r'\b(?P<year>' + _str_y + r')' + r'-'       +\
                r'(?P<month>' + _str_mm + r')' + r'-'       +\
                r'(?P<day>' + _str_dd + r')\b'
_regex_4 = re.compile(_str_ymd_dash, re.IGNORECASE)

# day, month, and two-digit year with dots or tabs
_str_dmy2 = r'\b(?P<day>' + _str_dd + r')' + r'[.\t]'       +\
            r'(?P<month>' + _str_mm + r')' + r'[.]'         +\
            r'(?P<year>' + _str_yy + r')\b'
_regex_5 = re.compile(_str_dmy2, re.IGNORECASE)

# day, textual month and year
_str_dtmy = r'\b(?P<day>' + _str_dd + r')' + r'[-.\t ]*'    +\
            r'(?P<month>' + _str_m + r')' + r'[-.\t ]*'     +\
            r'(?P<year>' + _str_y + r')\b'
_regex_6 = re.compile(_str_dtmy, re.IGNORECASE)

# textual month, day, and year
_str_tmdy = r'\b(?P<month>' + _str_m + r')' + r'[-.\t ]*'             +\
            r'(?P<day>' + _str_dd + r')' + r'(st|nd|rd|th|[-,.\t ])+' +\
            r'(?P<year>' + _str_y + r')\b'
_regex_7 = re.compile(_str_tmdy, re.IGNORECASE)

# abbreviated month, day, and year
_str_mdy = r'\b(?P<month>' + _str_M + r')' + r'-'  +\
           r'(?P<day>' + _str_DD + r')' + r'-'     +\
           r'(?P<year>' + _str_y + r')\b'
_regex_8 = re.compile(_str_mdy, re.IGNORECASE)

# year, abbreviated month, day
_str_ymd = r'\b(?P<year>' + _str_y + r')' + r'-'   +\
           r'(?P<month>' + _str_M + r')' + r'-'    +\
           r'(?P<day>' + _str_DD + r')\b'
_regex_9 = re.compile(_str_ymd, re.IGNORECASE)

# American month and day, e.g. 5/12, 10/27
_str_american_md = r'\b(?P<month>' + _str_mm + r')' + r'/' +\
                   r'(?P<day>' + _str_dd + r')\b'
_regex_10 = re.compile(_str_american_md, re.IGNORECASE)

# textual month and day
_str_tmd = r'\b(?P<month>' + _str_m + r')' + r'[-.\t ]*'               +\
           r'(?P<day>' + _str_dd + r')' + r'(st|nd|rd|th|[-,.\t ])*\b'
_regex_11 = re.compile(_str_tmd, re.IGNORECASE)

# day and textual month
_str_dtm = r'\b(?P<day>' + _str_dd + r')' + r'[-.\t ]*'   +\
           r'(?P<month>' + _str_m + r')\b'
_regex_12 = re.compile(_str_dtm, re.IGNORECASE)

# GNU four-digit year and month
_str_gnu_ym = r'\b(?P<year>' + _str_YY + r')' + r'-'      +\
              r'(?P<month>' + _str_mm + r')\b'
_regex_13 = re.compile(_str_gnu_ym, re.IGNORECASE)

# textual month and four-digit year
_str_tmy4 = r'\b(?P<month>' + _str_m + r')' + r'[-.\t ]*' +\
            r'(?P<year>' + _str_YY + r')\b'
_regex_14 = re.compile(_str_tmy4, re.IGNORECASE)

# four-digit year and textual month
_str_y4tm = r'\b(?P<year>' + _str_YY + r')' + r'[-.\t ]*' +\
            r'(?P<month>' + _str_m + r')\b'
_regex_15 = re.compile(_str_y4tm, re.IGNORECASE)

# year only
_str_year = r'\b(?P<year>' + _str_YY + r')\b'
_regex_16 = re.compile(_str_year, re.IGNORECASE)

# textual month only
_str_month = r'\b(?P<month>' + _str_m + r')\.?\b'
_regex_17 = re.compile(_str_month, re.IGNORECASE)

######   ISO 8601 formats  #####

# eight-digit year, month, day
_str_iso_8 = r'\b(?P<year>' + _str_YY + r')'  +\
             r'(?P<month>' + _str_MM + r')'   +\
             r'(?P<day>' + _str_DD + r')\b'
_regex_iso_1 = re.compile(_str_iso_8)

# optional sign, four-digit year, two-digit month, two-digit day, dashes
_str_iso_s4y2m2d = r'\b(?P<sign>[-+]?)'                     +\
                   r'(?P<year>' + _str_YY + r')' + r'-'     +\
                   r'(?P<month>' + _str_MM + r')' + r'-'    +\
                   r'(?P<day>' + _str_DD + r')\b'
_regex_iso_2 = re.compile(_str_iso_s4y2m2d)

# four-digit year, two-digit month, two-digit day, fwd slashes
_str_iso_4y2m2d = r'\b(?P<year>' + _str_YY + r')' + r'/'    +\
                  r'(?P<month>' + _str_MM + r')' + r'/'     +\
                  r'(?P<day>' + _str_DD + r')\b'
_regex_iso_3 = re.compile(_str_iso_4y2m2d)

# two-digit year, two-digit month, two-digit day, dashes
_str_iso_2y2m2d = r'\b(?P<year>' + _str_yy + r')' + r'-'    +\
                  r'(?P<month>' + _str_MM + r')' + r'-'     +\
                  r'(?P<day>' + _str_DD + r')\b'
_regex_iso_4 = re.compile(_str_iso_2y2m2d)

# all date regexes
_regexes = [
    _regex_iso_1,
    _regex_iso_2,
    _regex_iso_3,
    _regex_iso_4,
    _regex_1,
    _regex_2,
    _regex_3,
    _regex_4,
    _regex_5,
    _regex_6,
    _regex_7,
    _regex_8,
    _regex_9,
    _regex_10,
    _regex_11,
    _regex_12,
    _regex_13,
    _regex_14,
    _regex_15,
    _regex_16,
    _regex_17
]

# match (), {}, and []
_str_brackets = r'[(){}\[\]]'
_regex_brackets = re.compile(_str_brackets)


###############################################################################
def _has_overlap(spans, start, end):
    """
    Check the match object for overlap with previous matches.
    Returns True if overlaps a previous match, False if not.
    """

    for start_i, end_i in spans:

        # new match is entirely contained within an existing match
        if start >= start_i and end <= end_i:
            return True

    return False


###############################################################################
def _resolve_candidates(candidates):
    """
    Given a list of candidate DateValue objects, resolve into
    non-overlapping dates.
    """

    if 0 == len(candidates):
        return []

    candidates = sorted(candidates, key=lambda x: x.start)

    results = [candidates[0]]
    prev_end = candidates[0].end
    for i in range(1, len(candidates)):
        start = candidates[i].start
        if start > prev_end:
            results.append(candidates[i])
            prev_end = candidates[i].end

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

    Find dates in the sentence by attempting to match all regexes. Avoid
    matching sub-expressions of already-matched strings. Returns a JSON
    array containing info on each date found.

    """

    spans = []  # [start, end) character offsets of each match
    results = []  # DateValue namedtuple results
    candidates = []  # potential matches, need overlap resolution to confirm

    original_sentence = sentence
    sentence = _clean_sentence(sentence)

    for regex in _regexes:
        iterator = regex.finditer(sentence)
        for match in iterator:
            match_text = match.group().strip()
            start = match.start()
            end = start + len(match_text)

            # check to see if not contained within a previous match
            if not _has_overlap(spans, start, end):

                int_year  = EMPTY_FIELD
                int_month = EMPTY_FIELD
                int_day   = EMPTY_FIELD

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
                    text = match_text,
                    start = start,
                    end = end,
                    year = int_year,
                    month = int_month,
                    day = int_day)
                
                candidates.append(meas)
                spans.append((start, end))

    candidates = _resolve_candidates(candidates)
    results.extend(candidates)

    # convert to list of dicts to preserve field names in JSON output
    return json.dumps([r._asdict() for r in results], indent=4)


###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
def show_help():
    print(get_version())
    print("""
    USAGE: python3 ./date_finder.py -s <sentence> [-hvz]

    OPTIONS:

        -s, --sentence <quoted string>  Sentence to be processed.

    FLAGS:

        -h, --help                      Print this information and exit.
        -v, --version                   Print version information and exit.
        -z, --test                      Disable -s option and use internal test sentences.

    """)


###############################################################################
if __name__ == '__main__':

    TEST_SENTENCES = [
        'The date 20121128 is in iso_8 format.',
        'The dates 2012/11/28 and 2012/03/15 are in iso_YYYYMMDD format.',
        'The dates 12-11-28 and 12-03-15 are in iso_YYMMDD format.',
        'The date +2012-11-28 is in iso_sYYYYMMDD format.',
        'The dates 11/28/2012, 1/3/2012, and 2/17/15 are in American month/day/year format.',
        'The dates 28-11-2012, 3-1-2012, and 17.2.2015 are in dmYYYY format.',
        'The dates 2008-6-30, 78-12-22, and 8-6-21 are in year-month-day format.',
        'The dates 30.6.08 and 22\t12.78 are in dmYY format.',
        'The dates 30-June 2008, 22DEC78, and 14 MAR 1879 are in dtmy format.',
        'The dates July 1st, 2008, April 17, 1790, and May.9,78 are in tmdy format.',
        'The dates May-09-78, Apr-17-1790, and Dec-12-2005 are in month-day-year format.',
        'The dates 78-Dec-22, 1814-MAY-17, and 05-Jun-24 are in ymd format.',
        'The dates 5/12, 10/27, and 5/5 are in American month/day format.',
        'The dates "July 1st,", Apr 17, and May.9 are in tmd format.',
        'The dates 1 July, 17 Apr, and 9.May are in dtm format.',
        'The dates 2008-6, 2008-06, and 1978-12 are in GNU ym format.',
        'The dates June 2008, DEC1978, March 1879 are in tmy4 format.',
        'The dates 2008 June, 1978-12, and 1879.MARCH are in y4tm format.',
        'The dates 2004, 1968, 1492 are individual years.',
        'The dates January, Feb., Sept. and December are individual months.'
    ]

    optparser = optparse.OptionParser(add_help_option=False)
    optparser.add_option('-s', '--sentence', action='store', dest='sentence')
    optparser.add_option('-v', '--version', action='store_true', dest='get_version')
    optparser.add_option('-h', '--help', action='store_true', dest='show_help', default=False)
    optparser.add_option('-z', '--test', action='store_true', dest='use_test_sentences', default=False)

    opts, other = optparser.parse_args(sys.argv)

    sentence = opts.sentence
    use_test_sentences = opts.use_test_sentences

    if not use_test_sentences and 1 == len(sys.argv):
        show_help()
        sys.exit(0)

    if opts.show_help:
        show_help()
        sys.exit(0)

    if opts.get_version:
        print(get_version())
        sys.exit(0)

    if not sentence and not use_test_sentences:
        print('A sentence must be specified on the command line.')
        sys.exit(-1)

    sentences = []
    if use_test_sentences:
        sentences = TEST_SENTENCES
    else:
        sentences.append(sentence)

    # main loop
    for sentence in sentences:

        if use_test_sentences:
            print(sentence)

        # find the dates and print JSON results to stdout
        json_result = run(sentence)
        print(json_result)
