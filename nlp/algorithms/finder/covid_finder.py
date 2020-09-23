#!/usr/bin/env python3
"""

This is a module for finding and extracting the number of COVID-19 cases,
hospitalizations, and deaths from text scraped from the Internet.

"""

import os
import re
import sys
import json
import argparse
from collections import namedtuple

# try:
#     # for normal operation via NLP pipeline
#     from algorithms.finder.date_finder import run as \
#         run_date_finder, DateValue, EMPTY_FIELD as EMPTY_DATE_FIELD
#     from algorithms.finder import finder_overlap as overlap
    
# except:
#     this_module_dir = sys.path[0]
#     pos = this_module_dir.find('/nlp')
#     if -1 != pos:
#         nlp_dir = this_module_dir[:pos+4]
#         finder_dir = os.path.join(nlp_dir, 'algorithms', 'finder')
#         sys.path.append(finder_dir)    
#     from date_finder import run as run_date_finder, \
#         DateValue, EMPTY_FIELD as EMPTY_DATE_FIELD
#     import finder_overlap as overlap

if __name__ == '__main__':
    # for interactive testing only
    match = re.search(r'nlp/', sys.path[0])
    if match:
        nlp_dir = sys.path[0][:match.end()]
        sys.path.append(nlp_dir)
    else:
        print('\n*** covid_finder.py: nlp dir not found ***\n')
        sys.exit(0)

from date_finder import run as run_date_finder, \
    DateValue, EMPTY_FIELD as EMPTY_DATE_FIELD
from time_finder import run as run_time_finder, \
    TimeValue, EMPTY_FIELD as EMPTY_TIME_FIELD
import finder_overlap as overlap    


# default value for all fields
EMPTY_FIELD = None


COVID_TUPLE_FIELDS = [
    'sentence',
    'case_start',      # char offset for start of case match
    'case_end',        # char offset for end of case match
    'hosp_start',       
    'hosp_end',
    'death_start',
    'death_end',
    'text_case',       # matching text for case counts
    'text_hosp',       # matching text for hospitalization counts
    'text_death',      # matching text for death counts
    'value_case',      # number of reported cases
    'value_hosp',      # number of reported hospitalizations
    'value_death',     # number of reported deaths
]
CovidTuple = namedtuple('CovidTuple', COVID_TUPLE_FIELDS)


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 4
_MODULE_NAME   = 'covid_finder.py'

# set to True to enable debug output
_TRACE = False

_STR_THOUSAND = 'thousand'
_STR_MILLION  = 'million'

# throwaway words
_THROWAWAY_SET = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your',
    'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she',
    'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
    'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
    'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
    'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of',
    'at', 'by', 'for', 'with', 'against', 'between', 'into', 'through',
    'during', 'before', 'after', 'above', 'below', 'from', 'up', 'down',
    'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
    'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any',
    'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
    'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can',
    'will', 'just', 'dont', 'should', 'shouldve', 'now', 'arent', 'couldnt',
    'didnt', 'doesnt', 'hadnt', 'hasnt', 'havent', 'isnt', 'shouldnt',
    'wasnt', 'werent', 'wont', 'wouldnt'
}

# a word, possibly hyphenated or abbreviated
_str_word = r'[-a-z]+\.?\s?'

# nongreedy word captures
_str_words = r'(' + _str_word + r'){0,5}?'
_str_one_or_more_words = r'(' + _str_word + r'){1,5}?'

# textual numbers and related regexes
_str_tnum_digit = r'\b(one|two|three|four|five|six|seven|eight|nine|zero)'
_str_tnum_10s  = r'\b(ten|eleven|twelve|(thir|four|fif|six|seven|eight|nine)teen)'
_str_tnum_20s  = r'\b(twenty[-\s]?' + _str_tnum_digit + r'|twenty)'
_str_tnum_30s  = r'\b(thirty[-\s]?' + _str_tnum_digit + r'|thirty)'
_str_tnum_40s  = r'\b(forty[-\s]?' + _str_tnum_digit + r'|forty)'
_str_tnum_50s  = r'\b(fifty[-\s]?' + _str_tnum_digit + r'|fifty)'
_str_tnum_60s  = r'\b(sixty[-\s]?' + _str_tnum_digit + r'|sixty)'
_str_tnum_70s  = r'\b(seventy[-\s]?' + _str_tnum_digit + r'|seventy)'
_str_tnum_80s  = r'\b(eighty[-\s]?' + _str_tnum_digit + r'|eighty)'
_str_tnum_90s  = r'\b(ninety[-\s]?' + _str_tnum_digit + r'|ninety)'
_str_tnum_100s = _str_tnum_digit + r'[-\s]hundred[-\s](and[-\s])?' +\
    r'(' +\
    _str_tnum_90s + r'|' + _str_tnum_80s + r'|' + _str_tnum_70s + r'|' +\
    _str_tnum_60s + r'|' + _str_tnum_50s + r'|' + _str_tnum_40s + r'|' +\
    _str_tnum_30s + r'|' + _str_tnum_20s + r'|' + _str_tnum_20s + r'|' +\
    _str_tnum_10s + r'|' + _str_tnum_digit +\
    r')?'
