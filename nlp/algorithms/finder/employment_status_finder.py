#!/usr/bin/env python3
"""

Module for finding a patient's employment status.

"""

import os
import re
import sys
import json
from collections import namedtuple

if __name__ == '__main__':
    # interactive testing
    match = re.search(r'nlp/', sys.path[0])
    if match:
        nlp_dir = sys.path[0][:match.end()]
        sys.path.append(nlp_dir)
    else:
        path, module_name = os.path.split(__file__)
        print('\n*** {0}: nlp dir not found ***\n'.format(module_name))
        sys.exit(0)
    
try:
    # interactive path
    import finder_overlap as overlap
    DISPLAY = print
except:
    # ClarityNLP path
    from claritynlp_logging import log, ERROR, DEBUG
    DISPLAY = log
    from algorithms.finder import finder_overlap as overlap


EMPLOYMENT_STATUS_EMPLOYED   = 'Employed'   # either full or part-time
EMPLOYMENT_STATUS_UNEMPLOYED = 'Unemployed'
EMPLOYMENT_STATUS_RETIRED    = 'Retired'
EMPLOYMENT_STATUS_DISABLED   = 'Disabled'
# don't need an unknown - just leave blank

EMPLOYMENT_TUPLE_FIELDS = [
    'sentence',
    'employment_status', # one of the constants above
]

EmploymentTuple = namedtuple('EmploymentTuple', EMPLOYMENT_TUPLE_FIELDS)
EmploymentTuple.__new__.__defaults__ = (None,) * len(EmploymentTuple._fields)


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 1

# set to True to enable debug output
_TRACE = False

# a word, possibly hyphenated or abbreviated
_str_word = r'[-a-z]+\.?\s?'

# nongreedy word capture
_str_words = r'\s?(' + _str_word + r'){0,5}?'

# greedy word capture
_str_one_or_more_words = r'\s?(' + _str_word + r'){1,7}'

_str_header = r'\bemployment status:\s?'

_str_employment_statement = _str_header + r'(?P<words>' + _str_one_or_more_words + r')'
_regex_employment_statement = re.compile(_str_employment_statement, re.IGNORECASE)

_str_unemployed1 = r'\b(?P<unemployed>(unemployed|not? (employed|work(ing)?)|deferred|laid off))\b'
_regex_unemployed1 = re.compile(_str_unemployed1, re.IGNORECASE)

_str_job = r'\b(employment|work(ing)?|job)\b'
_str_unemployed2 = r'\b(?P<unemployed>(look|search|seek|find)(ing)?\b' + _str_words + _str_job + r')'
_regex_unemployed2 = re.compile(_str_unemployed2, re.IGNORECASE)

_str_unemployed3 = r'\b(?P<unemployed>(terminat(ed?|ing)|laid off)\b' + _str_words + _str_job + r')'
_regex_unemployed3 = re.compile(_str_unemployed3, re.IGNORECASE)

_str_unemployed4 = r'\b(?P<unemployed>not?\b' + _str_words + _str_job + r')'
_regex_unemployed4 = re.compile(_str_unemployed4, re.IGNORECASE)

_str_disabled = r'\b(?P<disabled>disab(ility|led?))\b'
_regex_disabled = re.compile(_str_disabled, re.IGNORECASE)

_str_retired = r'\b(?P<retired>retire(d|e))\b'
_regex_retired = re.compile(_str_retired, re.IGNORECASE)

# explicit statement of employment
# prevents captures of "employment of", since that often refer to devices
_str_employed1 = r'\b(?P<employed>(((self|place of) )?employ(ed|ment)(?! of)|work(ing|s)?|career))\b'
_regex_employed1 = re.compile(_str_employed1, re.IGNORECASE)

_str_ignore = r'\b(unk(nown)?|student)\b'
_regex_ignore = re.compile(_str_ignore, re.IGNORECASE)

# need explicit check for unknown

_REGEXES = [
    _regex_unemployed1,
    _regex_unemployed2,
    _regex_unemployed3,
    _regex_unemployed4,
    _regex_disabled,
    _regex_retired,
    _regex_employed1,
]


_CHAR_SPACE = ' '


