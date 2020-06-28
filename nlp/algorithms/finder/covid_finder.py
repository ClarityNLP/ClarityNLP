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
#     from algorithms.finder.time_finder import run as \
#         run_time_finder, TimeValue, EMPTY_FIELD as EMPTY_DATE_FIELD
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
#     from time_finder import run as run_time_finder, \
#         TimeValue, EMPTY_FIELD as EMPTY_TIME_FIELD
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
#from time_finder import run as run_time_finder, \
#    TimeValue, EMPTY_FIELD as EMPTY_TIME_FIELD
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

_STR_THOUSAND = 'thousand'
_STR_MILLION  = 'million'


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 1
_MODULE_NAME   = 'covid_finder.py'

# set to True to enable debug output
_TRACE = False

# connectors between portions of the regexes below; either symbols or words
#_str_cond = r'(?P<cond>(~=|>=|<=|[-/:<>=~\s.@^]+|\s[a-z\s]+)+)?'

_str_word = r'[-a-z]+\.?\s?'
_str_words = r'(' + _str_word + r'){0,5}?'

_str_one_or_more_words = r'(' + _str_word + r'){1,5}?'

# words, possibly hyphenated or abbreviated, nongreedy match
#_str_words = r'([-a-z\s.]+?)?'


# textual numbers and related regexes
_str_tnum_digit = r'(one|two|three|four|five|six|seven|eight|nine|zero)'
_str_tnum_10s = r'(ten|eleven|twelve|(thir|four|fif|six|seven|eight|nine)teen)'
_str_tnum_20s  = r'(twenty[-\s]?' + _str_tnum_digit + r'|twenty)'
_str_tnum_30s  = r'(thirty[-\s]?' + _str_tnum_digit + r'|thirty)'
_str_tnum_40s  = r'(forty[-\s]?' + _str_tnum_digit + r'|forty)'
_str_tnum_50s  = r'(fifty[-\s]?' + _str_tnum_digit + r'|fifty)'
_str_tnum_60s  = r'(sixty[-\s]?' + _str_tnum_digit + r'|sixty)'
_str_tnum_70s  = r'(seventy[-\s]?' + _str_tnum_digit + r'|seventy)'
_str_tnum_80s  = r'(eighty[-\s]?' + _str_tnum_digit + r'|eighty)'
_str_tnum_90s  = r'(ninety[-\s]?' + _str_tnum_digit + r'|ninety)'
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
_str_int = r'(?<!covid)(?<!covid-)(?<!\d)(\d{1,3}(,\d{3})+|\d+)'

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
    _str_num = r'('                                          +\
        r'(?P<{0}>'.format(a) + _str_int + r')|'             +\
        r'(?P<{0}>'.format(b) + _str_tnum + r')|'            +\
        r'(?P<{0}>'.format(c)                                +\
        r'(' + _str_enum + r'(?= case)' + r'|'               +\
               _str_enum + r'(?= (confirmed|positive) case)' +\
        r'))'                                                +\
        r')(?!%)(?! %)(?! percent)(?! pct)'
    return _str_num

# regex to recognize either a range or a single integer
_str_num = r'(' + r'(\bfrom\s)?' +\
    _make_num_regex('int_from', 'tnum_from', 'enum_from') +\
    r'\s?to\s?' +\
    _make_num_regex('int_to',   'tnum_to',   'enum_to')   +\
    r'|' + _str_float_word + r'|' + _make_num_regex() + r')'

_str_qual = r'(total|(lab(oratory)?[-\s])?confirmed|probable|suspected|' \
    r'active|more|(brand[-\s]?)?new)\s?'

# time durations
_str_duration = r'(?<!\d)\d+\s(year|yr\.?|month|mo\.?|week|wk\.?|day|' +\
    r'hour|hr\.?|minute|min\.?|second|sec\.?)s?'
_regex_duration = re.compile(_str_duration, re.IGNORECASE)

# covid case statements
# _str_covid0 = r'(covid([-\s]?19)?|(corona)?virus)\s?'
# _str_covid1 = _str_covid0 + _str_words + r'cases?\s?'
# _str_covid2 = r'cases?\sof\s' + _str_covid0
# _str_covid3 = r'cases?'
# _str_covid = r'(' + _str_covid1 + r'|' + _str_covid2 + r'|' +\
#     _str_covid0 + r'|' + _str_covid3 + r')'