_str_tnum = r'(' +\
    _str_tnum_100s + r'|' + _str_tnum_90s + r'|' + _str_tnum_80s + r'|' +\
    _str_tnum_70s +  r'|' + _str_tnum_60s + r'|' + _str_tnum_50s + r'|' +\
    _str_tnum_40s +  r'|' + _str_tnum_30s + r'|' + _str_tnum_20s + r'|' +\
    _str_tnum_10s +  r'|' + _str_tnum_digit +\
    r')(?!\-)'

_regex_tnum_digit = re.compile(_str_tnum_digit)
_regex_tnum_10s   = re.compile(_str_tnum_10s)
_regex_tnum_20s   = re.compile(_str_tnum_20s)
_regex_tnum_30s   = re.compile(_str_tnum_30s)
_regex_tnum_40s   = re.compile(_str_tnum_40s)
_regex_tnum_50s   = re.compile(_str_tnum_50s)
_regex_tnum_60s   = re.compile(_str_tnum_60s)
_regex_tnum_70s   = re.compile(_str_tnum_70s)
_regex_tnum_80s   = re.compile(_str_tnum_80s)
_regex_tnum_90s   = re.compile(_str_tnum_90s)
_regex_tnum_100s  = re.compile(_str_tnum_100s)
_regex_hundreds   = re.compile(_str_tnum_digit + r'[-\s]?hundred[-\s]?', re.IGNORECASE)

# used for conversions from tnum to int
_tnum_to_int_map = {
    'one':1, 'two':2, 'three':3, 'four':4, 'five':5, 'six':6, 'seven':7,
    'eight':8, 'nine':9, 'ten':10, 'eleven':11, 'twelve':12, 'thirteen':13,
    'fourteen':14, 'fifteen':15, 'sixteen':16, 'seventeen':17, 'eighteen':18,
    'nineteen':19, 'twenty':20, 'thirty':30, 'forty':40, 'fifty':50,
    'sixty':60, 'seventy':70, 'eighty':80, 'ninety':90,
    'zero':0,
}

# enumerations
# 'no' is needed for "no new cases" and similar
_str_enum = r'(first|second|third|fourth|fifth|sixth|seventh|eighth|' +\
    r'ninth|tenth|eleventh|twelfth|'                                  +\
    r'(thir|four|fif|six|seven|eight|nine)teenth|'                    +\
    r'1[0-9]th|[2-9]0th|[4-9]th|3rd|2nd|1st|'                         +\
    r'(twen|thir|for|fif|six|seven|eigh|nine)tieth)'

# used for conversions from enum to int
_enum_to_int_map = {
    'zeroth':0,
    'first':1, '1st':1, 'second':2, '2nd':2, 'third':3, '3rd':3,
    'fourth':4, '4th':4, 'fifth':5, '5th':5, 'sixth':6, '6th':6,
    'seventh':7, '7th':7, 'eighth':8, '8th':8, 'ninth':9, '9th':9,
    'tenth':10, '10th':10, 'eleventh':11, '11th':11, 'twelfth':12, '12th':12,
    'thirteenth':13, '13th':13, 'fourteenth':14, '14th':14,
    'fifteenth':15, '15th':15, 'sixteenth':16, '16th':16,
    'seventeenth':17, '17th':17, 'eighteenth':18, '18th':18,
    'ninenteenth':19, '19th':19, 'twentieth':20, '20th':20,
    'thirtieth':30, '30th':30, 'fortieth':40, '40th':40,
    'fiftieth':50, '50th':50, 'sixtieth':60, '60th':60,
    'seventieth':70, '70th':70, 'eightieth':80, '80th':80,
    'ninetieth':90, '90th':90,
}

# integers, possibly including commas
# do not capture numbers in phrases such as "in their 90s", etc
_str_int = r'(?<!covid)(?<!covid-)(?<!\d)(\d{1,3}(,\d{3})+|(?<![,\d])\d+(?!\d)(?!\'?s))'

# find numbers such as 3.4 million, 4 thousand, etc.
_str_float_word = r'(?<!\d)(?P<floatnum>\d+(\.\d+)?)\s' +\
    r'(?P<floatunits>(thousand|million))'
_regex_float_word = re.compile(_str_float_word, re.IGNORECASE)

# Create a regex that recognizes either an int with commas, a decimal integer,
# a textual integer, or an enumerated integer. The enum must be followed either
# by ' (confirmed|positive)?\s?case'. For example, these would be accepted:
#
#    sixth case
#    fourth positive case in the county
#
# but not this:
#
#     third highest number of confirmed cases
#
def _make_num_regex(a='int', b='tnum', c='enum'):
    _str_num = r'(?<![-])('                                                 +\
        r'(?P<{0}>'.format(a) +  _str_int + r')|'                           +\
        r'(?P<{0}>'.format(b) + _str_tnum + r')|'                           +\
        r'(?P<{0}>'.format(c) + _str_enum + r'(?![-])(?! (high|large|great|small|tini)est))'  +\
        r')(?!%)(?! %)(?! percent)(?! pct)'
    return _str_num

