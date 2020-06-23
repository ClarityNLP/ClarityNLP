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

if __name__ == '__main__':
    # for interactive testing only
    match = re.search(r'nlp/', sys.path[0])
    if match:
        nlp_dir = sys.path[0][:match.end()]
        sys.path.append(nlp_dir)
    else:
        print('\n*** covid_finder.py: nlp dir not found ***\n')
        sys.exit(0)

try:
    import finder_overlap as overlap
except:
    from algorithms.finder import finder_overlap as overlap

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
_VERSION_MINOR = 1
_MODULE_NAME   = 'covid_finder.py'

# set to True to enable debug output
_TRACE = False

# connectors between portions of the regexes below; either symbols or words
#_str_cond = r'(?P<cond>(~=|>=|<=|[-/:<>=~\s.@^]+|\s[a-z\s]+)+)?'

# words, possibly hyphenated or abbreviated, nongreedy match
_str_words = r'([-a-z\s.]+?)?'


_str_units = r'\(?(percent|pct\.?|%|mmHg)\)?'


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
    r')'

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
    'zero':0
}

# integers, possibly including commas
_str_int = r'(?<!covid)(?<!covid-)(?<!\d)(\d{3}(,\d{3})+|\d+)'

# general integer number, both decimals and text
def _make_num_regex(a,b):
    _str_num = r'((?P<{0}>'.format(a) + _str_int + r')|(?P<{0}>'.format(b) + _str_tnum + r'))'
    return _str_num

_str_qual = r'(total|(lab(oratory)?[-\s])?confirmed|probable|suspected|' \
    r'more|(brand[-\s]?)?new)\s?'

# covid case statements
_str_covid0 = r'(covid([-\s]?19)?|coronavirus)\s?'
_str_covid1 = _str_covid0 + _str_words + r'cases?\s?'
_str_covid2 = r'cases?\sof\s' + _str_covid0
_str_covid3 = r'cases?'
_str_covid = r'(' + _str_covid1 + r'|' + _str_covid2 + r'|' +\
    _str_covid0 + r'|' + _str_covid3 + r')'

#
# regexes to find case reports
#

# find '97 confirmed cases', 16 new cases,  and similar
_str_case0 = _make_num_regex('int', 'tnum') + r'\s?' + _str_qual + _str_covid #r'\scases?\b'
_regex_case0 = re.compile(_str_case0, re.IGNORECASE)

# find 'the number of confirmed COVID-19 cases increased to 12' and similar
_str_case1 = _str_qual + _str_words + _str_covid + _str_words +\
    _make_num_regex('int', 'tnum')
_regex_case1 = re.compile(_str_case1, re.IGNORECASE)

# find 'cumulative total of 137 cases of COVID-19' and similar
_str_case2 = _str_qual + _str_words + _make_num_regex('int', 'tnum') +\
    _str_words + _str_covid
_regex_case2 = re.compile(_str_case2, re.IGNORECASE)

# find 'two employees test positive for COVID-19' similar
_str_case3 = _make_num_regex('int', 'tnum') + r'\s?' + _str_words +\
    r'positive\sfor\s' + _str_covid
_regex_case3 = re.compile(_str_case3, re.IGNORECASE)

# find '30 coronavirus cases' and similar
_str_case4 = _make_num_regex('int', 'tnum') + r'\s?' + _str_covid
_regex_case4 = re.compile(_str_case4, re.IGNORECASE)

# find 'number of confirmed cases from 10 to 8' and similar
_str_case5 = r'\bfrom\s' + _str_words + _make_num_regex('int_from', 'tnum_from') +\
    r'\s?to\s?' + _make_num_regex('int', 'tnum')
_regex_case5 = re.compile(_str_case5, re.IGNORECASE)

_CASE_REGEXES = [
    _regex_case0,
    _regex_case1,
    _regex_case2,
    _regex_case3,
    _regex_case4,
    _regex_case5,
]



###############################################################################
def _enable_debug():

    global _TRACE
    _TRACE = True
    