_str_coronavirus = r'(covid([-\s]?19)?|(novel\s)?(corona)?virus)\s?'

_str_death = r'(deaths?|fatalit(ies|y))'
_str_hosp  = r'(hospitalizations?)'
_str_death_or_hosp = r'(' + _str_death + r'|' + _str_hosp + r')'

#
# regexes to find case reports
#

"""

# 1. <num> <words> <coronavirus> cases?
<num> covid-19 cases
<num> coronavirus cases
<num> new covid-19 cases
<num> confirmed coronavirus cases
<num> new <location> covid-19 cases

# 2. <num> <words> cases? <words> <coronavirus>
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

# 3. <num> <words> cases?
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

# 4. <num> <words> with <coronavirus>
<num> employees with coronavirus

# 5. <num> <words> positive for <words> <coronavirus>
<num> test positive for covid-19
<num> have tested positive for the virus
<num> <words> tested positive for the coronavirus
<num> residents having tested positive for covid-19
<num> additional staff members are positive for covid-19
<num> people had tested positive for the novel coronavirus

# 6. <num> <words> tested positive
<num> inmates have tested positive

# 7. (total|number of) <words> <coronavirus> cases? <words> <num>
total number of coronavirus cases had reached <num>
total number of covid-19 cases in <location> to <num>
      number of COVID cases recorded in a one day was <num>

# 8. <coronavirus> cases? <words> <num>
coronavirus cases (<num>)
covid-19 cases below <num>
covid-19 cases up to <num>
covid-19 cases <words> <num>
coronavirus cases reach <num>
coronavirus cases rise to <num>
coronavirus case total tops <num>
covid-19 cases in <location> increased to <num>

# 9. (total|number of) <words> cases? <words> <num>
total number of positive cases <words> <num>
total of positive cases has been updated to <num>
total of lab-confirmed cases in <location> is now <num>
total tally of cases in <location> since the pandemic began to <num>

# 10. cases <words> <num>
cases-<num>
cases at <num>
cases balloon to over <num>

# 11. total <words> <num>
total of <num>
brings our total to <num>

number of confirmed cases from <num1> to <num2>
<num1>-<num2> positive cases in <location>
<num1> staff members and <num2> residents have now tested positive
<num1> words and <num2> words cases of covid-19
<num1> new cases in <location1> and <num2> in <location2>
"""

# # find '97 confirmed cases', 16 new cases,  and similar
# _str_case0 = _str_num + r'\s?' + _str_qual + _str_words + _str_covid
# _regex_case0 = re.compile(_str_case0, re.IGNORECASE)

# # find 'the number of confirmed COVID-19 cases increased to 12' and similar
# # make sure the number is not followed by 'death' or 'hospitalization'
# # and related words
# #_str_case1 = _str_words + _str_covid + _str_words + _make_num_regex() +\
# #    r'(?!\d)(?!\s?{0})'.format(_str_death_or_hosp)
# _str_case1 = _str_words + _str_covid + _str_words + _str_num +\
#     r'(?!\d)(?!\s?{0})'.format(_str_death_or_hosp)
# _regex_case1 = re.compile(_str_case1, re.IGNORECASE)

# # find 'cumulative total of 137 cases of COVID-19' and similar
# _str_case2 = _str_words + _str_num + _str_words + _str_covid
# _regex_case2 = re.compile(_str_case2, re.IGNORECASE)

# # find 'two employees test positive for COVID-19' similar
# _str_case3 = _str_num + r'\s?' + _str_words + r'positive\sfor\s' + _str_covid
# _regex_case3 = re.compile(_str_case3, re.IGNORECASE)

# # find '30 coronavirus cases' and similar
# _str_case4 = _str_num + r'\s?' + _str_covid
# _regex_case4 = re.compile(_str_case4, re.IGNORECASE)

# <num> <words> positive for <words> <coronavirus>
_str_case0 = _str_num + r'\s' + _str_words + r'positive\sfor\s' + _str_words + _str_coronavirus
_regex_case0 = re.compile(_str_case0, re.IGNORECASE)