# def _make_num_regex(a='int', b='tnum', c='enum'):
#     _str_num = r'('                                          +\
#         r'(?P<{0}>'.format(a) + _str_int + r')|'             +\
#         r'(?P<{0}>'.format(b) + _str_tnum + r')|'            +\
#         r'(?P<{0}>'.format(c)                                +\
#         r'(' + _str_enum + r'(?= case)' + r'|'               +\
#                _str_enum + r'(?= (confirmed|positive) case)' +\
#         r'))'                                                +\
#         r')(?!%)(?! %)(?! percent)(?! pct)'
#     return _str_num


# regex to recognize either a range or a single integer
# also recognize 'no' for situations such as "no new cases of covid-19"
# do not capture a text num followed by 'from', as in
# "decreased by one from 17 to 16", in which the desired num is 16, not "one"
_str_num = r'(' + r'(\bfrom\s)?' +\
    _make_num_regex('int_from', 'tnum_from', 'enum_from') +\
    r'\s?to\s?' +\
    _make_num_regex('int_to',   'tnum_to',   'enum_to')   +\
    r'|' + r'\b(?P<no>no)\b' + r'|' +  _str_float_word    +\
    r'|' + _make_num_regex() + r')(?!\sfrom\s)'


# time durations, also relative times such as "a week ago"
_str_duration = r'(' + _str_num + r'|' + r'\ba\b' + r')' +\
    r'[-\s](years?|yrs?\.?|months?|mo\.?|weeks?|wk\.?|' +\
    r'days?|hours?|hrs?\.?|minutes?|min\.?|seconds?|sec\.?)(?![a-z])(\sago\s)?'
_regex_duration = re.compile(_str_duration, re.IGNORECASE)

# clock times

# am or pm indicator
_str_am_pm = r'[ap]\.?m\.?'
# time zone, either standard time or daylight time
_str_tz = r'(ak|ha|e|c|m|p|h)[sd]t\b'
_str_clock = r'(?<!\d)(2[0-3]|1[0-9]|0[0-9])[-:\s][0-5][0-9]\s?' +\
    _str_am_pm + r'\s?' + _str_tz
_regex_clock = re.compile(_str_clock, re.IGNORECASE)


_str_coronavirus = r'(covid([-\s]?19)?|(novel\s)?(corona)?virus|disease)([-\s]related)?\s?'

_str_death = r'(deaths?|fatalit(ies|y))'
_str_hosp  = r'(hospitalizations?)'
_str_death_or_hosp = r'(' + _str_death + r'|' + _str_hosp + r')'

# names of groups of people who might become infected
_str_who = r'\b(babies|baby|boy|captive|child|children|citizen|client|'      +\
    r'convict|customer|detainee|employee|girl|guest|holidaymaker|'           +\
    r'individual|infant|inhabitant|inmate|internee|laborer|man|men|native|'  +\
    r'national|neighbor|newborn|occupant|passenger|patient|patron|people|'   +\
    r'personnel|prisoner|regular|resident|shopper|staff|tourist|traveler|'   +\
    r'victim|visitor|voter|woman|women|worker)s?\s?'
_regex_who = re.compile(_str_who, re.IGNORECASE)

#
# death regexes
#

# <num> <words> <coronavirus> deaths
_str_death0 = _str_num + r'\s?' + _str_words + _str_coronavirus +\
    r'(deaths|(?<!a\s)death)'
_regex_death0 = re.compile(_str_death0, re.IGNORECASE)

# <num> <words> deaths <words> <coronavirus>
_str_death1 = _str_num + r'\s?' + _str_words + r'(deaths|(?<!a\s)death)\s?' +\
    _str_words + _str_coronavirus
_regex_death1 = re.compile(_str_death1, re.IGNORECASE)

# <num> <words> (deaths?|died)
# don't capture "candied", "deaths of", "died of" with this regex
# if regex index is changed from 2, fix special handling below in _regex_match
_str_death2 = _str_num + r'\s?' + r'(?P<words>' + _str_words + r')' +\
    r'((deaths|(?<!a\s)death)|(?<![a-z])(died|dead(?![a-z])))(?! of)'
_regex_death2 = re.compile(_str_death2, re.IGNORECASE)

# <coronavirus> <words> deaths <words> <num>
# prevent a match at the start of a space-separated list of numbers
_str_death3 = _str_coronavirus + _str_words + r'(deaths|(?<!a\s)death)\s?' +\
    _str_words + _str_num + r'(?! \d)'
_regex_death3 = re.compile(_str_death3, re.IGNORECASE)

# <num> <who> (have)? died <words> <coronavirus>
_str_death4 = _str_num + r'\s?' + _str_words + r'\s?'      +\
    r'(' + _str_who + r')?' + r'(have\s)?(?<![a-z])died\s' +\
    _str_words + _str_coronavirus
_regex_death4 = re.compile(_str_death4, re.IGNORECASE)

# deaths|died <connector> <words> <num>
# also prevent a match at the start of a space-separated list of numbers
_str_death5 = r'\b((deaths|(?<!a\s)death)|died)[-\s:]{1,2}' + _str_words +\
    _str_num + r'(?! (of|\d))'
_regex_death5 = re.compile(_str_death5, re.IGNORECASE)

#
# case count regexes
#

# <num> <words> positive for <words> <coronavirus>
_str_case0 = _str_num + r'\s' + r'(?P<words>' + _str_words + r')' +\
    r'(?<!\bnot tested )positive\sfor\s' + _str_words + _str_coronavirus
