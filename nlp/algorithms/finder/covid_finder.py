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
_str_cond = r'(?P<cond>(~=|>=|<=|[-/:<>=~\s.@^]+|\s[a-z\s]+)+)?'

# words, possibly hyphenated or abbreviated, nongreedy match
_str_words = r'([-a-z\s./:~]+?)?'

# # wordy relationships
# _str_equal     = r'\b(equal|eq\.?)'
# _str_approx    = r'(~=|~|\b(approx\.?|approximately|near(ly)?|about))'
# _str_less_than = r'\b(less\s+than|lt\.?|up\s+to|under|below)'
# _str_gt_than   = r'\b(greater\s+than|gt\.?|exceed(ing|s)|above|over)'

# _str_lt  = r'(<|' + _str_less_than + r')'
# _str_lte = r'(<=|</=|' + _str_less_than + r'\s+or\s+' + _str_equal + r')'
# _str_gt  = r'(>|' + _str_gt_than + r')'
# _str_gte = r'(>=|>/=|' + _str_gt_than + r'\s+or\s+' + _str_equal + r')'

# _regex_lt     = re.compile(_str_lt,     re.IGNORECASE)
# _regex_lte    = re.compile(_str_lte,    re.IGNORECASE)
# _regex_gt     = re.compile(_str_gt,     re.IGNORECASE)
# _regex_gte    = re.compile(_str_gte,    re.IGNORECASE)
# _regex_approx = re.compile(_str_approx, re.IGNORECASE)


_str_units = r'\(?(percent|pct\.?|%|mmHg)\)?'


# integers, possibly including commas
_str_int = r'(?P<int>(\d{3}(,\d{3})+|\d+))'

_str_qual = r'((lab(oratory)?[-\s])?confirmed|probable|suspected)\s?'

# covid cases
_str_covid = r'covid(\-?19)?' + _str_words + r'cases?\s?'

# find '97 confirmed cases' and similar
_str_case0 = _str_int + r'\s?' + _str_qual + r'\scases?\b'
_regex_case0 = re.compile(_str_case0, re.IGNORECASE)

# find 'the number of confirmed COVID-19 cases increased to 12' and similar
_str_case1 = _str_qual + _str_words + _str_covid + _str_words + _str_int
_regex_case1 = re.compile(_str_case1, re.IGNORECASE)


_CASE_REGEXES = [
    _regex_case0,
    _regex_case1,
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

    # replace ' w/ ' with ' with '
    sentence = re.sub(r'\sw/\s', ' with ', sentence)
    
    # replace selected chars with whitespace
    sentence = re.sub(r'[,&(){}\[\]]', ' ', sentence)

    # collapse repeated whitespace
    sentence = re.sub(r'\s+', ' ', sentence)

    return sentence


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
    
    # # only a single match for pao2, fio2, p_to_f_ratio

    # if _TRACE:
    #     print('PaO2 candidates: ')
    # pao2 = EMPTY_FIELD
    # pao2_candidates = _regex_match(remaining_sentence, [_regex_pao2])
    # if len(pao2_candidates) > 0:
    #     # take the first match
    #     match_obj = pao2_candidates[0].other
    #     pao2, pao2_2 = _extract_values(match_obj)

    # # erase these matches also
    # remaining_sentence = _erase(remaining_sentence, pao2_candidates)

    # if _TRACE:
    #     print('FiO2 candidates: ')
    # fio2 = EMPTY_FIELD
    # fio2_candidates = _regex_match(remaining_sentence, _FIO2_REGEXES)
    # if len(fio2_candidates) > 0:
    #     # take the first match
    #     match_obj = fio2_candidates[0].other
    #     fio2, fio2_2 = _extract_values(match_obj)
    #     # convert fio2 to a percentage
    #     if fio2 < 1.0:
    #         fio2 *= 100.0

    # # erase these matches
    # remaining_sentence = _erase(remaining_sentence, fio2_candidates)
            
    # if _TRACE:
    #     print('PaO2/FiO2 candidates: ')
    # p_to_f_ratio = EMPTY_FIELD
    # pf_candidates = _regex_match(cleaned_sentence, [_regex_pf_ratio])
    # if len(pf_candidates) > 0:
    #     # take the first match
    #     match_obj = pf_candidates[0].other
    #     p_to_f_ratio, p_to_f_ratio_2 = _extract_values(match_obj)

    # if _TRACE:
    #     print('Extracting data from pruned candidates...')

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
        'Currently, there are 97 confirmed cases in North Carolina.',
        
        'As of Tuesday morning, the number of confirmed COVID-19 cases in ' \
        'Mercer County increased to 12.',
        
        'Williamson Countys confirmed cases of COVID-19 spiked by 17, 27 ' \
        'and 18 from May 12 through May 14. As of May 16, the county has ' \
        'had 463 confirmed cases in the coronavirus pandemic.',

        'The Wyoming Department of Health reports that 674lab-confirmed ' \
        'cases have recovered and 196 probable cases have recoveredacross ' \
        'the state.',
        
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
