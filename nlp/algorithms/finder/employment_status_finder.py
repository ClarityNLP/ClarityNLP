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


EMPLOYMENT_STATUS_EMPLOYED   = 'Employed',   # either full or part-time
EMPLOYMENT_STATUS_UNEMPLOYED = 'Unemployed',
EMPLOYMENT_STATUS_RETIRED    = 'Retired',
EMPLOYMENT_STATUS_DISABLED   = 'Disabled'
# don't need an unknown - just leave blank

EMPLOYMENT_TUPLE_FIELDS = [
    'sentence',
    'employment_status', # one of the constants above
]

EmploymentTuple = namedtuple('EmploymentTuple', EMPLOYMENT_TUPLE_FIELDS)

# set default value of all fields to None
EmploymentTuple.__new__.__defaults__ = (None,) * len(EmploymentTuple._fields)


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 1

# set to True to enable debug output
_TRACE = True

# a word, possibly hyphenated or abbreviated
_str_word = r'[-a-z]+\.?\s?'

# nongreedy word captures
_str_words = r'\s?(' + _str_word + r'){0,5}?'


_str_header = r'\bemployment status:'

_str_status_header = _str_header + r'\s?(?P<words>' + _str_words + r')'
_regex_status_header = re.compile(_str_status_header, re.IGNORECASE)

_str_disabled = r'\bdisab(ility|led?)\b'
_regex_disabled = re.compile(_str_disabled, re.IGNORECASE)

_REGEXES = [
    _regex_status_header,
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
        iterator = regex.finditer(sentence)
        for match in iterator:
            # strip any trailing whitespace (invalidates match.end())
            match_text = match.group().rstrip()
            start = match.start()
            end = start + len(match_text)

            if _TRACE:
                print('\t' + match_text)
            
            #candidates.append(overlap.Candidate(
            #    start, end, match_text, regex, other=religion_text
            #))


###############################################################################
def run(sentence):

    results = []
    cleaned_sentence = _cleanup(sentence)

    if _TRACE:
        DISPLAY(cleaned_sentence)

    candidates = _regex_match(cleaned_sentence, _REGEXES)


###############################################################################
def get_version():
    path, module_name = os.path.split(__file__)
    return '{0} {1}.{2}'.format(module_name, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':
    

    SENTENCES = [

        'FOB is currently unemployed and looking for a job.',
        'She reports that pt is unemployed and \"disabled\" from cardiac problems.',
        'she recently lost her job and pt has been unemployed for several months',
        "currently living with the pt's uncle as pt and wife are unemployed and have no income",
        'He is presently unemployed',
        'The patient lives with parents and is currently unemployed',
        'Pt is unemployed X one year, husband recently lost job',
        'Mo is a bilingual unemployed homemaker w/ 2 older children',
        'continuing her search for employment',

        'Employment status: Unemployed',
        'Employment status: Not working',
        'Employment status: Unemployed--Pt has had numerous jobs',
        'Employment status: Unemployed--Pt was just laid off from his work',
        
        'Employment status: part time employment',
        "Employment status: works 25 hr's per week",
        'Employment status: Disable',
        'Employment status: Disabled',
        'Employment status: Disability',
        'Employment status: Disable/dog walker',
        'Employment status: Deferred',
        'Employment status: Retired',
        'Employment status: Employed',
        'Employment status: Employed at the time of admission',
        'Employment status: student',
        'Employment status: self employed',
        'Employment status: Good Year Tire - long term disability',
        'Employment status: On medical leave',
        'Employment status: Pt on disability due to illness; previously worked in demolition',
        'Employment status: Post Office',
        'Employment status: Unknown',
        'Employment status: intermittent employment as power washer',
        'Employment status: Employed as civil naval engineer',
        'Employment status: Seeking employment--just finished post doc',
        'Employment status: works as administrative assistant at 2 jobs',
        'Employment status: Career Military, currently at Hanssom AFB',
        'Employment status: full time work at funeral home',
        'Employment status: Employed...works as nursing instructor',
        'Employment status: Employed as freelance text book editor, works from   home',
        'Employment status: Pt reports she has been unemployed since the onset   of health problems',
        'Employment status: Pt works as a sous chef and has worked in restaurants for over 20 years',

        'Pt knows birth date, his current address and place of employment',
        'Mum has terminated employment and is greatly relieved to not have to juggle work and visiting',
        
        # negative
        'Employment of aerosol mask with FIO2 of 35%',
        'Subsequent images demonstrate successful employment of a Wallstent across the stricture',
    ]

    for sentence in SENTENCES:
        DISPLAY('\n' + sentence)
        run(sentence)