_regex_case0 = re.compile(_str_case0, re.IGNORECASE)

# <num> <words> tested positive
_str_case1 = _str_num + r'\s' + r'(?P<words>' + _str_words + r')' +\
    r'(?<!\bnot )tested\spositive'
_regex_case1 = re.compile(_str_case1, re.IGNORECASE)

# <num> <words> <coronavirus> cases?
_str_case2 = _str_num + r'\s' + _str_words + _str_coronavirus + r'cases?'
_regex_case2 = re.compile(_str_case2, re.IGNORECASE)

# <num> <words> cases? <words> <coronavirus>
_str_case3 = _str_num + r'\s' + _str_words + r'cases?\s' + _str_words + _str_coronavirus
_regex_case3 = re.compile(_str_case3, re.IGNORECASE)

# <num> <words> with <coronavirus>
#_str_case4 = _str_num + r'\s' + _str_words + r'with\s' + _str_coronavirus
_str_case4 = _str_num + r'\s' + _str_who + r'with\s' + _str_coronavirus
_regex_case4 = re.compile(_str_case4, re.IGNORECASE)

# (total|number of) <words> <coronavirus> cases? <words> <num>
_str_case5 = r'(total|number\sof)\s' + _str_words + _str_coronavirus + r'cases?\s' + _str_words + _str_num
_regex_case5 = re.compile(_str_case5, re.IGNORECASE)

# (total|number of) <words> cases? <words> <num>
_str_case6 = r'(total|number\sof)\s' + _str_words + r'cases?\s' + _str_words + _str_num
_regex_case6 = re.compile(_str_case6, re.IGNORECASE)

# <coronavirus> cases? <words> <num>
_str_case7 = _str_coronavirus + r'cases?\s' + r'(?P<words>' + _str_one_or_more_words + r')' + _str_num
_regex_case7 = re.compile(_str_case7, re.IGNORECASE)

# cases (at|to(\sover)?)\s <num>
_str_case8 = r'(cases|total)\s(at|to(\sover))\s' + _str_num
_regex_case8 = re.compile(_str_case8, re.IGNORECASE)

# <num> <words> cases?
_str_case9 = _str_num + r'\s?' + _str_words + r'cases?'
_regex_case9 = re.compile(_str_case9, re.IGNORECASE)

# confirmed <words> <coronavirus> <words> <num>
_str_case10 = r'\bconfirmed\s' + _str_words + _str_coronavirus + _str_words + _str_num
_regex_case10 = re.compile(_str_case10, re.IGNORECASE)

_CASE_REGEXES = [
    _regex_case0,
    _regex_case1,
    _regex_case2,
    _regex_case3,
    _regex_case4,
    _regex_case5,
    _regex_case6,
    _regex_case7,
    _regex_case8,
    _regex_case9,
    _regex_case10,
]

_DEATH_REGEXES = [
    _regex_death0,
    _regex_death1,
    _regex_death2,
    _regex_death3,
    _regex_death4,
    _regex_death5,
]

# matching data used to build the result object
MatchTuple = namedtuple('MatchTuple', ['start', 'end', 'text', 'value'])


###############################################################################
def _enable_debug():

    global _TRACE
    _TRACE = True


###############################################################################
def _erase(sentence, candidates):
    """
    Erase all candidate matches from the sentence. Only substitute a single
    whitespace for the region, since this is performed on the previously
    cleaned sentence and offsets need to be preserved.
    """

    new_sentence = sentence
    for c in candidates:
        start = c.start
        end = c.end
        s1 = new_sentence[:start]
        s2 = ' '*(end-start)
        s3 = new_sentence[end:]
        new_sentence = s1 + s2 + s3

    if _TRACE:
        print('sentence after erasing candidates: ')
        print(new_sentence)
        print()
        
    return new_sentence
    

###############################################################################
def _erase_segment(sentence, start, end):
    """
    Replace sentence[start:end] with whitespace.
    """
    
    s1 = sentence[:start]
    s2 = ' '*(end - start)
    s3 = sentence[end:]
    return s1 + s2 + s3
    

###############################################################################
def _erase_time_expressions(sentence):
    """
    """

    segments = []
    
    # erase expressions such as 10 minutes, 4 days, etc.
    iterator = _regex_duration.finditer(sentence)
    for match in iterator:
        segments.append( (match.start(), match.end()) )

    # erase clock times
    iterator = _regex_clock.finditer(sentence)
    for match in iterator:
        segments.append ( (match.start(), match.end()) )

    for start,end in segments:
        if _TRACE:
            print('\terasing time expression "{0}"'.format(sentence[start:end]))    
        sentence = _erase_segment(sentence, start, end)

    return sentence