###############################################################################
def _cleanup(sentence):
    """
    Apply some cleanup operations to the sentence and return the
    cleaned sentence.
    """

    # convert to lowercase
    sentence = sentence.lower()

    # replace MIMIC [** ... **] anonymizations with whitespace
    sentence = re.sub(r'\[\*\*[^\]]+\]', _CHAR_SPACE, sentence)    

    # replace ' w/ ' with ' with '
    sentence = re.sub(r'\sw/\s', ' with ', sentence)

    # replace ' @ ' with ' at '
    sentence = re.sub(r'\s@\s', ' at ', sentence)

    # replace "->" with whitespace
    sentence = re.sub(r'\->', _CHAR_SPACE, sentence)

    # erase commas and apostrophes
    sentence = re.sub(r'[,\'`]', '', sentence)

    # replace ellipsis with whitespace
    sentence = re.sub(r'\.\.\.', _CHAR_SPACE, sentence)

    # replace other chars with whitespace
    sentence = re.sub(r'[-&(){}\[\]~/;]', _CHAR_SPACE, sentence)

    # replace "long term disability" and "short term disability" with "disability"
    sentence = re.sub(r'\b(long|short) term disability', 'disability', sentence)
    
    # collapse repeated whitespace
    sentence = re.sub(r'\s+', _CHAR_SPACE, sentence)

    return sentence


###############################################################################
def _regex_match(sentence, regex_list):
    """
    """

    candidates = []
    for i, regex in enumerate(regex_list):
        # expect only a single match
        iterator = regex.finditer(sentence)
        for match in iterator:
            # strip any trailing whitespace (invalidates match.end())
            match_text = match.group().rstrip()
            start = match.start()
            end = start + len(match_text)

            if _TRACE:
                DISPLAY('\t' + match_text)

            # get group name to determine employment status
            status = None
            if 'unemployed' in match.groupdict() and match.group('unemployed') is not None:
                status = EMPLOYMENT_STATUS_UNEMPLOYED
            elif 'disabled' in match.groupdict() and match.group('disabled') is not None:
                status = EMPLOYMENT_STATUS_DISABLED
            elif 'retired' in match.groupdict() and match.group('retired') is not None:
                status = EMPLOYMENT_STATUS_RETIRED
            elif 'employed' in match.groupdict() and match.group('employed') is not None:
                status = EMPLOYMENT_STATUS_EMPLOYED

            # append the new match if no other candidates of the same type
            ok_to_append = True
            for c in candidates:
                if c.other == status:
                    ok_to_append = False
                    break

            if ok_to_append:
                candidates.append(overlap.Candidate(
                    start, end, match_text, regex, other=status
                ))

    # sort candidates in DECREASING order of length
    candidates = sorted(candidates, key=lambda x: x.end-x.start)

    if _TRACE:
        DISPLAY('\tCandidate matches: ')
        index = 0
        for c in candidates:
            regex_index = regex_list.index(c.regex)
            DISPLAY('\t[{0:2}] R{1:2}\t[{2},{3}): ->{4}<-'.
                  format(index, regex_index, c.start, c.end, c.match_text))
            index += 1
        DISPLAY()

    # keep the longest of any overlapping matches
    pruned_candidates = overlap.remove_overlap(candidates,
                                               False,
                                               keep_longest=True)

    if _TRACE:
        DISPLAY('\tCandidate matches after overlap resolution: ')
        index = 0
        for c in pruned_candidates:
            regex_index = regex_list.index(c.regex)
            DISPLAY('\t[{0:2}] R{1:2}\t[{2},{3}): ->{4}<-'.
                  format(index, regex_index, c.start, c.end, c.match_text))
            index += 1
        DISPLAY()
    
    return pruned_candidates
    