###############################################################################
def _cleanup(sentence):
    """
    Apply some cleanup operations to the sentence and return the
    cleaned sentence.
    """

    # convert to lowercase
    sentence = sentence.lower()
    
    # replace ' w/ ' with ' with '
    sentence = re.sub(r'\sw/\s', ' with ', sentence)
    
    # replace selected chars with whitespace
    sentence = re.sub(r'[,&(){}\[\]:~/@]', ' ', sentence)

    # collapse repeated whitespace
    sentence = re.sub(r'\s+', ' ', sentence)

    print('sentence after cleanup: "{0}"'.format(sentence))
    return sentence


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
                print('[{0:2}]: [{1:3}, {2:3})\tMATCH TEXT: ->{3}<-'.
                      format(i, start, end, match_text))
                print('\tmatch.groupdict entries: ')
                for k,v in match.groupdict().items():
                    print('\t\t{0} => {1}'.format(k,v))
                

    if 0 == len(candidates):
        return []        
    
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

    # if two overlap exactly, keep candidate with longer device string
    prev_start = candidates[0].start
    prev_end = candidates[0].end
    delete_index = None
    for i in range(1, len(candidates)):
        c = candidates[i]
        if c.start == prev_start and c.end == prev_end:
            if _TRACE:
                print('\tCandidates at indices {0} and {1} have ' \
                      'identical overlap'.format(i-1, i))
            # the regex match object is stored in the 'other' field
            matchobj = c.other
            matchobj_prev = candidates[i-1].other
            if 'device' in matchobj.groupdict() and 'device' in matchobj_prev.groupdict():
                device = matchobj.group('device')
                device_prev = matchobj_prev.group('device')
                if device is not None and device_prev is not None:
                    len_device = len(device)
                    len_device_prev = len(device_prev)
                    if _TRACE:
                        print('\t\tdevice string for index {0}: {1}'.
                              format(i-1, device_prev))
                        print('\t\tdevice string for index {0}: {1}'.
                              format(i, device))
                    if len_device > len_device_prev:
                        delete_index = i-1
                    else:
                        delete_index = i
                    if _TRACE:
                        print('\t\t\tdelete_index: {0}'.format(delete_index))
                    break
        prev_start = c.start
        prev_end = c.end

    if delete_index is not None:
        del candidates[delete_index]
        if _TRACE:
            print('\tRemoved candidate at index {0} with shorter device string'.
                  format(delete_index))

    # remove any that are proper substrings of another, exploiting the fact
    # that the candidate list is sorted in decreasing order of length
    discard_set = set()
    for i in range(1, len(candidates)):
        start = candidates[i].start
        end   = candidates[i].end
        for j in range(0, i):
            prev_start = candidates[j].start
            prev_end   = candidates[j].end
            if start >= prev_start and end <= prev_end:
                discard_set.add(i)
                if _TRACE:
                    print('\t[{0:2}] is a substring of [{1}], discarding...'.
                          format(i, j))
                break

    survivors = []
    for i in range(len(candidates)):
        if i not in discard_set:
            survivors.append(candidates[i])

    candidates = survivors
        

    # Now find the maximum number of non-overlapping candidates. This is an
    # instance of the equal-weight interval scheduling problem, which has an
    # optimal greedy solution. See the book "Algorithm Design" by Kleinberg and
    # Tardos, ch. 4.
    
    # sort candidates in increasing order of their END points
    candidates = sorted(candidates, key=lambda x: x.end)
    
    pruned_candidates = [candidates[0]]
    prev_end = pruned_candidates[0].end
    for i in range(1, len(candidates)):
        c = candidates[i]
        if c.start >= prev_end:
            pruned_candidates.append(c)
            prev_end = c.end
#    else:
#        # run the usual overlap resolution
#        pruned_candidates = overlap.remove_overlap(candidates, _TRACE)

    if _TRACE:
        print('\tcandidate count after overlap removal: {0}'.
              format(len(pruned_candidates)))
        print('\tPruned candidates: ')
        for c in pruned_candidates:
            print('\t\t[{0},{1}): {2}'.format(c.start, c.end, c.match_text))
        print()

    return pruned_candidates
    

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
            if 'int' == k:
                value_case_list.append(int(v))
            elif 'tnum' == k:
                val = _tnum_to_int(v)
                if val is not None:
                    value_case_list.append(int(val))
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
    #results = sorted(results, key=lambda x: x.start)

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

        'The Wyoming Department of Health reports that 674lab-confirmed ' \
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

        'decreasing the number of confirmed cases from 19 to 18.',

        'now has two confirmed COVID-19 cases Facebook Staff WriterLocal ',
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