###############################################################################
def _erase_dates(sentence):
    """
    Find date expressions in the sentence and erase them.
    """
    
    json_string = run_date_finder(sentence)
    json_data = json.loads(json_string)

    # unpack JSON result into a list of DateMeasurement namedtuples
    dates = [DateValue(**record) for record in json_data]

    # erase each date expression from the sentence
    for date in dates:
        start = int(date.start)
        end   = int(date.end)

        if _TRACE:
            print('\tfound date expression: "{0}"'.format(date))

        # erase date if not all digits
        if not re.match(r'\A\d+\Z', date.text):
            if _TRACE:
                print('\terasing date "{0}"'.format(date.text))
            sentence = _erase_segment(sentence, start, end)

    # look for constructs such as 6-24 and similar
    _str_month_day = r'(?<!\d)(0?[0-9]|1[0-2])[-/]([0-2][0-9]|3[01])'
    _regex_month_day = re.compile(_str_month_day)

    segments = []
    iterator = _regex_month_day.finditer(sentence)
    for match in iterator:
        segments.append( (match.start(), match.end()))
    for start,end in segments:
        if _TRACE:
            print('\terasing month-day expression "{0}"'.
                  format(sentence[start:end]))
        sentence = _erase_segment(sentence, start, end)
            
    return sentence


###############################################################################
def _split_at_positions(text, pos_list):
    """
    Split a string at the list of positions in the string and return a list
    of chunks.
    """

    chunks = []
    prev_end = 0
    for pos in pos_list:
        chunk = text[prev_end:pos]
        chunks.append(chunk)
        prev_end = pos
    chunks.append(text[prev_end:])
    return chunks


###############################################################################
def _cleanup(sentence):
    """
    Apply some cleanup operations to the sentence and return the
    cleaned sentence.
    """

    # convert to lowercase
    sentence = sentence.lower()

    sentence = _erase_dates(sentence)
    sentence = _erase_time_expressions(sentence)
    
    # replace ' w/ ' with ' with '
    sentence = re.sub(r'\sw/\s', ' with ', sentence)

    # erase certain characters
    sentence = re.sub(r'[\']', '', sentence)
    
    # replace selected chars with whitespace
    sentence = re.sub(r'[&(){}\[\]:~/@;]', ' ', sentence)

    # insert a missing space surrounding Covid-19
    space_pos = []
    iterator = re.finditer(r'[a-z]covid\-?19', sentence, re.IGNORECASE)
    for match in iterator:
        # position where the space is needed
        pos = match.start() + 1
        space_pos.append(pos)
    chunks = _split_at_positions(sentence, space_pos)
    sentence = ' '.join(chunks)
    
    # replace commas with whitespace if not inside a number (such as 32,768)
    comma_pos = []
    iterator = re.finditer(r'\D,\D', sentence, re.IGNORECASE)
    for match in iterator:
        pos = match.start() + 1
        comma_pos.append(pos)
    chunks = _split_at_positions(sentence, comma_pos)
    # strip the comma from the first char of each chunk, if present
    for i in range(len(chunks)):
        if chunks[i].startswith(','):
            chunks[i] = chunks[i][1:]
    sentence = ' '.join(chunks)
        
    # collapse repeated whitespace
    sentence = re.sub(r'\s+', ' ', sentence)

    if _TRACE:
        print('sentence after cleanup: "{0}"'.format(sentence))
    return sentence


###############################################################################
def _to_int(str_int):
    """
    Convert a string to int; the string could contain embedded commas.
    """

    if -1 == _str_int.find(','):
        val = int(str_int)
    else:
        text = re.sub(r',', '', str_int)
        val = int(text)

    return val
    

###############################################################################
def _enum_to_int(_str_enum):
    """
    Convert an enumerated count such as 'third' or 'ninenteenth' to an int.
    """

    val = None
    text = _str_enum.strip()
    if text in _enum_to_int_map:
        val = _enum_to_int_map[text]

    return val
    

###############################################################################
def _tnum_to_int(_str_tnum):
    """
    Convert a textual number to an integer. Returns None if number cannot
    be converted, or the actual integer value.
    """

    if _TRACE:
        print('calling _tnum_to_int...')
        print('\t_str_tnum: "{0}"'.format(_str_tnum))

    # replace dashes with a space and collapse any repeated spaces
    text = re.sub(r'\-', ' ', _str_tnum)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    if _TRACE:
        print('\ttnum after dash replacement: "{0}"'.format(text))
    
    if text in _tnum_to_int_map:
        return _tnum_to_int_map[text]

    val_h = 0
    val_t = 0
    val_o = 0
    
    # extract hundreds, if any
    match = _regex_hundreds.match(text)
    if match:
        tnum = match.group().split()[0].strip()
        if tnum in _tnum_to_int_map:
            val_h += _tnum_to_int_map[tnum]
            text = text[match.end():].strip()
        else:
            # invalid number
            if _TRACE:
                print('invalid textual number: "{0}"'.format(text))
                return None

    if len(text) > 0:

        # strip 'and', if any
        pos = text.find('and')
        if -1 != pos:
            text = text[pos+3:]
            text = text.strip()

        # extract tens
        words = text.split()
        assert len(words) <= 2
        if 2 == len(words):
            if words[0] not in _tnum_to_int_map or words[1] not in _tnum_to_int_map:
                # invalid number
                if _TRACE:
                    print('invalid textual number: "{0}"'.format(text))
                    return None

            val_t = _tnum_to_int_map[words[0]]
            val_o = _tnum_to_int_map[words[1]]
        else:
            if words[0] not in _tnum_to_int_map:
                # invalid number
                if _TRACE:
                    print('invalid textual number: "{0}"'.format(text))
                    return None
            val_o = _tnum_to_int_map[words[0]]                                       

    # for val_t, a textual number such as "forty-four" will return 40 from the
    # map lookup, so no need to multiply by 10
    return 100*val_h + val_t + val_o