###############################################################################
def run(sentence):

    results = []
    cleaned_sentence = _cleanup(sentence)

    if _TRACE:
        DISPLAY(cleaned_sentence)

    # try the employment statement regex first
    candidates = []
    match_text = None
    match = _regex_employment_statement.search(cleaned_sentence)
    if match:
        # matched "Employment Status: <words>"
        match_text = match.group().strip()
        start = match.start()
        end = start + len(match_text)

        # get the 'words' group text
        words = match.group('words').strip()

        # strip out subsequent Mimic headers, if any
        words = re.sub(r'(legal involvement|mandated reporting information):', '', words)
        words = re.sub(r'\s+', _CHAR_SPACE, words)

        if words.isspace():
            candidates = []
        else:
            match2 = _regex_ignore.search(words)
            if match2:
                candidates = []
            else:
                candidates = _regex_match(words, _REGEXES)

                if 0 == len(candidates):
                    # the default is to assume employed if words appear after "Employment Status: "
                    # and these other checks have failed
                    candidates.append(overlap.Candidate(
                        start, end, match_text, None, other=EMPLOYMENT_STATUS_EMPLOYED
                    ))
                    
    else:
        candidates = _regex_match(cleaned_sentence, _REGEXES)

    for c in candidates:
        employment_status = c.other

        obj = EmploymentTuple(
            sentence = cleaned_sentence,
            employment_status = employment_status
        )

        results.append(obj)

    return json.dumps([r._asdict() for r in results], indent=4)
        

###############################################################################
def get_version():
    path, module_name = os.path.split(__file__)
    return '{0} {1}.{2}'.format(module_name, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':
    

    SENTENCES = [

        # unemployed
        'FOB is currently unemployed and looking for a job.',
        'She reports that pt is unemployed and \"disabled\" from cardiac problems.',
        'she recently lost her job and pt has been unemployed for several months',
        "currently living with the pt's uncle as pt and wife are unemployed and have no income",
        'He is presently unemployed',
        'The patient lives with parents and is currently unemployed',
        'Pt is unemployed X one year, husband recently lost job',
        'Mo is a bilingual unemployed homemaker w/ 2 older children',
        'continuing her search for employment',
        'Mum has terminated employment and is greatly relieved to not have to juggle work and visiting',
        'pt is trying hard to find a job',
        'she is not currently working',
        'pt was laid off from his job last week',

        # unemployed
        'Employment status: Unemployed',
        'Employment status: Not working',
        'Employment status: Unemployed--Pt has had numerous jobs',
        'Employment status: Unemployed--Pt was just laid off from his work',
        'Employment status: Deferred',        
        'Employment status: Seeking employment--just finished post doc',
        'Employment status: Pt reports she has been unemployed since the onset   of health problems',
        'Employment status: no job',
        'Employment status: laid off two months ago',

        # disabled
        'Employment status: Disable',
        'Employment status: Disabled',
        'Employment status: Disability',
        'Employment status: Disable/dog walker',
        'Employment status: Good Year Tire - long term disability',
        'Employment status: Pt on disability due to illness; previously worked in demolition',        
        
        # retured
        'Employment status: Retired',
        'Employment status: five year retiree',

        # employed
        'Employment status: Employed',
        'Employment status: Employed at the time of admission',
        'Employment status: self employed',
        "Employment status: works 25 hr's per week",
        'Employment status: Employed as civil naval engineer',
        'Employment status: works as administrative assistant at 2 jobs',
        'Employment status: full time work at funeral home',
        'Pt knows birth date, his current address and place of employment',
        'Employment status: Employed...works as nursing instructor',
        'Employment status: Employed as freelance text book editor, works from   home',
        'Employment status: Pt works as a sous chef and has worked in restaurants for over 20 years',
        'Employment status: Career Military, currently at Hanssom AFB',
        
        # part-time employment
        'Employment status: part time employment',        
        'Employment status: intermittent employment as power washer',

        'Employment status: On medical leave',
        'Employment status: Post Office',
        
        
        # negative
        'Employment of aerosol mask with FIO2 of 35%',
        'Subsequent images demonstrate successful employment of a Wallstent across the stricture',
        'Employment status: student',        
        'Employment status: Unknown',
    ]

    for sentence in SENTENCES:
        DISPLAY('\n' + sentence)
        json_result = run(sentence)
        json_data = json.loads(json_result)
        result_list = [EmploymentTuple(**d) for d in json_data]
        for r in result_list:
            DISPLAY('\t{0}'.format(r))