# <num> <words> tested positive
_str_case1 = _str_num + r'\s' + _str_words + r'tested\spositive'
_regex_case1 = re.compile(_str_case1, re.IGNORECASE)

# <num> <words> <coronavirus> cases?
_str_case2 = _str_num + r'\s' + _str_words + _str_coronavirus + r'cases?'
_regex_case2 = re.compile(_str_case2, re.IGNORECASE)

# <num> <words> cases? <words> <coronavirus>
_str_case3 = _str_num + r'\s' + _str_words + r'cases?\s' + _str_words + _str_coronavirus
_regex_case3 = re.compile(_str_case3, re.IGNORECASE)

# <num> <words> with <coronavirus>
_str_case4 = _str_num + r'\s' + _str_words + r'with\s' + _str_coronavirus
_regex_case4 = re.compile(_str_case4, re.IGNORECASE)

# (total|number of) <words> <coronavirus> cases? <words> <num>
_str_case5 = r'(total|number\sof)\s' + _str_words + _str_coronavirus + r'cases?\s' + _str_words + _str_num
_regex_case5 = re.compile(_str_case5, re.IGNORECASE)

# (total|number of) <words> cases? <words> <num>
_str_case6 = r'(total|number\sof)\s' + _str_words + r'cases?\s' + _str_words + _str_num
_regex_case6 = re.compile(_str_case6, re.IGNORECASE)

# <coronavirus> cases? <words> <num>
_str_case7 = _str_coronavirus + r'cases?\s' + _str_one_or_more_words + _str_num
_regex_case7 = re.compile(_str_case7, re.IGNORECASE)

# cases (at|to(\sover)?)\s <num>
_str_case8 = r'(cases|total)\s(at|to(\sover))\s' + _str_num
_regex_case8 = re.compile(_str_case8, re.IGNORECASE)

# <num> <words> cases?
_str_case9 = _str_num + r'\s' + _str_words + r'cases?'
_regex_case9 = re.compile(_str_case9, re.IGNORECASE)

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
]



###############################################################################
def _enable_debug():

    global _TRACE
    _TRACE = True


###############################################################################
def _erase(sentence, candidates):
    """
    Erase all candidate matches from the sentence. Only substitute a single
    whitespace for the region, since this is performed on the previously
    cleaned sentence.
    """

    new_sentence = sentence
    for c in candidates:
        start = c.start
        end = c.end
        s1 = new_sentence[:start]
        s2 = ' '
        s3 = new_sentence[end:]
        new_sentence = s1 + s2 + s3

    # collapse repeated whitespace, if any
    new_sentence = re.sub(r'\s+', ' ', new_sentence)
        
    return new_sentence
    

###############################################################################
def _erase_durations(sentence):
    """
    Erase expressions such as 10 minutes, 4 days, etc.
    """

    segments = []
    iterator = _regex_duration.finditer(sentence)
    for match in iterator:
        segments.append( (match.start(), match.end()) )

    for start,end in segments:
        if _TRACE:
            print('\terasing duration "{0}"'.format(sentence[start:end]))
            s1 = sentence[:start]
            s2 = ' '*(end - start)
            s3 = sentence[end:]
            sentence = s1 + s2 + s3

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
            s1 = sentence[:start]
            s2 = ' '*(end - start)
            s3 = sentence[end:]
            sentence = s1 + s2 + s3

    return sentence

            