###############################################################################
def _remove_inferior_matches(candidates, regex_list, regex_minor):
    """
    If a match from regex_minor overlaps any other regex in the list, remove
    the match from regex_minor in the list of candidates. Returns the updated
    list of candidates.
    """
    
    to_remove = set()
    for i in range(len(candidates)):
        if candidates[i].regex != regex_minor:
            continue
        c1 = candidates[i]        
        for j in range(len(candidates)):
            c2 = candidates[j]
            if j != i and c2.regex in regex_list and c2.regex != regex_minor:
                # check for overlap
                if overlap.has_overlap(c1.start, c1.end, c2.start, c2.end):
                    to_remove.add(i)
                    if _TRACE:
                        print('removing overlapping inferior match "{0}", '.
                              format(c1.match_text))
                    break
                
    if len(to_remove) > 0:
        new_candidates = []
        for i in range(len(candidates)):
            if i not in to_remove:
                new_candidates.append(candidates[i])
        candidates = new_candidates

    return candidates


###############################################################################
def _find_contained_match(regex, match):
    """
    Find another match from the same regex within the original match. This
    situation is possible with a few of the regexes. Smaller spans of matched
    text are preferred for the CovidFinder.
    """

    match_text = match.group().rstrip()
    
    # find the first whitespace char
    start_offset = match_text.find(' ')
    if -1 != start_offset:
        # new text to search is a subset of the original match
        sentence2 = match_text[start_offset:]
        # search it again for a more compact match
        match2 = _regex_death2.search(sentence2)
        if match2:
            if _TRACE:
                print('\tfound contained match: "{0}" in "{1}"'.
                      format(match2.group(), match_text))
            # set start explicitly before overwriting 'match'
            start = match.start() + start_offset + match2.start()    
            return match2, start

    # return originals if no secondary match
    return match, match.start()


###############################################################################
def _regex_match(sentence, regex_list):
    """
    Run a list of regexes against a sentence, produce candidate matches, apply
    regex-dependent special handling where need, and run a candidate resolution
    process to select the winning match(es).
    """
    
    candidates = []
    for i, regex in enumerate(regex_list):
        # finditer finds non-overlapping matches
        iterator = regex.finditer(sentence)
        for match in iterator:
            # strip any trailing whitespace
            # NOTE: this invalidates match.end()!
            match_text = match.group().rstrip()
            start = None
            start_offset = 0

            # special handling for _regex_case0 and _regex_case1
            if _regex_case0 == regex or _regex_case1 == regex:
                words = match.group('words').strip()
                # remove 'tested' or 'test'
                words = re.sub(r'test(ed)?', ' ', words)
                match2 = _regex_who.search(words)
                if not match2 and not words.isspace():
                    # skip this, does not refer to groups of people
                    if _TRACE:
                        print('_regex_case[01] override: "{0}"'.
                              format(match_text))
                    continue
            
            # special handling for _regex_case7
            if _regex_case7 == regex:
                # check 'words' capture for throwaway words
                words = [w.strip() for w in match.group('words').split()]
                last_word = words[-1]
                if last_word in _THROWAWAY_SET:
                    if _TRACE:
                        print('ignoring match "{0}"; final word is throwaway'.
                              format(match_text))
                    continue

            # look for contained matches for _regex_case2 and _regex_death2
            if _regex_case2 == regex:
                match, start = _find_contained_match(_regex_case2, match)
                match_text = match.group().rstrip()
            elif _regex_death2 == regex:
                match, start = _find_contained_match(_regex_death2, match)
                match_text = match.group().rstrip()

            # update the start position of the match and recompute the end    
            if start is None:
                start = match.start()
            end = start + len(match_text)

            # found one more candidate, still need overlap resolution
            candidates.append(overlap.Candidate(start, end, match_text, regex,
                                                other=match))
            if _TRACE:
                print('R[{0:2}]: [{1:3}, {2:3})\tMATCH TEXT: ->{3}<-'.
                      format(i, start, end, match_text))
                print('\tmatch.groupdict entries: ')
                for k,v in match.groupdict().items():
                    print('\t\t{0} => {1}'.format(k,v))
                
    if 0 == len(candidates):
        return []        

    # if _regex_case8 overlaps any others, remove the matches for _regex_case8
    candidates = _remove_inferior_matches(candidates,
                                          _CASE_REGEXES,
                                          _regex_case8)
    
    # if _regex_death5 overlaps any others, remove the match for _regex_death5
    candidates = _remove_inferior_matches(candidates,
                                          _DEATH_REGEXES,
                                          _regex_death5)
        
    # sort the candidates in ASCENDING order of length, which is needed for
    # one-pass overlap resolution later on
    candidates = sorted(candidates, key=lambda x: x.end-x.start)
    
    if _TRACE:
        print('\tCandidate matches: ')
        index = 0
        for c in candidates:
            print('\t[{0:2}]\t[{1},{2}): {3}'.
                  format(index, c.start, c.end, c.match_text, c.regex))
            index += 1
        print()

    # keep the SHORTEST of any overlapping matches, to minimize chances
    # of capturing junk
    pruned_candidates = overlap.remove_overlap(candidates,
                                               _TRACE,
                                               keep_longest=False)

    if _TRACE:
        print('\tcandidate count after overlap removal: {0}'.
              format(len(pruned_candidates)))
        print('\tPruned candidates: ')
        for c in pruned_candidates:
            print('\t\t[{0},{1}): {2}'.format(c.start, c.end, c.match_text))
        print()

    return pruned_candidates


###############################################################################
def _text_to_num(match, key, textval):
    """
    Convert a text capture (in 'text') to a numeric value, or return None.
    """

    val = None
    if 'no' == key:
        val = 0
    if 'int_to' == key or 'int' == key:
        val = _to_int(textval)
    elif 'tnum_to' == key or 'tnum' == key:
        val = _tnum_to_int(textval)
    elif 'enum_to' == key or 'enum' == key:
        val = _enum_to_int(textval)
    elif 'floatnum' == key:
        val = float(textval)
        # get the units
        if 'floatunits' in match.groupdict():
            str_units = match.groupdict()['floatunits']
            if _STR_THOUSAND == str_units:
                val *= 1000.0
            elif _STR_MILLION == str_units:
                val *= 1.0e6

    return val


###############################################################################
def _extract_candidates(candidates):
    """
    Extract match results and return a list of
    (start, end, matching_text, value) tuples.
    """

    tuples = []
    for c in candidates:
        # recover the regex match object from the 'other' field
        match = c.other
        assert match is not None

        text  = match.group().strip()
        start = match.start()
        # recompute the end position, since match.group() could include space at
        # the end of the match
        end   = start + len(text)

        for k,v in match.groupdict().items():
            if v is None:
                continue

            #if _TRACE:
            #    print('{0} => {1}'.format(k,v))
            
            val = _text_to_num(match, k, v)
            if val is not None:
                match_tuple = MatchTuple(start, end, text, val)
                tuples.append(match_tuple)
            else:
                # invalid number
                continue

    if len(tuples) > 1:
        tuples = sorted(tuples, key=lambda x: x.start)
        
    return tuples
            
            
###############################################################################
def run(sentence):
    """
    """

    cleaned_sentence = _cleanup(sentence)

    # find case report counts and erase matches from sentence
    if _TRACE:
        print('case count candidates: ')
    case_candidates = _regex_match(cleaned_sentence, _CASE_REGEXES)
    remaining_sentence = _erase(cleaned_sentence, case_candidates)

    assert len(cleaned_sentence) == len(remaining_sentence)

    # find death report counts and erase matches from sentence
    if _TRACE:
        print('death count candidates: ')
    death_candidates = _regex_match(remaining_sentence, _DEATH_REGEXES)
    remaining_sentence = _erase(remaining_sentence, death_candidates)

    # find hospitalization counts and erase matches from sentence
    if _TRACE:
        print('hosp count candidates: ')
    hosp_candidates = []

    # get result tuples for each, sorted in order of occurrence in sentence
    case_tuples  = _extract_candidates(case_candidates)
    hosp_tuples  = _extract_candidates(hosp_candidates)
    death_tuples = _extract_candidates(death_candidates)

    # find which has the most entries
    case_count  = len(case_tuples)
    hosp_count  = len(hosp_tuples)
    death_count = len(death_tuples)
    count = max(case_count, hosp_count, death_count)
    
    if _TRACE:
        print('  case_count: {0}'.format(case_count))
        print('  hosp_count: {0}'.format(hosp_count))
        print(' death_count: {0}'.format(death_count))
        print('       count: {0}'.format(count))
        print(' case_tuples: {0}'.format(case_tuples))
        print('death_tuples: {0}'.format(death_tuples))
        print(' hosp_tuples: {0}'.format(hosp_tuples))

    # Build result objects, taking results from cases, hosp, and deaths
    # in order.
    results = []
    for i in range(count):

        case_start  = EMPTY_FIELD
        case_end    = EMPTY_FIELD
        hosp_start  = EMPTY_FIELD
        hosp_end    = EMPTY_FIELD
        death_start = EMPTY_FIELD
        death_end   = EMPTY_FIELD
        text_case   = EMPTY_FIELD
        text_hosp   = EMPTY_FIELD
        text_death  = EMPTY_FIELD
        value_case  = EMPTY_FIELD
        value_hosp  = EMPTY_FIELD
        value_death = EMPTY_FIELD

        if i < case_count:
            case_start = case_tuples[i].start
            case_end   = case_tuples[i].end
            text_case  = case_tuples[i].text
            value_case = case_tuples[i].value

        if i < hosp_count:
            hosp_start = hosp_tuples[i].start
            hosp_end   = hosp_tuples[i].end
            text_hosp  = hosp_tuples[i].text
            value_hosp = hosp_tuples[i].value

        if i < death_count:
            death_start = death_tuples[i].start
            death_end   = death_tuples[i].end
            text_death  = death_tuples[i].text
            value_death = death_tuples[i].value
        
        covid_tuple = CovidTuple(
            sentence    = cleaned_sentence,
            case_start  = case_start,
            case_end    = case_end,
            hosp_start  = hosp_start,
            hosp_end    = hosp_end,
            death_start = death_start,
            death_end   = death_end,
            text_case   = text_case,
            text_hosp   = text_hosp,
            text_death  = text_death,
            value_case  = value_case,
            value_hosp  = value_hosp,
            value_death = value_death,
        )
        results.append(covid_tuple)

    # convert to list of dicts to preserve field names in JSON output
    return json.dumps([r._asdict() for r in results], indent=4)
    