###############################################################################
def _cleanup(sentence):
    """
    Apply some cleanup operations to the sentence and return the
    cleaned sentence.
    """

    # convert to lowercase
    sentence = sentence.lower()

    sentence = _erase_dates(sentence)
    sentence = _erase_durations(sentence)
    
    # replace ' w/ ' with ' with '
    sentence = re.sub(r'\sw/\s', ' with ', sentence)

    # erase certain characters
    sentence = re.sub(r'[\']', '', sentence)
    
    # replace selected chars with whitespace
    sentence = re.sub(r'[&(){}\[\]:~/@;]', ' ', sentence)

    # replace commas with whitespace if not inside a number (such as 32,768)
    comma_pos = []
    iterator = re.finditer(r'\D,\D', sentence, re.IGNORECASE)
    for match in iterator:
        pos = match.start() + 1
        comma_pos.append(pos)
    for pos in comma_pos:
        sentence = sentence[:pos] + ' ' + sentence[pos+1:]    
        
    # collapse repeated whitespace
    sentence = re.sub(r'\s+', ' ', sentence)

    #print('sentence after cleanup: "{0}"'.format(sentence))
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
def _regex_match(sentence, regex_list):
    """
    """
    
    candidates = []
    for i, regex in enumerate(regex_list):
        iterator = regex.finditer(sentence)
        for match in iterator:
            match_text = match.group().strip()

            start = match.start()
            end   = start + len(match_text)
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

    # find 
        
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
def run(sentence):
    """
    """

    cleaned_sentence = _cleanup(sentence)

    if _TRACE:
        print('case count candidates: ')
    case_candidates = _regex_match(cleaned_sentence, _CASE_REGEXES)

    # erase these matches from the sentence
    remaining_sentence = _erase(cleaned_sentence, case_candidates)
    

    results = []
    case_results = []
    hosp_results = []
    death_results = []

    case_start_list  = []
    case_end_list    = []
    hosp_start_list  = []
    hosp_end_list    = []
    death_start_list = []
    death_end_list   = []
    text_case_list   = []
    text_hosp_list   = []
    text_death_list  = []
    value_case_list  = []
    value_hosp_list  = []
    value_death_list = []
    
    for c in case_candidates:
        # recover the regex match object from the 'other' field
        match = c.other
        assert match is not None

        case_start_list.append(match.start())
        case_end_list.append(match.end())
        text_case_list.append(match.group())

        for k,v in match.groupdict().items():
            if v is None:
                continue

            #if _TRACE:
            #    print('{0} => {1}'.format(k,v))
            
            # convert number text captures
            val = None
            if 'int_to' == k or 'int' == k:
                val = _to_int(v)
            elif 'tnum_to' == k or 'tnum' == k:
                val = _tnum_to_int(v)
            elif 'enum_to' == k or 'enum' == k:
                val = _enum_to_int(v)
            elif 'floatnum' == k:
                val = float(v)
                # get the units
                if 'floatunits' in match.groupdict():
                    str_units = match.groupdict()['floatunits']
                    if _STR_THOUSAND == str_units:
                        val *= 1000.0
                    elif _STR_MILLION == str_units:
                        val *= 1.0e6
                
            if val is not None:
                value_case_list.append(val)
            else:
                # invalid number
                continue

    case_count  = len(value_case_list)
    hosp_count  = len(value_hosp_list)
    death_count = len(value_death_list)
    count = max(case_count, hosp_count, death_count)

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
            case_start = case_start_list.pop(0)
            case_end   = case_end_list.pop(0)
            text_case  = text_case_list.pop(0)
            value_case = value_case_list.pop(0)

        if i < hosp_count:
            hosp_start = hosp_start_list.pop(0)
            hosp_end   = hosp_end_list.pop(0)
            text_hosp  = text_hosp_list.pop(0)
            value_hosp = value_hosp_list.pop(0)

        if i < death_count:
            death_start = death_start_list.pop(0)
            death_end   = death_end_list.pop(0)
            text_death  = text_death_list.pop(0)
            value_death = value_death_list.pop(0)
        
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

    # sort results to match order of occurrence in sentence
    results = sorted(results, key=lambda x: x.case_start)

    # hospitalizations
    # deaths

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
        '16 New Cases COVID-19 Claims Three More Lives in Atlantic County',
        
        'Currently, there are 97 confirmed cases in North Carolina.',

        'The Newton Co Health Dept reports 2 more cases of COVID-19 for ' \
        'our county-this brings our total to 9.',
        
        'As of Tuesday morning, the number of confirmed COVID-19 cases in ' \
        'Mercer County increased to 12.',
        
        'Williamson Countys confirmed cases of COVID-19 spiked by 17, 27 ' \
        'and 18 from May 12 through May 14. As of May 16, the county has ' \
        'had 463 confirmed cases in the coronavirus pandemic.',

        'The Wyoming Department of Health reports that 674lab-confirmed '   \
        'cases have recovered and 196 probable cases have recoveredacross ' \
        'the state.',

        'The new cases bring the health district up to a cumulative total ' \
        'of 137 cases of COVID-19, including 111 in Cache and 26 in Elder.',

        'has had   one hundred forty seven test positive for COVID-19, the ' \
        'manager said',

        'saw the biggest three-day increase of positive cases yet with 16 ' \
        'new cases reported over the weekend and 12 on Monday.',

        'officials confirm 692 coronavirus cases as hospitalizations ' \
        'continue to decline',

        'now has two confirmed COVID-19 cases Facebook Staff WriterLocal ',

        'The announcement, of this sixth case in Floyd County comes '      \
        'alongside reports from Gov. Andy Beshear on April 21 that there ' \
        'are 3,192 positive cases in the state, as well as 171 deaths '    \
        'from the virus.',

        'Contra Costa also reported that its total number of coronavirus ' \
        'cases had reached 1,336 by the end of Sunday, with 15 new cases ' \
        'from the day before.',

        'Some Are Turned Away Health Governor Says Coronavirus Cases Rise ' \
        'to 77, Blood Donors Needed',

        'The North Dakota Department of Health confirmed Friday 40 ' \
        'additional cases of COVID-19 out of 2,894 total tests completed',

        'Seventeen new COVID-19 cases in North Dakota were confirmed '    \
        'Wednesday, May 27. As of Wednesday morning, the state is at 56 ' \
        'deaths, 621 active cases (including eight in Richland County, '  \
        'North Dakota), 1,762 recoveries and 2,439 total cases to date.',

        'Wednesdays totals include 21 new cases in Cass County; five new ' \
        'cases in Stutsman County; two new cases in Burleigh and Ransom '  \
        'counties and one new case each in Grand Forks, Walsh and Ward '   \
        'counties.',

        'Coronavirus cases are surging past 5 million worldwide, with '    \
        'most of the new cases coming from just four countries: Russia, '  \
        'Brazil, India, and the United States.',

        'decreasing the number of confirmed cases from 19 to 18.',

        'Macon County reported just three positive cases of COVID-19 '     \
        'for 12 weeks.',

        'Carroll County surpasses 1,000 coronavirus cases - Carroll '      \
        'County Times Carroll County surpassed 1,000 cases of COVID-19 '   \
        'on Wednesday, according to the health department.',
        
        # do NOT capture anything here
        'In fact, the Bear River Health District has the third highest '   \
        'amount of total cases in the state.',

        # new errors

        # returns 9
        'nearly 300 new covid-19 cases 9 more deaths',

        # returns 9
        'on sunday the indiana state department of health announced '      \
        '397 new covid-19 cases and 9 additional deaths.',

        # returns 10
        'as the number of cases of the coronavirus are flattening '        \
        'locally greene county offices will reopen on monday to a '        \
        'regular volume of traffic.',

        # returns 2 only, misses 48
        'greene county now has two active cases with 48 reported since '   \
        'the pandemic began',

        # returns 0
        'according tothe center for systems science and engineering at '   \
        'johns hopkins university there have been more than 6,200,00 '     \
        'confirmed cases worldwide with more than 2,660,000 recoveries '   \
        'and more than 372,000 deaths. 2020',

        # misses 1,373
        'officials announced 16 new covid-19 cases on sunday bringing '    \
        'the countywide total to 1,373.',

        # returns 6
        'after 6 days of no new covid-19 cases in st. louis county '       \
        'public health director says its too soon to make conclusions '    \
        'numbers as of thursday .',

        # # captures 'coronavirus cases 9' (fixed)
        # 'indiana reports 292 new coronavirus cases 9 additional deaths '   \
        # 'indiana health officials nearly 300 new coronavirus cases '       \
        # 'monday along with 9 additional deaths related to the virus.',

        # # captures 29 (fixed)
        # 'while african-americans make up 14 percent of the states '        \
        # 'population they represented 29 percent of coronavirus cases.'
        
        # TBD
        # 'Two residents at Fairhaven in Sykesville, one resident at '       \
        # 'Flying Colors of Success in Westminster and two staff members '   \
        # 'at Pleasant View Nursing Home in Mount Airy who live in Carroll ' \
        # 'tested positive, pushing the facilities total to 559.',        
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