###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)

                        
###############################################################################
if __name__ == '__main__':

    # for command-line testing only

    parser = argparse.ArgumentParser(
        description='test covid finder task locally')

    parser.add_argument('--debug',
                        action='store_true',
                        help='print debugging information')

    args = parser.parse_args()

    if 'debug' in args and args.debug:
        _enable_debug()

    SENTENCES = [

        # captures "deaths matter pentecost tongues of fire four"
        'not want not call waiting four questions blake elder rockhill '     \
        'studios the afterwife mosquito appeal which deaths matter '         \
        'pentecost tongues of fire four questions wolf loescher balls to '   \
        'the walls more articles',
        
        #<num> residents dying
        
        # # TBD
        # # 'Two residents at Fairhaven in Sykesville, one resident at '       \
        # # 'Flying Colors of Success in Westminster and two staff members '   \
        # # 'at Pleasant View Nursing Home in Mount Airy who live in Carroll ' \
        # # 'tested positive, pushing the facilities total to 559.',
        
    ]

    for i, sentence in enumerate(SENTENCES):
        print('\n[{0:2d}]: {1}'.format(i, sentence))
        result = run(sentence)
        #print(result)

        data = json.loads(result)
        for d in data:
            for k,v in d.items():
                print('\t\t{0} = {1}'.format(k, v))
            
        
###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)




"""
death reports

<num> deaths

<num>           <coronavirus> deaths
<num> more      <coronavirus> deaths
<num> confirmed <coronavirus> deaths
no additional <coronavirus>-related deaths

<num> more deaths related to <coronavirus>
<num>      deaths due     to <coronavirus>
<num>      deaths from the   <coronavirus>
<num> new  deaths directly caused by or related to <coronavirus>

<num> additional         deaths
no    new                deaths
<num> new                deaths
<num> total              deaths
<num> confirmed resident deaths

2nd    <coronavirus> death
second <coronavirus> death
third  <coronavirus>-related death

<num> residents dying

<num> residents   died as a result of the <coronavirus>
<num> people have died 
<num>        have died after contracting it
<num> inmates     died of the <coronavirus>

total number of <coronavirus>-related deaths stands at <num>
                <coronavirus>-related deaths near      <num>

<coronavirus> death toll hits <num>

              total deaths to <num>
                    deaths-<num>
number of confirmed deaths: <num>


false positives:
    two-thirds of all <coronavirus> deaths




case reports

# <num> <words> <coronavirus> cases?
<num> covid-19 cases
<num> coronavirus cases
<num> new covid-19 cases
<num> confirmed coronavirus cases
<num> new <location> covid-19 cases

# <num> <words> cases? <words> <coronavirus>
<num> cases of covid-19
<num> new cases of covid-19
<num> more cases of covid-19
<num> positive covid-19 cases
<num> active cases of covid-19
<num> confirmed cases of covid-19
<enum> confirmed case of covid-19
<num> additional cases of covid-19
<num> positive case of coronavirus
<num> confirmed cases of the virus
<num> confirmed cases of the coronavirus

# <num> <words> cases?
<num> cases
<num> new cases
<num> total cases
<num> active cases
<num> probable cases
<num> positive cases
<num> positive cases
<num> new daily cases
<num> confirmed cases
<num> new positive cases
<num> lab-confirmed cases
<num> total confirmed cases
<num> confirmed and probable cases

# <num> <words> with <coronavirus>
<num> employees with coronavirus

# <num> <words> positive for <words> <coronavirus>
<num> test positive for covid-19
<num> have tested positive for the virus
<num> <words> tested positive for the coronavirus
<num> residents having tested positive for covid-19
<num> additional staff members are positive for covid-19
<num> people had tested positive for the novel coronavirus

# <num> <words> tested positive
<num> inmates have tested positive

# (total|number of) <words> <coronavirus> cases? <words> <num>
total number of coronavirus cases had reached <num>
total number of covid-19 cases in <location> to <num>
      number of COVID cases recorded in a one day was <num>

# <coronavirus> cases? <words> <num>
coronavirus cases (<num>)
covid-19 cases below <num>
covid-19 cases up to <num>
covid-19 cases <words> <num>
coronavirus cases reach <num>
coronavirus cases rise to <num>
coronavirus case total tops <num>
covid-19 cases in <location> increased to <num>

# (total|number of) <words> cases? <words> <num>
total number of positive cases <words> <num>
total of positive cases has been updated to <num>
total of lab-confirmed cases in <location> is now <num>
total tally of cases in <location> since the pandemic began to <num>

# cases <words> <num>
cases-<num>
cases at <num>
cases balloon to over <num>

# total <words> <num>
total of <num>
brings our total to <num>

number of confirmed cases from <num1> to <num2>
<num1>-<num2> positive cases in <location>
<num1> staff members and <num2> residents have now tested positive
<num1> words and <num2> words cases of covid-19
<num1> new cases in <location1> and <num2> in <location2>
"""
